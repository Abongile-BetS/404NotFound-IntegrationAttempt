import IntelligencePanel from "../components/IntelligencePanel";
import { useEffect, useState } from "react";
import { getInvestigationWorkspace } from "../services/api";
import type { WorkspaceResponse, WorkspaceRow } from "../services/api";
import WorkspaceLayout from "../components/workspace/WorkspaceLayout";
import {
    Panel,
    Records,
    RelationshipGraph,
    RiskBreakdown,
    Tabs,
    WorkspaceLoading,
} from "../components/workspace/WorkspaceUi";

export default function InvestigationWorkspace() {
    const [data, setData] = useState<WorkspaceResponse | null>(null);
    const [error, setError] = useState("");
    const [search, setSearch] = useState("");
    const [selected, setSelected] = useState("");
    useEffect(() => {
        let active = true;
        getInvestigationWorkspace()
            .then((payload) => {
                if (active) setData(payload);
            })
            .catch((reason: unknown) => {
                if (active)
                    setError(
                        reason instanceof Error
                            ? reason.message
                            : "Unable to load investigation",
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
    const customer = data.view.customer;
    return (
        <WorkspaceLayout
            module="investigations"
            data={data}
            error={error}
            search={search}
            onSearchChange={setSearch}
        >
            <Panel title={`Investigation subject / ${data.view.case_id}`}>
                <div className="flex flex-wrap items-center gap-3 p-3.5">
                    <div className="flex h-9 w-9 items-center justify-center bg-[#263747] text-[11px] font-semibold">
                        {customer?.initials}
                    </div>
                    <div className="min-w-[130px] flex-1">
                        <div className="text-[13px] font-semibold text-slate-100">
                            {customer?.name}
                        </div>
                        <div className="mt-1 text-[8px] text-slate-500">
                            {customer?.id} · {customer?.country} ·{" "}
                            {customer?.joined}
                        </div>
                    </div>
                    {data.kpis.slice(1).map((item) => (
                        <div
                            key={item.label}
                            className="text-[8px] text-slate-500"
                        >
                            {item.label}
                            <br />
                            <span>{item.value}</span>
                        </div>
                    ))}
                </div>
            </Panel>
            <Tabs items={data.view.tabs ?? []} />
            <div className="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-12">
                <div className="space-y-3 xl:col-span-8">
                    <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                        <Panel
                            title={`KYC and screening / ${data.view.snapshot}`}
                        >
                            <div className="space-y-2 p-3.5 text-[8px] text-slate-400">
                                {data.kpis.slice(1).map((item) => (
                                    <p key={item.label}>
                                        {item.label}: {item.value} ·{" "}
                                        {item.detail}
                                    </p>
                                ))}
                            </div>
                        </Panel>
                        <Panel title="Activity summary">
                            <div className="space-y-2 p-3.5 text-[8px] text-slate-400">
                                {(data.view.activity ?? []).map((item) => (
                                    <p key={item.label}>
                                        {item.label}:{" "}
                                        <span className="text-slate-200">
                                            {item.value}
                                        </span>
                                    </p>
                                ))}
                            </div>
                        </Panel>
                    </div>
                    <Panel
                        title={`Network evidence / ${data.view.graph?.cluster}`}
                    >
                        <RelationshipGraph data={data} />
                    </Panel>
                    <Panel
                        title={`Evidence register / ${data.view.evidence_summary}`}
                    >
                        <Records
                            data={data}
                            rows={rows}
                            selected={selected}
                            onSelect={setSelected}
                            minWidth="min-w-[650px]"
                        />
                    </Panel>
                </div>
                <div className="space-y-3 xl:col-span-4">
                    <Panel title="Model evidence">
                        <RiskBreakdown data={data} />
                    </Panel>
                    <Panel title="Recorded analyst notes">
                        <div className="space-y-3 p-3.5 text-[8px] text-slate-400">
                            {(data.view.notes ?? []).map((note) => (
                                <div
                                    key={`${note.author}-${note.timestamp}`}
                                    className="border border-[#263342] bg-[#172331] p-2.5"
                                >
                                    <div className="text-slate-300">
                                        {note.author} · {note.timestamp} ·{" "}
                                        {note.label}
                                    </div>
                                    <p className="mt-2 leading-relaxed">
                                        {note.body}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </Panel>
                </div>
            </div>
        
            <IntelligencePanel kind="risk" /><IntelligencePanel kind="rules" />
        </WorkspaceLayout>
    );
}
