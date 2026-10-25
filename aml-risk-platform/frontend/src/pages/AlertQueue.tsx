import { useEffect, useState } from "react";
import { getAlertWorkspace } from "../services/api";
import type { WorkspaceResponse, WorkspaceRow } from "../services/api";
import WorkspaceLayout from "../components/workspace/WorkspaceLayout";
import {
    Metrics,
    Panel,
    Records,
    Tabs,
    WorkspaceLoading,
} from "../components/workspace/WorkspaceUi";

export default function AlertQueue() {
    const [data, setData] = useState<WorkspaceResponse | null>(null);
    const [error, setError] = useState("");
    const [search, setSearch] = useState("");
    const [selected, setSelected] = useState("");

    useEffect(() => {
        let active = true;
        getAlertWorkspace()
            .then((payload) => {
                if (active) setData(payload);
            })
            .catch((reason: unknown) => {
                if (active)
                    setError(
                        reason instanceof Error
                            ? reason.message
                            : "Unable to load alerts",
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
    const alert = data.view.selected_alert;
    return (
        <WorkspaceLayout
            module="alerts"
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
                    <Panel title="Analyst workload / Open alerts by owner">
                        <div className="grid grid-cols-2 gap-2 p-3 sm:grid-cols-4">
                            {(data.view.workload ?? []).map((item) => (
                                <div
                                    key={item.name}
                                    className="bg-[#1a2633] p-2.5"
                                >
                                    <div className="text-[9px] font-medium text-slate-200">
                                        {item.name}
                                    </div>
                                    <div className="mt-1 text-[10px] text-blue-300">
                                        {item.count}
                                    </div>
                                    <div className="mt-1 text-[7px] text-slate-500">
                                        {item.detail}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Panel>
                </div>
                <div className="xl:col-span-4">
                    <Panel title={`Selected alert / ${alert?.id}`}>
                        <div className="p-3.5">
                            <div className="flex items-center justify-between">
                                <span className="bg-rose-950/70 px-1.5 py-1 text-[7px] text-rose-200">
                                    {alert?.priority}
                                </span>
                                <span className="bg-[#1c3859] px-1.5 py-1 text-[7px] text-blue-200">
                                    {alert?.status}
                                </span>
                            </div>
                            <h3 className="mt-3 text-[12px] font-semibold text-slate-100">
                                {alert?.customer}
                            </h3>
                            <p className="mt-2 text-[8px] leading-relaxed text-slate-400">
                                {alert?.description}
                            </p>
                            <div className="mt-3 space-y-1.5 border-y border-[#263342] py-3 text-[8px] text-slate-400">
                                <p>Detected: {alert?.detected}</p>
                                <p>Owner / SLA: {alert?.owner_sla}</p>
                                <p>Linked case: {alert?.case}</p>
                            </div>
                            <div className="my-3 space-y-2 text-[8px] text-slate-400">
                                {(alert?.factors ?? []).map((item) => (
                                    <div
                                        key={item.name}
                                        className="flex justify-between"
                                    >
                                        <span>{item.name}</span>
                                        <span className="text-rose-300">
                                            {item.score}
                                        </span>
                                    </div>
                                ))}
                            </div>
                            <div className="mb-3 border-l-2 border-amber-400 bg-[#29271f] p-2 text-[8px] text-amber-100">
                                {alert?.disclaimer}
                            </div>
                            <div className="flex gap-2">
                                <span className="text-xs text-slate-500">Reassign</span>
                                <span className="text-xs text-slate-500">Open investigation</span>
                            </div>
                        </div>
                    </Panel>
                </div>
            </div>
        </WorkspaceLayout>
    );
}
