import IntelligencePanel from "../components/IntelligencePanel";
import { useEffect, useState } from "react";
import { getKycWorkspace } from "../services/api";
import type { WorkspaceResponse, WorkspaceRow } from "../services/api";
import WorkspaceLayout from "../components/workspace/WorkspaceLayout";
import {
    Metrics,
    Panel,
    Records,
    Tabs,
    WorkspaceLoading,
} from "../components/workspace/WorkspaceUi";

export default function KycMonitoring() {
    const [data, setData] = useState<WorkspaceResponse | null>(null);
    const [error, setError] = useState("");
    const [search, setSearch] = useState("");
    const [selected, setSelected] = useState("");
    useEffect(() => {
        let active = true;
        getKycWorkspace()
            .then((payload) => {
                if (active) setData(payload);
            })
            .catch((reason: unknown) => {
                if (active)
                    setError(
                        reason instanceof Error
                            ? reason.message
                            : "Unable to load KYC monitoring",
                    );
            });
        return () => {
            active = false;
        };
    }, []);
    if (!data) return <WorkspaceLoading error={error} />;
    const rows: WorkspaceRow[] = data.rows.filter((row) =>
        Object.values(row)
            .join(" ")
            .toLowerCase()
            .includes(search.toLowerCase()),
    );
    const customer = data.view.selected_customer;
    const request = data.view.request;
    return (
        <WorkspaceLayout
            module="kyc"
            data={data}
            error={error}
            search={search}
            onSearchChange={setSearch}
        >
            <Metrics data={data} />
            <Tabs items={data.view.tabs ?? []} />
            <div className="grid grid-cols-1 gap-3 xl:grid-cols-12">
                <div className="space-y-3 xl:col-span-8">
                    <Panel title={data.table_title}>
                        <Records
                            data={data}
                            rows={rows}
                            selected={selected}
                            onSelect={setSelected}
                            minWidth="min-w-[720px]"
                        />
                    </Panel>
                    <Panel title="Renewal and exception workload">
                        <div className="grid grid-cols-2 gap-3 p-3 sm:grid-cols-4">
                            {(data.view.renewal_bars ?? []).map((item) => (
                                <div key={item.label}>
                                    <div className="text-[8px] text-slate-500">
                                        {item.label}
                                    </div>
                                    <div className="mt-1 text-[14px] font-semibold text-slate-200">
                                        {item.value}
                                    </div>
                                    <div className="mt-2 h-[3px] bg-[#263342]">
                                        <div
                                            className="h-full bg-blue-400"
                                            style={{ width: `${item.width}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Panel>
                </div>
                <div className="space-y-3 xl:col-span-4">
                    <Panel
                        title={`Selected customer / ${customer?.name} · ${customer?.id}`}
                    >
                        <div className="p-3.5">
                            <div className="flex items-center gap-2">
                                <span className="bg-emerald-950/70 px-1.5 py-1 text-[7px] text-emerald-200">
                                    {customer?.identity_badge}
                                </span>
                                <span className="bg-rose-950/70 px-1.5 py-1 text-[7px] text-rose-200">
                                    {customer?.risk_badge}
                                </span>
                            </div>
                            <div className="mt-3 space-y-2 text-[8px] text-slate-400">
                                <p>Provider: {customer?.provider}</p>
                                <p>Document: {customer?.document}</p>
                                <p>Valid until: {customer?.valid_until}</p>
                                <p>Name / DOB: {customer?.name_dob}</p>
                                <p>Liveness: {customer?.liveness}</p>
                                <p>Verified at: {customer?.verified_at}</p>
                            </div>
                            <div className="mt-3 border-l-2 border-amber-400 bg-[#29271f] p-2 text-[8px] text-amber-100">
                                {customer?.notice}
                            </div>
                        </div>
                    </Panel>
                    <Panel
                        title={request?.title ?? "Document request and audit"}
                    >
                        <div className="space-y-2 p-3.5 text-[8px] text-slate-400">
                            <p>Requested: {request?.requested}</p>
                            <p>{request?.period}</p>
                            <p>Request sent: {request?.request_sent}</p>
                            <p>Due: {request?.due}</p>
                            <p>{request?.status}</p>
                            <p>{request?.audit}</p>
                        </div>
                    </Panel>
                </div>
            </div>
        
            <IntelligencePanel kind="kyc" />
        </WorkspaceLayout>
    );
}
