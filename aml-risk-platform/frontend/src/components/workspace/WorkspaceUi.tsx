import type { ReactNode } from "react";
import { CircleAlert, ShieldCheck } from "lucide-react";
import {
    CartesianGrid,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import type { WorkspaceResponse, WorkspaceRow } from "../../services/api";

const tones: Record<string, string> = {
    red: "text-rose-600",
    amber: "text-amber-600",
    blue: "text-indigo-600",
    green: "text-emerald-600",
    white: "text-slate-900",
};

const cls = (...parts: Array<string | false | undefined>) =>
    parts.filter(Boolean).join(" ");

export function Panel({
    title,
    children,
    className = "",
}: {
    title: string;
    children: ReactNode;
    className?: string;
}) {
    return (
        <section
            className={cls(
                "min-w-0 overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-[0_10px_35px_rgba(31,24,74,0.055)]",
                className,
            )}
        >
            <div className="flex min-h-[66px] items-center gap-3 px-4 py-3 sm:px-5">
                <div className="flex min-w-0 items-center gap-3">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-violet-50 text-violet-600">
                        <ShieldCheck size={18} />
                    </div>
                    <h2 className="min-w-0 text-[13px] font-bold text-slate-900 sm:text-[15px]">
                        {title}
                    </h2>
                </div>

            </div>
            {children}
        </section>
    );
}

export function Metrics({ data }: { data: WorkspaceResponse }) {
    const iconStyles: Record<string, string> = {
        red: "bg-pink-50 text-pink-600",
        amber: "bg-amber-50 text-amber-600",
        blue: "bg-indigo-50 text-indigo-600",
        green: "bg-emerald-50 text-emerald-600",
        purple: "bg-violet-50 text-violet-600",
    };

    return (
        <div className="mb-5 flex flex-wrap gap-4">
            {data.kpis.map((metric, index) => (
                <section
                    key={metric.label}
                    className="min-w-[190px] flex-1 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_10px_30px_rgba(31,24,74,0.05)]"
                >
                    <div className="flex items-start justify-between gap-3">
                        <div
                            className={cls(
                                "flex h-10 w-10 items-center justify-center rounded-xl",
                                iconStyles[metric.tone] ??
                                    ["bg-violet-50 text-violet-600", "bg-indigo-50 text-indigo-600", "bg-amber-50 text-amber-600", "bg-pink-50 text-pink-600"][index % 4],
                            )}
                        >
                            <ShieldCheck size={20} />
                        </div>
                        <span className="rounded-full bg-slate-50 px-2 py-1 text-[9px] font-semibold text-slate-400">
                            Live metrics
                        </span>
                    </div>

                    <p className="mt-4 text-xs font-medium text-slate-500">
                        {metric.label}
                    </p>
                    <p
                        className={cls(
                            "mt-1 text-2xl font-black tracking-tight",
                            tones[metric.tone] ?? "text-slate-900",
                        )}
                    >
                        {metric.value}
                    </p>
                    <p className="mt-1 text-[10px] leading-relaxed text-slate-400">
                        {metric.detail}
                    </p>
                </section>
            ))}
        </div>
    );
}

export function Trend({
    data,
    className = "",
}: {
    data: WorkspaceResponse;
    className?: string;
}) {
    return (
        <Panel title={data.trend_title} className={className}>
            <div className="h-[260px] px-3 pb-2 pt-4 sm:px-4">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                        data={data.trend}
                        margin={{ top: 8, right: 10, left: -18, bottom: 0 }}
                    >
                        <CartesianGrid
                            stroke="#eef0f7"
                            strokeDasharray="3 4"
                            vertical={false}
                        />
                        <XAxis
                            dataKey="label"
                            tick={{ fill: "#94a3b8", fontSize: 10 }}
                            axisLine={false}
                            tickLine={false}
                            tickMargin={10}
                        />
                        <YAxis
                            tick={{ fill: "#94a3b8", fontSize: 10 }}
                            axisLine={false}
                            tickLine={false}
                            tickMargin={8}
                        />
                        <Tooltip
                            contentStyle={{
                                background: "#ffffff",
                                border: "1px solid #e2e8f0",
                                borderRadius: 12,
                                boxShadow: "0 8px 24px rgba(15,23,42,.08)",
                                color: "#334155",
                                fontSize: 11,
                            }}
                        />
                        {data.series.map((series, index) => (
                            <Line
                                key={series.key}
                                type="monotone"
                                dataKey={series.key}
                                name={series.label}
                                stroke={
                                    series.color ||
                                    ["#8b5cf6", "#14b8a6", "#f59e0b", "#ec4899"][index % 4]
                                }
                                strokeWidth={2.5}
                                dot={false}
                                activeDot={{ r: 4 }}
                            />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div className="flex flex-wrap gap-x-5 gap-y-2 px-5 pb-4">
                {data.series.map((series, index) => (
                    <span
                        key={series.key}
                        className="flex items-center gap-2 text-[10px] font-medium text-slate-500"
                    >
                        <i
                            className="h-2 w-2 rounded-full"
                            style={{
                                backgroundColor:
                                    series.color ||
                                    ["#8b5cf6", "#14b8a6", "#f59e0b", "#ec4899"][index % 4],
                            }}
                        />
                        {series.label}
                    </span>
                ))}
            </div>
        </Panel>
    );
}

function getStatusStyle(value: string) {
    if (/high|overdue|held|expired|candidate|pending|action required/i.test(value)) {
        return "bg-amber-50 text-amber-700 ring-amber-100";
    }
    if (/verified|clear|complete|no match|resolved/i.test(value)) {
        return "bg-emerald-50 text-emerald-700 ring-emerald-100";
    }
    if (/critical|blocked|rejected|failed/i.test(value)) {
        return "bg-pink-50 text-pink-700 ring-pink-100";
    }
    return "bg-violet-50 text-violet-700 ring-violet-100";
}

export function Records({
    data,
    rows,
    selected,
    onSelect,
    minWidth = "min-w-[640px]",
}: {
    data: WorkspaceResponse;
    rows: WorkspaceRow[];
    selected?: string;
    onSelect?: (id: string) => void;
    minWidth?: string;
}) {
    return (
        <div className="overflow-x-auto px-3 pb-4 sm:px-4">
            <table
                className={cls(
                    "w-full border-separate border-spacing-0 text-left",
                    minWidth,
                )}
            >
                <thead>
                    <tr className="bg-slate-50 text-[10px] uppercase tracking-wide text-slate-400">
                        {data.columns.map((column, index) => (
                            <th
                                key={column.key}
                                className={cls(
                                    "px-3 py-3 font-semibold",
                                    index === 0 && "rounded-l-lg",
                                    index === data.columns.length - 1 && "rounded-r-lg",
                                )}
                            >
                                {column.label}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row, index) => {
                        const id = String(row.id ?? index);
                        const isSelected = selected
                            ? selected === id
                            : String(rows[0]?.id ?? 0) === id;

                        return (
                            <tr
                                key={id}
                                onClick={() => onSelect?.(id)}
                                tabIndex={0}
                                onKeyDown={(event) => {
                                    if (event.key === "Enter" || event.key === " ") {
                                        event.preventDefault();
                                        onSelect?.(id);
                                    }
                                }}
                                className={cls(
                                    "cursor-pointer transition hover:bg-violet-50/60",
                                    isSelected && "bg-violet-50/40",
                                )}
                            >
                                {data.columns.map((column) => {
                                    const value = String(row[column.key] ?? "—");
                                    const isStatus =
                                        /verified|clear|complete|no match|high|overdue|held|expired|candidate|pending|action required|critical|blocked|rejected|failed|review/i.test(value);

                                    return (
                                        <td
                                            key={column.key}
                                            className="border-b border-slate-100 px-3 py-3 text-[11px] text-slate-500"
                                        >
                                            {isStatus ? (
                                                <span
                                                    className={cls(
                                                        "inline-flex max-w-[200px] items-center rounded-full px-2.5 py-1 text-[10px] font-semibold ring-1",
                                                        getStatusStyle(value),
                                                    )}
                                                >
                                                    {value}
                                                </span>
                                            ) : (
                                                <span
                                                    className={cls(
                                                        "block max-w-[240px] truncate",
                                                        column === data.columns[0] &&
                                                            "font-bold text-slate-800",
                                                    )}
                                                    title={value}
                                                >
                                                    {value}
                                                </span>
                                            )}
                                        </td>
                                    );
                                })}
                            </tr>
                        );
                    })}
                </tbody>
            </table>

            {rows.length === 0 && (
                <div className="px-4 py-10 text-center">
                    <div className="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-violet-50 text-violet-500">
                        <ShieldCheck size={19} />
                    </div>
                    <p className="text-xs font-semibold text-slate-700">
                        No records found
                    </p>
                    <p className="mt-1 text-[10px] text-slate-400">
                        Try adjusting your search terms.
                    </p>
                </div>
            )}

            <div className="flex items-center justify-between px-1 pt-3 text-[10px] text-slate-400">
                <span>
                    Showing {rows.length} of {data.rows.length} records
                </span>
                <span className="font-medium text-violet-600">
                    {rows.length > 0 ? "Filtered results" : "No results"}
                </span>
            </div>
        </div>
    );
}

export function Facts({
    items,
}: {
    items: WorkspaceResponse["side_metrics"];
}) {
    return (
        <div className="space-y-3 px-4 py-4 sm:px-5">
            {items.map((item, index) => (
                <div
                    key={item.label}
                    className="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50/60 p-3 transition hover:border-violet-100 hover:bg-violet-50/40"
                >
                    <div
                        className={cls(
                            "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
                            [
                                "bg-violet-50 text-violet-600",
                                "bg-amber-50 text-amber-600",
                                "bg-pink-50 text-pink-600",
                                "bg-emerald-50 text-emerald-600",
                            ][index % 4],
                        )}
                    >
                        <span className="text-xs font-black">
                            {item.label.slice(0, 1).toUpperCase()}
                        </span>
                    </div>

                    <div className="min-w-0 flex-1">
                        <div className="text-[11px] font-bold text-slate-800">
                            {item.label}
                        </div>
                        <div
                            className={cls(
                                "mt-1 text-sm font-bold",
                                tones[item.tone] ?? "text-slate-700",
                            )}
                        >
                            {item.value}
                        </div>
                        <div className="mt-1 text-[10px] leading-relaxed text-slate-400">
                            {item.detail}
                        </div>
                    </div>

                </div>
            ))}
        </div>
    );
}

export function Tabs({ items }: { items: string[] }) {
    return (
        <div className="flex gap-5 overflow-x-auto border-b border-slate-100 px-5">
            {items.map((item, index) => (
                <span
                    key={item}
                    className={cls(
                        "shrink-0 border-b-2 py-3 text-[11px] font-semibold",
                        index === 0
                            ? "border-violet-600 text-violet-700"
                            : "border-transparent text-slate-400",
                    )}
                >
                    {item}
                </span>
            ))}
        </div>
    );
}


export function RiskBreakdown({ data }: { data: WorkspaceResponse }) {
    const risk = data.view.risk;
    const factors = risk?.factors ?? [];
    const maximum = Math.max(...factors.map((item) => item.value), 1);

    return (
        <div className="space-y-4 p-4 sm:p-5">
            <div className="flex items-end justify-between gap-3 rounded-xl bg-rose-50/70 p-4">
                <div>
                    <span className="text-[10px] font-medium text-slate-500">
                        Explainable risk score
                    </span>
                    <p className="mt-1 text-[11px] text-slate-400">
                        Based on the available risk factors
                    </p>
                </div>
                <div className="text-right">
                    <span className="text-3xl font-black tracking-tight text-rose-600">
                        {risk?.score ?? "—"}
                    </span>
                    <div className="mt-1 text-[10px] font-bold text-rose-600">
                        {risk?.level}
                    </div>
                </div>
            </div>

            {factors.map((item) => (
                <div key={item.label}>
                    <div className="flex justify-between gap-3 text-[10px]">
                        <span className="font-semibold text-slate-700">
                            +{item.value} {item.label}
                        </span>
                        <span className="text-right text-slate-400">
                            {item.detail}
                        </span>
                    </div>
                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
                        <div
                            className="h-full rounded-full bg-gradient-to-r from-pink-500 to-rose-400"
                            style={{
                                width: `${Math.max(5, (item.value / maximum) * 100)}%`,
                            }}
                        />
                    </div>
                </div>
            ))}

            {risk?.disclaimer && (
                <div className="rounded-xl border border-amber-100 bg-amber-50 px-3 py-3 text-[10px] leading-relaxed text-amber-800">
                    {risk.disclaimer}
                </div>
            )}

            {risk?.formula && (
                <div className="text-[10px] leading-relaxed text-slate-400">
                    {risk.formula}
                </div>
            )}
        </div>
    );
}

export function RelationshipGraph({ data }: { data: WorkspaceResponse }) {
    const graph = data.view.graph;
    const nodes = graph?.nodes ?? [];
    const nodeById = new Map(nodes.map((item) => [item.id, item]));

    return (
        <div className="relative h-[310px] overflow-hidden bg-slate-50">
            <svg
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
                className="absolute inset-0 h-full w-full"
                aria-hidden="true"
            >
                {(graph?.edges ?? []).map((edge) => {
                    const from = nodeById.get(edge.from);
                    const to = nodeById.get(edge.to);

                    return from && to ? (
                        <line
                            key={`${edge.from}-${edge.to}`}
                            x1={from.x}
                            y1={from.y}
                            x2={to.x}
                            y2={to.y}
                            stroke="#cbd5e1"
                            strokeWidth="0.4"
                        />
                    ) : null;
                })}
            </svg>

            {nodes.map((node) => (
                <div
                    key={node.id}
                    className="absolute z-10 -translate-x-1/2 -translate-y-1/2 text-center"
                    style={{ left: `${node.x}%`, top: `${node.y}%` }}
                >
                    <div
                        className={cls(
                            "mx-auto flex h-8 w-8 items-center justify-center border shadow-sm",
                            node.type === "selected"
                                ? "rounded-full border-rose-200 bg-rose-50 text-rose-600"
                                : node.type === "device"
                                  ? "rounded-xl border-indigo-200 bg-indigo-50 text-indigo-600"
                                  : "rounded-full border-violet-200 bg-white text-violet-600",
                        )}
                    >
                        <span className="text-[9px] font-bold">
                            {node.type === "device"
                                ? "D"
                                : node.type === "selected"
                                  ? "!"
                                  : "C"}
                        </span>
                    </div>
                    <div className="mt-1 whitespace-nowrap rounded bg-white/90 px-1 text-[8px] font-semibold text-slate-700">
                        {node.name}
                    </div>
                    <div className="mt-0.5 whitespace-nowrap text-[7px] text-slate-400">
                        {node.label}
                    </div>
                </div>
            ))}

            {graph?.note && (
                <div className="absolute bottom-2 left-3 rounded-lg bg-white/90 px-2 py-1 text-[8px] text-slate-500">
                    {graph.note}
                </div>
            )}
        </div>
    );
}

export function AlertIcon({ children }: { children: ReactNode }) {
    return (
        <div className="flex items-start gap-3 rounded-xl bg-rose-50/70 p-4">
            <CircleAlert className="mt-0.5 shrink-0 text-rose-500" size={18} />
            <div className="text-[11px] leading-relaxed text-slate-600">
                {children}
            </div>
        </div>
    );
}

export function WorkspaceLoading({ error }: { error: string }) {
    return (
        <main className="flex min-h-screen items-center justify-center bg-[#f7f7fb] p-6 text-slate-600">
            <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-[0_10px_35px_rgba(31,24,74,0.055)]">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-50 text-violet-600">
                    <ShieldCheck size={24} />
                </div>
                <h1 className="mt-4 text-lg font-black text-slate-900">
                    BETSOFTWARE
                </h1>
                <p className="mt-2 text-xs leading-relaxed text-slate-500">
                    {error || "Loading workspace data..."}
                </p>
                {error && (
                    <p className="mt-3 text-[10px] text-rose-600">
                        Check your API connection and try refreshing the page.
                    </p>
                )}
            </div>
        </main>
    );
}
