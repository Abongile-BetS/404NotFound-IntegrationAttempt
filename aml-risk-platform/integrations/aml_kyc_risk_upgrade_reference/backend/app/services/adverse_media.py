from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin
import ssl
import feedparser
import httpx
import truststore
from bs4 import BeautifulSoup

CRIME_TERMS = ("fraud", "corruption", "money laundering", "arrest", "charged", "court", "theft", "sanction", "financial crime", "investigation")


@dataclass
class Candidate:
    title: str
    publication: str
    url: str
    excerpt: str
    published_at: datetime | None = None
    category: str = "potential_adverse_media"
    relevance: float = 0.0
    matched_name: str = ""


def relevance(name: str, text: str) -> float:
    haystack = text.casefold()
    full = name.strip().casefold()
    parts = [p for p in full.split() if len(p) > 2]
    if full and full in haystack:
        base = 0.75
    elif parts and all(p in haystack for p in parts):
        base = 0.62
    elif parts and parts[-1] in haystack:
        base = 0.35
    else:
        return 0.0
    if any(term in haystack for term in CRIME_TERMS):
        base += 0.15
    return min(base, 0.95)


def best_relevance(names: list[str], text: str) -> tuple[float, str]:
    """Return the strongest identity-term match, including supplied aliases."""
    scored = [(relevance(name, text), name) for name in names if name.strip()]
    return max(scored, default=(0.0, ""), key=lambda item: item[0])


def _html_source(client: httpx.Client, source: str, url: str, names: list[str]) -> list[Candidate]:
    response = client.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for link in soup.select("a[href]"):
        title = " ".join(link.get_text(" ", strip=True).split())
        if len(title) < 12:
            continue
        score, matched_name = best_relevance(names, title)
        if score:
            results.append(Candidate(title=title, publication=source, url=urljoin(url, link.get("href")), excerpt=title, relevance=score, matched_name=matched_name))
    return results[:25]


def _rss_source(client: httpx.Client, source: str, url: str, names: list[str]) -> list[Candidate]:
    response = client.get(url)
    response.raise_for_status()
    feed = feedparser.parse(response.content)
    if getattr(feed, "bozo", False) and not feed.entries:
        raise ValueError(f"Invalid RSS response from {source}")
    results = []
    for entry in feed.entries[:100]:
        title = entry.get("title", "").strip()
        excerpt = BeautifulSoup(entry.get("summary", ""), "html.parser").get_text(" ", strip=True)
        score, matched_name = best_relevance(names, f"{title} {excerpt}")
        if not score:
            continue
        published = None
        parsed = entry.get("published_parsed")
        if parsed:
            published = datetime(*parsed[:6], tzinfo=timezone.utc)
        publication = entry.get("source", {}).get("title") or source
        results.append(Candidate(title=title, publication=publication, url=entry.get("link", ""), excerpt=excerpt[:700], published_at=published, relevance=score, matched_name=matched_name))
    return results


def search_public_sources(name: str, scope: str = "combined", aliases: list[str] | None = None) -> tuple[list[Candidate], dict]:
    aliases = [a.strip() for a in aliases or [] if a.strip()]
    names = [name.strip(), *aliases]
    terms = ' OR '.join(f'"{n}"' for n in names)
    crime = ' OR '.join(f'"{term}"' for term in CRIME_TERMS[:7])
    sources: list[tuple[str, str, str]] = []
    if scope in {"south_africa", "combined"}:
        sources += [
            ("NPA", "html", "https://www.npa.gov.za/media-releases"),
            ("SAPS", "html", "https://www.saps.gov.za/newsroom/news_search.php"),
            ("SIU", "html", "https://www.siu.org.za/media-statements/"),
            ("South African public news", "rss", f"https://news.google.com/rss/search?q={quote_plus(f'({terms}) ({crime}) (site:news24.com OR site:iol.co.za OR site:timeslive.co.za OR site:dailymaverick.co.za OR site:citizen.co.za OR site:bizcommunity.com)')}&hl=en-ZA&gl=ZA&ceid=ZA:en"),
        ]
    if scope in {"international", "combined"}:
        sources += [
            ("International public news", "rss", f"https://news.google.com/rss/search?q={quote_plus(f'({terms}) ({crime}) (site:reuters.com OR site:apnews.com OR site:bbc.com)')}&hl=en&gl=US&ceid=US:en"),
            ("BBC World", "rss", "https://feeds.bbci.co.uk/news/world/rss.xml"),
        ]
    coverage, candidates, seen = {}, [], set()
    headers = {"User-Agent": "AML-Nexus-Enterprise/0.1 compliance-screening contact=local-development"}
    tls_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    with httpx.Client(headers=headers, timeout=httpx.Timeout(12.0), follow_redirects=True, verify=tls_context) as client:
        for source, kind, url in sources:
            started = datetime.now(timezone.utc)
            try:
                found = _rss_source(client, source, url, names) if kind == "rss" else _html_source(client, source, url, names)
                unique = []
                for item in found:
                    key = item.url.split("?")[0].rstrip("/")
                    if key and key not in seen:
                        seen.add(key); unique.append(item); candidates.append(item)
                coverage[source] = {"status": "success", "url": url, "retrieved_at": started.isoformat(), "candidates": len(unique)}
            except Exception as exc:
                coverage[source] = {"status": "failed", "url": url, "retrieved_at": started.isoformat(), "error": str(exc)[:300], "candidates": 0}
    return candidates, coverage

