from app.services.adverse_media import best_relevance, relevance


def test_name_and_financial_crime_context_scores_candidate():
    score = relevance("Thabo Nkosi", "Thabo Nkosi charged in a fraud investigation")
    assert score >= 0.85


def test_crime_article_without_identity_match_is_not_a_candidate():
    assert relevance("Thabo Nkosi", "Another person was arrested for corruption") == 0


def test_name_only_is_candidate_not_confirmation():
    score = relevance("Thabo Nkosi", "Thabo Nkosi appointed to a new role")
    assert 0 < score < 0.9


def test_verified_alias_participates_in_relevance_scoring():
    score, matched = best_relevance(
        ["Acceptance Customer", "Albanian Mafia"],
        "Court sentences members in an Albanian mafia fraud investigation",
    )
    assert score >= 0.85
    assert matched == "Albanian Mafia"
