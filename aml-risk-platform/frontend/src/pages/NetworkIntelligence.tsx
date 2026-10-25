import IntelligencePanel from "../components/IntelligencePanel";
import { useEffect, useState } from "react";
import { getNetworkIntelligenceWorkspace } from "../services/api";
import type { WorkspaceResponse, WorkspaceRow } from "../services/api";
import WorkspaceLayout from "../components/workspace/WorkspaceLayout";
import {
    Facts,
    Metrics,
    Panel,
    Records,
    RelationshipGraph,
    WorkspaceLoading,
} from "../components/workspace/WorkspaceUi";

export default function NetworkIntelligence() {
    const [data, setData] = useState<WorkspaceResponse | null>(null);
    const [error, setError] = useState("");
    const [search, setSearch] = useState("");
    const [selected, setSelected] = useState("");
    useEffect(() => {
        let active = true;
        getNetworkIntelligenceWorkspace()
            .then((payload) => {
                if (active) setData(payload);
            })
            .catch((reason: unknown) => {
                if (active)
                    setError(
                        reason instanceof Error
                            ? reason.message
                            : "Unable to load network intelligence",
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
    const graph = data.view.graph;
    const entity = data.view.selected_entity;
    return (
        <WorkspaceLayout
            module="network"
            data={data}
            error={error}
            search={search}
            onSearchChange={setSearch}
        >
            <Metrics data={data} />
            <div className="grid grid-cols-1 gap-3 xl:grid-cols-12">
                <div className="space-y-3 xl:col-span-8">
                    <Panel title={`${graph?.title} / ${graph?.cluster}`}>
                        <div className="flex items-center justify-between px-3.5 py-2 text-[8px] text-slate-500">
                            <span>{graph?.seed}</span>
                        </div>
                        <RelationshipGraph data={data} />
                        <div className="border-t border-[#263342] px-3 py-2 text-[7px] text-slate-500">
                            {graph?.legend}
                        </div>
                    </Panel>
                    <Panel title={data.table_title}>
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
                    <Panel title={`${entity?.title} / ${entity?.id}`}>
                        <div className="p-3.5">
                            <div className="flex items-center justify-between text-[12px] font-semibold text-slate-100">
                                {entity?.name}
                                <span className="bg-rose-950/70 px-1.5 py-1 text-[7px] text-rose-200">
                                    {entity?.risk}
                                </span>
                            </div>
                            <div className="mt-3 space-y-2 text-[8px] text-slate-400">
                                <p>Cluster: {entity?.cluster}</p>
                                <p>Device: {entity?.device}</p>
                                <p>IP address: {entity?.ip}</p>
                                <p>Network score: {entity?.signals}</p>
                            </div>
                        </div>
                    </Panel>
                    <Panel title={data.side_title}>
                        <Facts items={data.side_metrics} />
                    </Panel>
                </div>
            </div>
        
            <IntelligencePanel kind="network" />
        </WorkspaceLayout>
    );
}
