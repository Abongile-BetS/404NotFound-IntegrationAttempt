import { useEffect, useState } from "react";
import { getDashboardWorkspace } from "../services/api";
import type { WorkspaceResponse, WorkspaceRow } from "../services/api";
import WorkspaceLayout from "../components/workspace/WorkspaceLayout";
import {
    Facts,
    Metrics,
    Panel,
    Records,
    Trend,
    WorkspaceLoading,
} from "../components/workspace/WorkspaceUi";

export default function DashboardHome() {
    const [data, setData] = useState<WorkspaceResponse | null>(null);
    const [error, setError] = useState("");
    const [search, setSearch] = useState("");
    const [selected, setSelected] = useState("");
    useEffect(() => {
        let active = true;
        getDashboardWorkspace()
            .then((payload) => {
                if (active) setData(payload);
            })
            .catch((reason: unknown) => {
                if (active)
                    setError(
                        reason instanceof Error
                            ? reason.message
                            : "Unable to load dashboard",
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
    const quickSearch = data.view.search;
    const activeCase = data.view.active_case;
    return (
        <WorkspaceLayout
            module="dashboard"
            data={data}
            error={error}
            search={search}
            onSearchChange={setSearch}
        >
            <Metrics data={data} />
            <div className="mb-3 grid grid-cols-1 gap-3 xl:grid-cols-12">
                <Trend data={data} className="xl:col-span-7" />
                <Panel
                    title={`${data.side_title} / Today`}
                    className="xl:col-span-5"
                >
                    <Facts items={data.side_metrics} />
                </Panel>
            </div>
            <div className="grid grid-cols-1 gap-3 xl:grid-cols-12">
                <Panel title={data.table_title} className="xl:col-span-8">
                    <Records
                        data={data}
                        rows={rows}
                        selected={selected}
                        onSelect={setSelected}
                    />
                </Panel>
                <div className="space-y-3 xl:col-span-4">
                    <Panel title={quickSearch?.title ?? "Adverse media search"}>
                        <div className="p-3.5">
                            <label className="mb-2 block text-[8px] text-slate-500">
                                {quickSearch?.label}
                            </label>
                            <p className="text-xs text-slate-500">Use the PEP, Sanctions & Media workspace to inspect screening evidence.</p>
                            <p className="mt-2 text-[7px] text-slate-500">
                                {quickSearch?.scope}
                            </p>
                        </div>
                    </Panel>
                    <Panel title={activeCase?.title ?? "Active case"}>
                        <div className="space-y-2 p-3.5">
                            <div className="flex items-center justify-between text-[10px] text-slate-200">
                                {activeCase?.customer} ·{" "}
                                {activeCase?.customer_id}
                                <span className="bg-[#1c3859] px-1.5 py-1 text-[7px] text-blue-200">
                                    {activeCase?.status}
                                </span>
                            </div>
                            <p className="text-[8px] text-slate-500">
                                {activeCase?.case_id} · {activeCase?.evidence}
                            </p>
                            <p className="text-[8px] text-slate-500">
                                {activeCase?.next_step}
                            </p>
                            <span className="text-xs text-slate-500">{activeCase?.action}</span>
                        </div>
                    </Panel>
                </div>
            </div>
        </WorkspaceLayout>
    );
}
