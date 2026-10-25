import IntelligencePanel from "../components/IntelligencePanel";
import { useEffect, useState } from "react";
import { FileText } from "lucide-react";
import { getExecutiveWorkspace } from "../services/api";
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

function exportOverview(rows: WorkspaceRow[]) {
    const columns = [...new Set(rows.flatMap((row) => Object.keys(row)))];
    const escape = (value: unknown) => `"${String(value ?? "").replaceAll('"', '""')}"`;
    const csv = [columns, ...rows.map((row) => columns.map((key) => row[key]))]
        .map((line) => line.map(escape).join(","))
        .join("\r\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `aml-overview-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
}

export default function ExecutiveDashboard() {
    const [data, setData] = useState<WorkspaceResponse | null>(null);
    const [error, setError] = useState("");
    const [search, setSearch] = useState("");
    const [selected, setSelected] = useState("");
    useEffect(() => {
        let active = true;
        getExecutiveWorkspace()
            .then((payload) => {
                if (active) setData(payload);
            })
            .catch((reason: unknown) => {
                if (active)
                    setError(
                        reason instanceof Error
                            ? reason.message
                            : "Unable to load executive dashboard",
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
    const report = data.view.report;
    return (
        <WorkspaceLayout
            module="executive"
            data={data}
            error={error}
            search={search}
            onSearchChange={setSearch}
        >
            <Metrics data={data} />
            <div className="mb-3 grid grid-cols-1 gap-3 xl:grid-cols-12">
                <Trend data={data} className="xl:col-span-7" />
                <Panel
                    title={
                        data.view.distribution_title ??
                        "Customer risk distribution"
                    }
                    className="xl:col-span-5"
                >
                    <div className="space-y-4 p-3.5">
                        {(data.view.distribution ?? []).map((risk) => (
                            <div key={risk.label}>
                                <div className="mb-1.5 flex justify-between text-[8px]">
                                    <span>{risk.label}</span>
                                    <span className="text-slate-500">
                                        {risk.count}
                                    </span>
                                </div>
                                <div className="h-[5px] bg-[#263342]">
                                    <div
                                        className={`h-full ${risk.tone === "red" ? "bg-rose-400" : risk.tone === "amber" ? "bg-amber-300" : "bg-emerald-300"}`}
                                        style={{ width: `${risk.width}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                        <p className="text-[7px] text-slate-500">
                            {data.view.distribution_note}
                        </p>
                    </div>
                </Panel>
            </div>
            <div className="grid grid-cols-1 gap-3 xl:grid-cols-12">
                <Panel title={data.table_title} className="xl:col-span-7">
                    <Records
                        data={data}
                        rows={rows}
                        selected={selected}
                        onSelect={setSelected}
                    />
                </Panel>
                <div className="space-y-3 xl:col-span-5">
                    <Panel title={data.side_title}>
                        <Facts items={data.side_metrics} />
                    </Panel>
                    <Panel title="Rule effectiveness and reporting">
                        <div className="divide-y divide-[#263342] p-3.5 text-[8px] text-slate-400">
                            {(data.view.rules ?? []).map((rule) => (
                                <div
                                    key={rule.name}
                                    className="grid grid-cols-2 gap-2 py-2"
                                >
                                    <span>{rule.name}</span>
                                    <span>
                                        {rule.resolved} resolved ·{" "}
                                        {rule.false_positives} false positives ·{" "}
                                        {rule.rate}
                                        <br />
                                        <span className="text-slate-500">
                                            {rule.action}
                                        </span>
                                    </span>
                                </div>
                            ))}
                            <div className="mt-2 flex items-center gap-2 border-t border-[#263342] pt-3 text-emerald-300">
                                <FileText size={12} />
                                {report?.title} · {report?.status}
                            </div>
                            <div className="mt-2 space-y-1 text-slate-500">
                                <p>{report?.dataset}</p>
                                <p>{report?.includes}</p>
                                <p>{report?.period}</p>
                                <p>{report?.privacy}</p>
                                <p>{report?.last_export}</p>
                            </div>
                            <button type="button" disabled={!rows.length} onClick={() => exportOverview(rows)} className="mt-3 bg-blue-500 px-3 py-1.5 text-[8px] text-white disabled:cursor-not-allowed disabled:opacity-50">
                                Export overview
                            </button>
                        </div>
                    </Panel>
                </div>
            </div>
        
            <IntelligencePanel kind="reports" /><IntelligencePanel kind="geography" />
        </WorkspaceLayout>
    );
}
