import IntelligencePanel from "../components/IntelligencePanel";
import { useEffect, useState } from "react";
import { getScreeningWorkspace } from "../services/api";
import type { WorkspaceResponse, WorkspaceRow } from "../services/api";
import WorkspaceLayout from "../components/workspace/WorkspaceLayout";
import {
    Facts,
    Panel,
    Records,
    RiskBreakdown,
    Tabs,
    WorkspaceLoading,
} from "../components/workspace/WorkspaceUi";

export default function RiskScreening() {
    const [data, setData] = useState<WorkspaceResponse | null>(null);
    const [error, setError] = useState("");
    const [search, setSearch] = useState("");
    const [selected, setSelected] = useState("");
    useEffect(() => {
        let active = true;
        getScreeningWorkspace()
            .then((payload) => {
                if (active) setData(payload);
            })
            .catch((reason: unknown) => {
                if (active)
                    setError(
                        reason instanceof Error
                            ? reason.message
                            : "Unable to load screening workspace",
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
            module="screening"
            data={data}
            error={error}
            search={search}
            onSearchChange={setSearch}
        >
            <Panel title={`${customer?.name} / ${customer?.id}`}>
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
                    <div className="text-[8px] text-slate-500">
                        KYC / Screening
                        <br />
                        <span className="text-amber-200">
                            {customer?.screening_status}
                        </span>
                    </div>
                    <div className="text-[8px] text-slate-500">
                        Account status
                        <br />
                        <span className="text-slate-200">
                            {customer?.account_status}
                        </span>
                    </div>
                    <div className="text-[8px] text-slate-500">
                        Assigned analyst
                        <br />
                        <span className="text-slate-200">
                            {customer?.analyst}
                        </span>
                    </div>
                    <div className="ml-auto text-right">
                        <div className="text-[20px] font-semibold text-rose-300">
                            {customer?.risk_score}
                        </div>
                        <span className="bg-rose-950/70 px-1.5 py-1 text-[7px] text-rose-200">
                            {customer?.risk_label}
                        </span>
                    </div>
                </div>
            </Panel>
            <Tabs items={data.view.tabs ?? []} />
            <div className="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-12">
                <div className="space-y-3 xl:col-span-8">
                    <Panel
                        title={`${data.table_title} / ${data.view.last_screened}`}
                    >
                        <div className="grid grid-cols-2 gap-2 p-3 sm:grid-cols-4">
                            {data.kpis.map((item) => (
                                <div
                                    key={item.label}
                                    className="border border-[#263342] bg-[#172331] p-2.5"
                                >
                                    <div className="text-[8px] text-slate-500">
                                        {item.label}
                                    </div>
                                    <div className="mt-2 text-[11px] font-semibold text-slate-200">
                                        {item.value}
                                    </div>
                                    <div className="mt-1 text-[8px] text-slate-500">
                                        {item.detail}
                                    </div>
                                </div>
                            ))}
                        </div>
                        <Records
                            data={data}
                            rows={rows}
                            selected={selected}
                            onSelect={setSelected}
                        />
                    </Panel>
                    <Panel title="Adverse media evidence">
                        <div className="divide-y divide-[#263342] p-3.5">
                            {(data.view.media ?? []).map((item) => (
                                <div
                                    key={item.title}
                                    className="flex items-start gap-3 py-2"
                                >
                                    <span className="bg-[#3a3020] px-1.5 py-1 text-[7px] text-amber-200">
                                        {item.badge}
                                    </span>
                                    <div>
                                        <div className="text-[9px] font-medium text-blue-300">
                                            {item.title}
                                        </div>
                                        <div className="mt-1 text-[8px] text-slate-500">
                                            {item.source} · {item.published} ·{" "}
                                            {item.indexed}
                                        </div>
                                        <p className="mt-1 text-[8px] text-slate-400">
                                            {item.body}
                                        </p>
                                    </div>
                                    <span className="text-xs text-slate-500">{item.action}</span>
                                </div>
                            ))}
                        </div>
                    </Panel>
                    <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                        <Panel title="Customer profile">
                            <div className="space-y-2 p-3.5">
                                {(data.view.profile ?? []).map((field) => (
                                    <p
                                        key={field.label}
                                        className="text-[8px] text-slate-500"
                                    >
                                        {field.label}:{" "}
                                        <span className="text-slate-300">
                                            {field.value}
                                        </span>
                                    </p>
                                ))}
                            </div>
                        </Panel>
                        <Panel title="Risk history / Model snapshots">
                            <div className="divide-y divide-[#263342] px-3.5">
                                {(data.view.history ?? []).map((item) => (
                                    <div
                                        key={item.timestamp}
                                        className="grid grid-cols-3 gap-2 py-2 text-[8px]"
                                    >
                                        <span>{item.timestamp}</span>
                                        <span className="text-rose-300">
                                            {item.score}
                                        </span>
                                        <span>{item.change}</span>
                                    </div>
                                ))}
                            </div>
                        </Panel>
                    </div>
                </div>
                <div className="space-y-3 xl:col-span-4">
                    <Panel title={data.side_title}>
                        <RiskBreakdown data={data} />
                    </Panel>
                    <Panel title="Review checkpoint">
                        <Facts items={data.side_metrics} />
                    </Panel>
                </div>
            </div>
        
            <IntelligencePanel kind="screening" /><IntelligencePanel kind="media" />
        </WorkspaceLayout>
    );
}
