import { useEffect, useState } from "react";

import keycloak from "../services/keycloak";

type RecordRow = Record<string, unknown>;
type ModuleResponse = { rows?: RecordRow[] };
type ApiError = { detail?: unknown };

const labels: Record<string, string> = {
    aml: "AML rule events",
    kyc: "KYC and CDD evidence",
    media: "Adverse media evidence",
    screening: "PEP and sanctions matches",
    network: "Linked devices",
    rules: "AML rule catalogue",
    risk: "Risk evaluations",
    geography: "Geographic exposure",
    reports: "Report evidence",
};

async function authHeaders(): Promise<Record<string, string>> {
    await keycloak.updateToken(30);
    if (!keycloak.token) {
        throw new Error("Sign in to load AML/KYC evidence.");
    }
    return { Authorization: `Bearer ${keycloak.token}` };
}

async function errorMessage(response: Response, fallback: string) {
    const body = (await response.json().catch(() => null)) as ApiError | null;
    return typeof body?.detail === "string"
        ? body.detail
        : `${fallback} (HTTP ${response.status})`;
}

export default function IntelligencePanel({ kind }: { kind: string }) {
    const [rows, setRows] = useState<RecordRow[]>([]);
    const [error, setError] = useState("");
    const [actionBusy, setActionBusy] = useState(false);
    const [customerId, setCustomerId] = useState("");
    const [assessment, setAssessment] = useState<unknown>(null);
    const [report, setReport] = useState("");
    const [refresh, setRefresh] = useState(0);
    const [loadedRequest, setLoadedRequest] = useState("");

    const api = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(
        /\/$/,
        "",
    );
    const requestKey = `${api}:${kind}:${refresh}`;
    const loading = loadedRequest !== requestKey;
    const busy = loading || actionBusy;

    useEffect(() => {
        let cancelled = false;

        async function loadEvidence() {
            try {
                const headers = await authHeaders();
                const response = await fetch(
                    `${api}/api/v1/intelligence/${encodeURIComponent(kind)}?limit=100&offset=0`,
                    { headers },
                );
                if (!response.ok) {
                    throw new Error(
                        await errorMessage(response, "Data unavailable"),
                    );
                }
                const data = (await response.json()) as ModuleResponse;
                if (!cancelled) {
                    setRows(data.rows ?? []);
                    setError("");
                }
            } catch (loadError) {
                if (!cancelled) {
                    setError(
                        loadError instanceof Error
                            ? loadError.message
                            : "Data unavailable",
                    );
                }
            } finally {
                if (!cancelled) {
                    setLoadedRequest(requestKey);
                }
            }
        }

        void loadEvidence();
        return () => {
            cancelled = true;
        };
    }, [api, kind, refresh, requestKey]);

    async function runAssessment(generateReport: boolean) {
        setActionBusy(true);
        setError("");
        try {
            const path = generateReport
                ? "reports/generate"
                : `customers/${encodeURIComponent(customerId.trim())}/evaluate`;
            const headers = await authHeaders();
            const response = await fetch(
                `${api}/api/v1/intelligence-engine/${path}`,
                {
                    method: generateReport ? "POST" : "GET",
                    headers: {
                        ...headers,
                        ...(generateReport
                            ? { "Content-Type": "application/json" }
                            : {}),
                    },
                    ...(generateReport
                        ? {
                              body: JSON.stringify({
                                  customer_id: customerId.trim(),
                              }),
                          }
                        : {}),
                },
            );
            if (!response.ok) {
                throw new Error(
                    await errorMessage(response, "Request failed"),
                );
            }
            const data = (await response.json()) as {
                report?: string;
            };
            if (generateReport) {
                setReport(data.report ?? "");
            } else {
                setAssessment(data);
            }
        } catch (requestError) {
            setError(
                requestError instanceof Error
                    ? requestError.message
                    : "Request failed",
            );
        } finally {
            setActionBusy(false);
        }
    }

    return (
        <section className="mt-5 space-y-3 rounded-xl border border-slate-200 bg-white p-4 text-slate-800">
            <div className="flex items-center justify-between">
                <h2 className="font-semibold">{labels[kind] ?? kind}</h2>
                <button
                    type="button"
                    onClick={() => {
                        setError("");
                        setRefresh((value) => value + 1);
                    }}
                    disabled={busy}
                    className="rounded-lg border px-3 py-1.5 text-xs disabled:opacity-50"
                >
                    Refresh evidence
                </button>
            </div>

            {(kind === "risk" || kind === "aml" || kind === "reports") && (
                <div className="space-y-2 rounded-lg bg-slate-50 p-3">
                    <label
                        className="block text-xs font-medium"
                        htmlFor={`customer-${kind}`}
                    >
                        Customer UUID for on-demand assessment
                    </label>
                    <input
                        id={`customer-${kind}`}
                        value={customerId}
                        onChange={(event) => setCustomerId(event.target.value)}
                        placeholder="Existing customer UUID"
                        className="w-full rounded-md border bg-white p-2 text-sm"
                    />
                    <div className="flex flex-wrap gap-2">
                        <button
                            type="button"
                            disabled={!customerId.trim() || busy}
                            onClick={() => void runAssessment(false)}
                            className="rounded-md bg-violet-600 px-3 py-2 text-xs text-white disabled:opacity-50"
                        >
                            Evaluate AML rules
                        </button>
                        {kind === "reports" && (
                            <button
                                type="button"
                                disabled={!customerId.trim() || busy}
                                onClick={() => void runAssessment(true)}
                                className="rounded-md bg-slate-800 px-3 py-2 text-xs text-white disabled:opacity-50"
                            >
                                Generate AI report
                            </button>
                        )}
                    </div>
                    <p className="text-xs text-slate-500">
                        On-demand evaluation is read-only; AI reports require a
                        configured model.
                    </p>
                    {assessment !== null && (
                        <pre className="max-h-72 overflow-auto whitespace-pre-wrap text-xs">
                            {JSON.stringify(assessment, null, 2)}
                        </pre>
                    )}
                    {report && (
                        <p className="whitespace-pre-wrap text-sm">{report}</p>
                    )}
                </div>
            )}

            {error && (
                <p role="alert" className="text-sm text-red-600">
                    {error}
                </p>
            )}
            {busy && <p className="text-xs text-slate-500">Loading...</p>}

            <div className="overflow-x-auto">
                {rows.length > 0 ? (
                    <table className="w-full text-left text-xs">
                        <thead>
                            <tr>
                                {Object.keys(rows[0]).map((key) => (
                                    <th key={key} className="border-b p-2">
                                        {key.replaceAll("_", " ")}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((row, rowIndex) => (
                                <tr key={String(row.id ?? rowIndex)}>
                                    {Object.entries(row).map(([key, value]) => (
                                        <td
                                            key={key}
                                            className="border-b p-2"
                                        >
                                            {value === null
                                                ? "Unavailable"
                                                : typeof value === "object"
                                                  ? JSON.stringify(value)
                                                  : String(value)}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    !busy &&
                    !error && (
                        <p className="text-sm text-slate-500">
                            No evidence records available.
                        </p>
                    )
                )}
            </div>
        </section>
    );
}
