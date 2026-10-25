import IntelligencePanel from "../components/IntelligencePanel";
import { useEffect, useState } from "react";
import { getTransactionMonitoringWorkspace } from "../services/api";
import type { WorkspaceResponse, WorkspaceRow } from "../services/api";
import WorkspaceLayout from "../components/workspace/WorkspaceLayout";
import {
    AlertIcon,
    Metrics,
    Panel,
    Records,
    Trend,
    WorkspaceLoading,
} from "../components/workspace/WorkspaceUi";

export default function TransactionMonitoring() {
    const [data, setData] = useState<WorkspaceResponse | null>(null);
    const [error, setError] = useState("");
    const [search, setSearch] = useState("");
    const [selected, setSelected] = useState("");
    useEffect(() => {
        let active = true;
        getTransactionMonitoringWorkspace()
            .then((payload) => {
                if (active) setData(payload);
            })
            .catch((reason: unknown) => {
                if (active)
                    setError(
                        reason instanceof Error
                            ? reason.message
                            : "Unable to load transaction monitoring",
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
    const transaction = data.view.transaction;
    const evidence = data.view.evidence;
    return (
        <WorkspaceLayout
            module="transactions"
            data={data}
            error={error}
            search={search}
            onSearchChange={setSearch}
        >
            <Metrics data={data} />
            <div className="mb-3 grid grid-cols-1 gap-3 xl:grid-cols-12">
                <Trend data={data} className="xl:col-span-8" />
                <Panel
                    title={transaction?.title ?? data.side_title}
                    className="xl:col-span-4"
                >
                    <div className="flex items-center justify-between px-3.5 pt-3">
                        <span className="text-[10px] font-semibold text-slate-100">
                            {transaction?.fields[0]?.value}
                        </span>
                        <span className="bg-amber-950/70 px-1.5 py-1 text-[7px] text-amber-200">
                            {transaction?.status}
                        </span>
                    </div>
                    <div className="space-y-2 p-3.5">
                        {transaction?.fields.slice(1).map((field) => (
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
                    <div className="mx-3.5 mb-3 border-l-2 border-rose-400 bg-rose-950/40 p-2 text-[8px] text-rose-200">
                        {transaction?.warning}
                    </div>
                </Panel>
            </div>
            <Panel title={data.table_title}>
                <Records
                    data={data}
                    rows={rows}
                    selected={selected}
                    onSelect={setSelected}
                    minWidth="min-w-[720px]"
                />
            </Panel>
            <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
                <Panel title="Evidence and workflow">
                    <div className="p-3.5 text-[8px] leading-relaxed text-slate-400">
                        {evidence?.provenance}
                        <br />
                        {evidence?.session}
                        <br />
                        {evidence?.detected}
                        <br />
                        {evidence?.linked_records}
                        <br />
                        {evidence?.note}
                    </div>
                </Panel>
                <Panel title="Rule signal">
                    <AlertIcon>{transaction?.warning}</AlertIcon>
                </Panel>
            </div>
        
            <IntelligencePanel kind="aml" />
        </WorkspaceLayout>
    );
}
