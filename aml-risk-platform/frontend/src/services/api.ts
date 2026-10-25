import keycloak from "./keycloak";

const API_URL = `${(import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/$/, "")}/api/v1`;

export type DashboardKpi = {
    label: string;
    value: string;
    change: string;
    positive: boolean;
    tone: string;
    points: number[];
};

export type DashboardActivity = {
    id: string;
    name: string;
    status: string;
    date: string;
    time: string;
};

export type DashboardQueueItem = {
    customer: string;
    name: string;
    verification: string;
    priority: string;
    waiting: string;
    tone: string;
};

export type DashboardTrendPoint = {
    day: string;
    verified: number;
    pending: number;
    action: number;
    started: number;
};

export type DashboardResponse = {
    kpis: DashboardKpi[];
    activity: DashboardActivity[];
    verification_queue: DashboardQueueItem[];
    trend: DashboardTrendPoint[];
    document_types: Array<{ name: string; value: string }>;
};

export type ScreeningResult = {
    id: string;
    customer: string;
    customerId: string;
    source: string | null;
    status: string | null;
    score: string | null;
    time: string | null;
};

export type ScreeningDashboardResponse = {
    kpis: Array<{ label: string; value: string; change: string; positive: boolean; tone: string }>;
    trend: Array<{ day: string; screened: number; matches: number }>;
    breakdown: Array<{ name: string; value: number }>;
    sources: Array<{ name: string; matches: number; percentage: number }>;
    results: ScreeningResult[];
    queue: Array<{ title: string; detail: string; priority: string; tone: string }>;
};

export type WorkspaceColumn = { key: string; label: string };
export type WorkspaceRow = Record<string, string | number>;
export type WorkspaceField = { label: string; value: string; detail?: string; tone?: string };
export type WorkspaceGraphNode = { id: string; name: string; label: string; x: number; y: number; type: string };
export type WorkspaceViewData = {
    tabs?: string[];
    filters?: string[];
    search?: Record<string, string>;
    active_case?: Record<string, string>;
    customer?: Record<string, string>;
    last_screened?: string;
    media?: Array<Record<string, string>>;
    risk?: { score: string; level: string; disclaimer: string; formula: string; factors: Array<{ label: string; value: number; detail: string }> };
    profile?: WorkspaceField[];
    history?: Array<{ timestamp: string; score: string; change: string }>;
    transaction?: { title: string; status: string; fields: WorkspaceField[]; warning: string };
    evidence?: Record<string, string>;
    selected_customer?: Record<string, string>;
    request?: Record<string, string>;
    renewal_bars?: Array<{ label: string; value: string; width: number }>;
    graph?: { title: string; cluster: string; seed: string; legend: string; note: string; nodes: WorkspaceGraphNode[]; edges: Array<{ from: string; to: string }> };
    selected_entity?: Record<string, string>;
    workload?: Array<{ name: string; count: string; detail: string }>;
    selected_alert?: { id: string; priority: string; status: string; customer: string; description: string; detected: string; owner_sla: string; case: string; factors: Array<{ name: string; score: string }>; disclaimer: string };
    case_id?: string;
    alert_id?: string;
    snapshot?: string;
    activity?: WorkspaceField[];
    notes?: Array<{ author: string; timestamp: string; label: string; body: string }>;
    note_placeholder?: string;
    evidence_summary?: string;
    model_notice?: string;
    distribution?: Array<{ label: string; count: string; width: number; tone: string }>;
    distribution_title?: string;
    distribution_note?: string;
    rules?: Array<{ name: string; resolved: string; false_positives: string; rate: string; action: string }>;
    report?: Record<string, string>;
};
export type WorkspaceResponse = {
    title: string;
    subtitle: string;
    updated_at: string;
    last_sync: string;
    model_version: string;
    demo: boolean;
    organization: { name: string; description: string };
    analyst: { name: string; role: string; initials: string };
    alert_count: string;
    kpis: Array<{ label: string; value: string; detail: string; tone: string }>;
    trend_title: string;
    trend: Array<Record<string, string | number>>;
    series: Array<{ key: string; label: string; color: string }>;
    table_title: string;
    columns: WorkspaceColumn[];
    rows: WorkspaceRow[];
    side_title: string;
    side_metrics: Array<{ label: string; value: string; detail: string; tone: string }>;
    view: WorkspaceViewData;
};

export async function apiGet<T>(path: string): Promise<T> {
    const response = await fetch(`${API_URL}${path}`);

    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }

    return response.json() as Promise<T>;
}

export function getDashboardData() {
    return apiGet<DashboardResponse>("/dashboard");
}

export function getScreeningResults() {
    return apiGet<ScreeningResult[]>("/screening");
}

export function getScreeningDashboard() {
    return apiGet<ScreeningDashboardResponse>("/screening/dashboard");
}

export function getCustomers() {
    return apiGet<Array<Record<string, unknown>>>("/customers");
}

export function getAlerts() {
    return apiGet<Array<Record<string, unknown>>>("/alerts");
}

export function getInvestigations() {
    return apiGet<Array<Record<string, unknown>>>("/investigations");
}

export function getTransactions() {
    return apiGet<Array<Record<string, unknown>>>("/transactions");
}

export function getDashboardWorkspace() {
    return apiGet<WorkspaceResponse>("/reporting/dashboard");
}

export function getScreeningWorkspace() {
    return apiGet<WorkspaceResponse>("/screening/workspace");
}

export function getTransactionMonitoringWorkspace() {
    return apiGet<WorkspaceResponse>("/transactions/dashboard");
}

export function getKycWorkspace() {
    return apiGet<WorkspaceResponse>("/kyc/dashboard");
}

export function getNetworkIntelligenceWorkspace() {
    return apiGet<WorkspaceResponse>("/network/dashboard");
}

export function getAlertWorkspace() {
    return apiGet<WorkspaceResponse>("/alerts/dashboard");
}

export function getInvestigationWorkspace() {
    return apiGet<WorkspaceResponse>("/investigations/dashboard");
}

export function getExecutiveWorkspace() {
    return apiGet<WorkspaceResponse>("/reporting/executive/dashboard");
}

export async function getCurrentUser() {
    if (!keycloak.token) {
        throw new Error("Not authenticated");
    }

    await keycloak.updateToken(30);

    const response = await fetch(
        `${API_URL}/auth/me`,
        {
            method: "GET",
            headers: {
                Authorization: `Bearer ${keycloak.token}`,
                "Content-Type": "application/json",
            },
        },
    );

    if (!response.ok) {
        throw new Error(
            `API request failed: ${response.status}`,
        );
    }

    return response.json();
}
