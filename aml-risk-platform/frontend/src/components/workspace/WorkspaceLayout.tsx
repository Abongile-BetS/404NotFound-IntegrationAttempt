import {
    Activity,
    Bell,
    ChevronDown,
    ChevronRight,
    FileBarChart,
    Fingerprint,
    LayoutDashboard,
    LogOut,
    Menu,
    Network,
    Search,
    ShieldAlert,
    ShieldCheck,
    X,
} from "lucide-react";
import { useState, type ReactNode } from "react";
import { NavLink } from "react-router-dom";
import type { WorkspaceResponse } from "../../services/api";
import { useAuth } from "../../services/AuthProvider";

const sections = [
    { title: "Overview", items: [
        { label: "Home dashboard", path: "/dashboard", module: "dashboard", icon: LayoutDashboard },
        { label: "Executive & AI Reports", path: "/executive", module: "executive", icon: FileBarChart },
    ] },
    { title: "Customer compliance", items: [
        { label: "KYC & CDD", path: "/kyc", module: "kyc", icon: Fingerprint },
        { label: "PEP, Sanctions & Media", path: "/screening", module: "screening", icon: ShieldCheck },
    ] },
    { title: "Detection & intelligence", items: [
        { label: "AML & Transactions", path: "/transactions", module: "transactions", icon: Activity },
        { label: "Network Intelligence", path: "/network", module: "network", icon: Network },
        { label: "Risk & Rule Evaluation", path: "/investigations", module: "investigations", icon: ShieldAlert },
    ] },
    { title: "Operations", items: [
        { label: "Alert queue", path: "/alerts", module: "alerts", icon: Bell },
    ] },
];
const items = sections.flatMap(section => section.items);

function Sidebar({
    data,
    onClose,
    onLogout,
}: {
    data: WorkspaceResponse;
    onClose?: () => void;
    onLogout: () => Promise<void>
}) {
    return (
        <aside className="flex h-full flex-col border-r border-slate-200 bg-white text-slate-600">
            <div className="flex h-[82px] shrink-0 items-center gap-3 border-b border-slate-100 px-5">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 via-indigo-500 to-purple-700 text-white shadow-[0_8px_25px_rgba(109,40,217,0.25)]">
                    <ShieldCheck size={24} strokeWidth={2.4} />
                </div>

                <div className="min-w-0">
                    <div className="text-xl font-black text-slate-950">
                        BET SOFTWARE
                    </div>
                    <div className="text-[9px] font-bold uppercase tracking-[0.14em] text-violet-600">
                        AI Risk Intelligence
                    </div>
                </div>

                {onClose && (
                    <button
                        type="button"
                        onClick={onClose}
                        aria-label="Close navigation"
                        className="ml-auto rounded-lg p-2 text-slate-400 hover:bg-slate-100"
                    >
                        <X size={18} />
                    </button>
                )}
            </div>
            <nav className="flex-1 space-y-4 overflow-y-auto px-3 pb-4 pt-5">
                {sections.map(section => <div key={section.title}>
                    <div className="px-3 pb-2 text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">{section.title}</div>
                    {section.items.map(({ label, path, module: itemModule, icon: Icon }) => (
                        <NavLink key={path} to={path} onClick={onClose} end
                            className={({isActive}) => `group flex min-h-[43px] items-center gap-3 rounded-xl px-3 text-[12px] font-medium transition-all ${isActive ? "bg-gradient-to-r from-violet-600 to-indigo-600 font-semibold text-white" : "text-slate-500 hover:bg-violet-50 hover:text-violet-700"}`}>
                            <Icon size={17} className="shrink-0"/><span className="min-w-0 flex-1 truncate">{label}</span>
                            {itemModule === "alerts" && <span className="rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-bold text-violet-700">{data.alert_count}</span>}
                        </NavLink>
                    ))}
                </div>)}
            </nav>

            <div className="border-t border-slate-100 p-4">
                <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-3">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-[10px] font-bold text-white">
                        {data.analyst.initials}
                    </div>
                    <div className="min-w-0 flex-1">
                        <p className="truncate text-[11px] font-bold text-slate-800">
                            {data.analyst.name}
                        </p>
                        <p className="mt-0.5 truncate text-[10px] text-slate-400">
                            {data.analyst.role}
                        </p>
                    </div>
                    <ChevronRight size={15} className="shrink-0 text-slate-400" />
                </div>

                <button
                    type="button"
                    onClick={() => {
                        void onLogout();
                    }}
                    className="mt-2 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-[11px] font-medium text-slate-500 transition hover:bg-violet-50 hover:text-violet-700"
                >
                    <LogOut size={16} />
                    Logout
                </button>
            </div>
        </aside>
    );
}

export default function WorkspaceLayout({
    module,
    data,
    error,
    search,
    onSearchChange,
    children,
}: {
    module: string;
    data: WorkspaceResponse;
    error: string;
    search: string;
    onSearchChange: (value: string) => void;
    children: ReactNode;
}) {
    const [mobileNav, setMobileNav] = useState(false);
    const [userMenuOpen, setUserMenuOpen] = useState(false);

    const activeItem = items.find((item) => item.module === module);
    const ActiveIcon = activeItem?.icon ?? LayoutDashboard;

    const {logout } = useAuth() ;
    return (
        <div className="min-h-screen bg-[#f7f7fb] text-slate-900">
            <aside className="fixed inset-y-0 left-0 z-30 hidden w-[236px] lg:flex">
                <Sidebar data={data} onLogout={logout} />
            </aside>

            {mobileNav && (
                <div
                    className="fixed inset-0 z-50 bg-slate-950/30 backdrop-blur-[2px] lg:hidden"
                    onClick={() => setMobileNav(false)}
                >
                    <div
                        className="h-full w-[270px] shadow-2xl"
                        onClick={(event) => event.stopPropagation()}
                    >
                        <Sidebar
                            data={data}
                            onClose={() => setMobileNav(false)}
                            onLogout={logout}
                        />
                    </div>
                </div>
            )}

            <main className="min-h-screen lg:pl-[236px]">
                <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
                    <div className="flex h-[70px] items-center gap-3 px-4 sm:px-6 lg:px-8">
                        <button
                            type="button"
                            className="rounded-lg p-2 text-slate-500 transition hover:bg-violet-50 hover:text-violet-700 lg:hidden"
                            onClick={() => setMobileNav(true)}
                            aria-label="Open navigation"
                        >
                            <Menu size={21} />
                        </button>

                        <div className="hidden items-center gap-2 text-xs text-slate-400 sm:flex">
                            <span>Workspace</span>
                            <ChevronRight size={13} />
                            <span className="font-semibold text-slate-700">
                                {activeItem?.label}
                            </span>
                        </div>

                        <div className="relative ml-auto hidden w-full max-w-[340px] md:block">
                            <Search
                                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                                size={16}
                            />
                            <input
                                value={search}
                                onChange={(event) => onSearchChange(event.target.value)}
                                placeholder="Search customers, alerts, cases..."
                                aria-label="Search workspace"
                                className="h-10 w-full rounded-xl border border-slate-200 bg-slate-50/70 pl-10 pr-4 text-xs text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-violet-300 focus:bg-white focus:ring-4 focus:ring-violet-100"
                            />
                        </div>

                        {data.demo && (
                            <span className="hidden rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 text-[10px] font-bold text-amber-700 sm:inline-flex">
                                Demo data
                            </span>
                        )}

                        <div className="relative">
                            <button
                                type="button"
                                onClick={() => setUserMenuOpen((open) => !open)}
                                aria-label="User profile"
                                aria-expanded={userMenuOpen}
                                className="flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-2.5 transition hover:bg-slate-50"
                            >
                                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-[10px] font-bold text-white">
                                    {data.analyst.initials}
                                </span>
                                <ChevronDown
                                    size={14}
                                    className={`text-slate-400 transition-transform ${
                                        userMenuOpen ? "rotate-180" : ""
                                    }`}
                                />
                            </button>

                            {userMenuOpen && (
                                <div className="absolute right-0 top-12 z-50 w-60 rounded-xl border border-slate-200 bg-white p-2 shadow-[0_15px_40px_rgba(31,24,74,0.12)]">
                                    <div className="border-b border-slate-100 px-3 py-3">
                                        <p className="text-xs font-bold text-slate-800">
                                            {data.analyst.name}
                                        </p>
                                        <p className="mt-1 text-[10px] text-slate-400">
                                            {data.analyst.role}
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>

                    </div>

                    <div className="border-t border-slate-100 px-4 py-2 md:hidden">
                        <div className="relative">
                            <Search
                                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                                size={15}
                            />
                            <input
                                value={search}
                                onChange={(event) => onSearchChange(event.target.value)}
                                placeholder="Search customers, alerts, cases..."
                                aria-label="Search workspace"
                                className="h-9 w-full rounded-xl border border-slate-200 bg-slate-50 pl-9 pr-3 text-xs outline-none focus:border-violet-300 focus:ring-2 focus:ring-violet-100"
                            />
                        </div>
                    </div>
                </header>

                <div className="mx-auto max-w-[1600px] px-4 py-6 sm:px-6 lg:px-8">
                    <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
                        <div className="flex min-w-0 items-center gap-3">
                            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-[0_10px_30px_rgba(109,40,217,0.22)]">
                                <ActiveIcon size={23} />
                            </div>
                            <div className="min-w-0">
                                <h1 className="text-2xl font-black tracking-tight text-slate-950 sm:text-[30px]">
                                    {data.title}
                                </h1>
                                <p className="mt-1 text-xs leading-relaxed text-slate-400 sm:text-sm">
                                    {data.subtitle}
                                </p>
                            </div>
                        </div>

                        <div className="shrink-0 text-[10px] text-slate-400">
                            <span>{data.last_sync}</span>
                            <span className="mx-1.5">·</span>
                            <span>{data.model_version}</span>
                        </div>
                    </div>

                    <div className="mb-5 flex flex-wrap items-center gap-2 rounded-xl border border-violet-100 bg-white px-4 py-3 text-[11px] text-slate-500 shadow-[0_4px_15px_rgba(31,24,74,0.025)]">
                        <span className="h-2 w-2 rounded-full bg-violet-500" />
                        {data.updated_at}
                    </div>

                    {error && (
                        <div
                            role="alert"
                            className="mb-5 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs text-rose-700"
                        >
                            {error}
                        </div>
                    )}

                    {children}

                    <footer className="mt-8 flex flex-col gap-2 border-t border-slate-200 pt-4 text-[10px] text-slate-400 sm:flex-row sm:items-center sm:justify-between">
                        <span>
                            Customer <span className="mx-1">›</span>
                            Intelligence <span className="mx-1">›</span>
                            Risk <span className="mx-1">›</span>
                            Alert <span className="mx-1">›</span>
                            Investigation <span className="mx-1">›</span>
                            Outcome
                        </span>
                        <span className="font-semibold text-violet-600">
                            BET SOFTWARE · Restricted workspace
                        </span>
                    </footer>
                </div>
            </main>
        </div>
    );
}
