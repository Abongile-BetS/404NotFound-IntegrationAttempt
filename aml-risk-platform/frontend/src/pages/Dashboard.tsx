import {
  AlertTriangle,
  ArrowUpRight,
  BarChart3,
  Bell,
  CalendarDays,
  ChevronDown,
  ChevronRight,
  CircleCheck,
  ClipboardCheck,
  FileCheck2,
  FileSearch,
  FolderKanban,
  Gauge,
  LayoutDashboard,
  LogOut,
  Menu,
  MoreVertical,
  Search,
  Settings,
  ShieldCheck,
  UserCheck,
  Users,
  X,
} from "lucide-react";

import type { LucideIcon } from "lucide-react";

import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { useEffect, useMemo, useState, type ReactNode } from "react";

import { NavLink, useNavigate } from "react-router-dom";
import { getDashboardData, type DashboardResponse } from "../services/api";

type NavItem = {
  label: string;
  icon: typeof LayoutDashboard;
  badge?: string;
  expandable?: boolean;
};

const navItems: NavItem[] = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Customers",
    icon: Users,
  },
  {
    label: "Screening",
    icon: ShieldCheck,
  },
  {
    label: "Alerts",
    icon: Bell,
    badge: "37",
  },
  {
    label: "Investigations",
    icon: FolderKanban,
  },
  {
    label: "Reports",
    icon: BarChart3,
  },
  {
    label: "Administration",
    icon: Settings,
    expandable: true,
  },
];

const kpiIcons: Record<string, LucideIcon> = {
  "Total Customers": Users,
  "KYC Pending": FileCheck2,
  "Verified Customers": CircleCheck,
  "Requires Action": AlertTriangle,
};

const documentTypeColors = [
  "bg-violet-500",
  "bg-indigo-500",
  "bg-amber-400",
  "bg-pink-400",
];

const cx = (...classes: Array<string | false | undefined>) =>
  classes.filter(Boolean).join(" ");

function MiniSparkline({
  points,
  stroke,
}: {
  points: number[];
  stroke: string;
}) {
  const max = Math.max(...points);
  const min = Math.min(...points);

  const width = 120;
  const height = 44;

  const path = points
    .map((point, index) => {
      const x = (index / (points.length - 1)) * width;

      const y = height - ((point - min) / Math.max(max - min, 1)) * 32 - 6;

      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  const gradientId = `spark-${stroke.replace("#", "")}`;

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="h-12 w-28"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={gradientId} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={stroke} stopOpacity="0.22" />
          <stop offset="100%" stopColor={stroke} stopOpacity="0" />
        </linearGradient>
      </defs>

      <path
        d={`${path} L ${width} ${height} L 0 ${height} Z`}
        fill={`url(#${gradientId})`}
      />

      <path
        d={path}
        fill="none"
        stroke={stroke}
        strokeWidth="2.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    Verified: "bg-emerald-50 text-emerald-700 ring-emerald-100",
    "Under Review": "bg-amber-50 text-amber-700 ring-amber-100",
    "Requires Action": "bg-pink-50 text-pink-700 ring-pink-100",
    Pending: "bg-violet-50 text-violet-700 ring-violet-100",
  };

  return (
    <span
      className={cx(
        "inline-flex items-center rounded-full px-3 py-1 text-[11px] font-semibold ring-1",
        styles[status] ?? "bg-slate-50 text-slate-600 ring-slate-100",
      )}
    >
      {status}
    </span>
  );
}

function Panel({
  title,
  subtitle,
  children,
  className,
  action = "View All",
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
  action?: string;
}) {
  return (
    <section
      className={cx(
        "overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-[0_10px_35px_rgba(31,24,74,0.055)]",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-4 px-5 pb-3 pt-5">
        <div className="flex min-w-0 items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-violet-50 text-violet-600">
            <ShieldCheck size={18} />
          </div>

          <div>
            <h2 className="text-[15px] font-bold text-slate-900">{title}</h2>

            {subtitle && (
              <p className="mt-0.5 text-[11px] text-slate-400">{subtitle}</p>
            )}
          </div>
        </div>

        {action && (
          <button
            type="button"
            className="flex shrink-0 items-center gap-1 text-[11px] font-bold text-violet-600 hover:text-violet-800"
          >
            {action}
            <ChevronRight size={13} />
          </button>
        )}
      </div>

      {children}
    </section>
  );
}

export function KycDashboard() {
  const [mobileNav, setMobileNav] = useState(false);
  const [query, setQuery] = useState("");
  const [period, setPeriod] = useState("Last 30 Days");
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [apiError, setApiError] = useState("");

  useEffect(() => {
    getDashboardData()
      .then(setDashboardData)
      .catch((error: unknown) => {
        setApiError(error instanceof Error ? error.message : "Unable to load dashboard data");
      });
  }, []);

  const filteredActivity = useMemo(
    () =>
      (dashboardData?.activity ?? []).filter((row) =>
        [row.id, row.name, row.status, row.date, row.time]
          .join(" ")
          .toLowerCase()
          .includes(query.toLowerCase()),
      ),
    [dashboardData, query],
  );
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#f7f7fb] text-slate-900">
      {/* Desktop sidebar */}

      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[236px] border-r border-slate-200 bg-white lg:flex lg:flex-col">
        <div className="flex h-[82px] items-center gap-3 border-b border-slate-100 px-6">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 via-indigo-500 to-purple-700 text-white shadow-[0_8px_25px_rgba(109,40,217,0.28)]">
            <ShieldCheck size={24} strokeWidth={2.4} />
          </div>

          <div>
            <div className="text-[19px] font-black tracking-tight text-slate-950">
              BET
            </div>

            <div className="-mt-1 text-[9px] font-bold tracking-[0.18em] text-violet-600">
              SOFTWARE
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-5">
          {navItems.map((item) => {
            const Icon = item.icon;

            if (item.expandable) {
              return (
                <button
                  type="button"
                  key={item.label}
                  className="group flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-[13px] font-bold text-slate-500 transition hover:bg-violet-50 hover:text-violet-700"
                >
                  <Icon size={18} />

                  <span className="flex-1">{item.label}</span>

                  <ChevronRight size={15} />
                </button>
              );
            }

            const pathMap: Record<string, string> = {
              Dashboard: "/dashboard",
              Customers: "/customers",
              Screening: "/screening",
              Alerts: "/alerts",
              Investigations: "/investigations",
              Reports: "/reports",
            };

            const path = pathMap[item.label] ?? "/dashboard";

            return (
              <NavLink
                key={item.label}
                to={path}
                end
                className={({ isActive }) =>
                  cx(
                    "group flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-[13px] font-medium transition",
                    isActive
                      ? "bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-[0_8px_22px_rgba(109,40,217,0.24)]"
                      : "text-slate-500 hover:bg-violet-50 hover:text-violet-700",
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon size={18} />

                    <span className="flex-1">{item.label}</span>

                    {item.badge && (
                      <span
                        className={cx(
                          "rounded-full px-2 py-0.5 text-[10px] font-bold",
                          isActive
                            ? "bg-white/20 text-white"
                            : "bg-violet-100 text-violet-700",
                        )}
                      >
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
        <div className="border-t border-slate-100 p-4">
          <div className="mb-3 flex items-center gap-3 rounded-xl bg-slate-50 p-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-xs font-bold text-white">
              NG
            </div>

            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-bold text-slate-800">
                Ntsika Gqokoma
              </p>

              <p className="truncate text-[10px] text-slate-400">
                Compliance Analyst
              </p>
            </div>

            <ChevronRight size={15} className="text-slate-400 font-bold" />
          </div>

          <button
            type="button"
            className="flex w-full items-center gap-3 px-2 py-2 text-xs font-medium text-slate-500 hover:text-violet-600"
          >
            <LogOut size={17} />
            Logout
          </button>
        </div>
      </aside>

      {/* Mobile navigation */}

      {mobileNav && (
        <div
          className="fixed inset-0 z-50 bg-slate-950/30 lg:hidden"
          onClick={() => setMobileNav(false)}
        >
          <div
            className="h-full w-[270px] bg-white p-4 shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="mb-6 flex items-center justify-between">
              <span className="font-black">BET SOFTWARE</span>

              <button
                type="button"
                onClick={() => setMobileNav(false)}
                aria-label="Close navigation"
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;

                return (
                  <button
                    type="button"
                    key={item.label}
                    className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm text-slate-600 hover:bg-violet-50 hover:text-violet-700"
                  >
                    <Icon size={18} />
                    {item.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      <main className="min-h-screen lg:pl-[236px]">
        {/* Top bar */}

        <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
          <div className="flex h-[70px] items-center gap-3 px-4 sm:px-6 lg:px-8">
            <button
              type="button"
              className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
              onClick={() => setMobileNav(true)}
              aria-label="Open navigation"
            >
              <Menu size={21} />
            </button>

            <div className="relative hidden max-w-[420px] flex-1 md:block">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                size={17}
              />

              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search customers, alerts, investigations..."
                className="h-10 w-full rounded-xl border border-slate-200 bg-slate-50/70 pl-10 pr-4 text-xs outline-none transition focus:border-violet-300 focus:bg-white focus:ring-4 focus:ring-violet-100"
              />
            </div>

            <div className="ml-auto flex items-center gap-2">
              <div className="relative">
                <CalendarDays
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-violet-500"
                  size={15}
                />

                <select
                  value={period}
                  onChange={(event) => setPeriod(event.target.value)}
                  className="h-10 appearance-none rounded-xl border border-slate-200 bg-white pl-9 pr-8 text-xs font-semibold text-slate-700 outline-none focus:border-violet-300"
                >
                  <option>Last 30 Days</option>
                  <option>Last 7 Days</option>
                  <option>Last 90 Days</option>
                </select>

                <ChevronDown
                  className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400"
                  size={14}
                />
              </div>

              <div className="relative">
                <button
                  type="button"
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-2.5 hover:bg-slate-50"
                  aria-label="User menu"
                  aria-expanded={isUserMenuOpen}
                >
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-[10px] font-bold text-white">
                    NG
                  </span>

                  <ChevronDown
                    size={14}
                    className={`text-slate-400 transition-transform duration-200 ${
                      isUserMenuOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>

                {isUserMenuOpen && (
                  <div className="absolute right-0 top-12 z-50 w-56 rounded-xl border border-slate-200 bg-white p-2 shadow-lg">
                    <button
                      type="button"
                      onClick={() => {
                        setIsUserMenuOpen(false);
                        navigate("/account");
                      }}
                      className="flex w-full items-center rounded-lg px-3 py-2.5 text-left text-sm font-medium text-slate-700 hover:bg-violet-50 hover:text-violet-700"
                    >
                      Account Details
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-[1600px] px-4 py-6 sm:px-6 lg:px-8">
          {/* Page heading */}

          <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <div className="mb-2 flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-[0_10px_30px_rgba(109,40,217,0.22)]">
                  <ShieldCheck size={23} />
                </div>

                <div>
                  <h1 className="text-2xl font-black tracking-tight text-slate-950 sm:text-[30px]">
                    KYC Dashboard
                  </h1>

                  <p className="text-xs text-slate-400 sm:text-sm">
                    Monitor customer verification status and KYC compliance
                    across all customers.
                  </p>
                </div>
              </div>
            </div>
            {apiError && (
              <p role="alert" className="text-sm text-red-600">
                Dashboard API unavailable: {apiError}
              </p>
            )}
          </div>

          {/* KPI row */}

          <div className="mb-5 flex flex-wrap gap-4">
            {(dashboardData?.kpis ?? []).map((item) => {
              const Icon = kpiIcons[item.label] ?? Gauge;

              const iconClass =
                item.tone === "purple"
                  ? "bg-violet-50 text-violet-600"
                  : item.tone === "pink"
                    ? "bg-pink-50 text-pink-500"
                    : item.tone === "blue"
                      ? "bg-indigo-50 text-indigo-600"
                      : "bg-amber-50 text-amber-500";

              const stroke =
                item.tone === "purple"
                  ? "#7c3aed"
                  : item.tone === "pink"
                    ? "#ec4899"
                    : item.tone === "blue"
                      ? "#2563eb"
                      : "#f59e0b";

              return (
                <div
                  key={item.label}
                  className="min-w-[220px] flex-1 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_10px_30px_rgba(31,24,74,0.05)]"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div
                      className={cx(
                        "flex h-10 w-10 items-center justify-center rounded-xl",
                        iconClass,
                      )}
                    >
                      <Icon size={20} />
                    </div>

                    <MiniSparkline points={item.points} stroke={stroke} />
                  </div>

                  <p className="mt-4 text-xs font-medium text-slate-500">
                    {item.label}
                  </p>

                  <div className="mt-1 flex items-end justify-between gap-3">
                    <p className="text-2xl font-black tracking-tight text-slate-900">
                      {item.value}
                    </p>

                    <span
                      className={cx(
                        "flex items-center text-[11px] font-bold",
                        item.positive ? "text-emerald-500" : "text-pink-500",
                      )}
                    >
                      <ArrowUpRight size={20} />
                      {item.change}
                    </span>
                  </div>

                  <p className="mt-1 text-[10px] text-slate-400">
                    vs. previous 30 days
                  </p>
                </div>
              );
            })}
          </div>

          {/* Main row */}

          <div className="flex flex-col gap-5 xl:flex-row">
            {/* KYC Verification Queue */}

            <Panel
              title="KYC Verification Queue"
              subtitle="Reviews requiring compliance attention"
              className="min-w-0 flex-[1.08]"
            >
              <div className="space-y-3 px-5 pb-5">
                {(dashboardData?.verification_queue ?? []).map((item) => {
                  const Icon = item.verification.includes("Identity")
                    ? UserCheck
                    : item.verification.includes("address")
                      ? FileCheck2
                      : item.verification.includes("Enhanced")
                        ? ShieldCheck
                        : FileSearch;

                  const iconTone =
                    item.tone === "red"
                      ? "bg-red-50 text-red-500"
                      : "bg-amber-50 text-amber-500";

                  const priorityTone =
                    item.priority === "High"
                      ? "bg-red-50 text-red-600"
                      : "bg-amber-50 text-amber-600";

                  return (
                    <button
                      type="button"
                      key={item.customer}
                      className="flex w-full items-center gap-3 rounded-xl border border-slate-100 bg-slate-50/60 p-3 text-left transition hover:border-violet-100 hover:bg-violet-50/50"
                    >
                      <div
                        className={cx(
                          "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
                          iconTone,
                        )}
                      >
                        <Icon size={18} strokeWidth={1.8} />
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-3">
                          <div className="min-w-0">
                            <p className="truncate text-xs font-bold text-slate-800">
                              {item.name}
                            </p>

                            <p className="mt-0.5 text-[10px] text-slate-400">
                              {item.customer}
                            </p>
                          </div>

                          <span
                            className={cx(
                              "shrink-0 rounded-full px-2.5 py-1 text-[10px] font-semibold",
                              priorityTone,
                            )}
                          >
                            {item.priority}
                          </span>
                        </div>

                        <div className="mt-2 flex items-center justify-between gap-3">
                          <p className="truncate text-[11px] font-medium text-slate-500">
                            {item.verification}
                          </p>

                          <span className="shrink-0 text-[10px] text-slate-400">
                            {item.waiting}
                          </span>
                        </div>
                      </div>

                      <ChevronRight
                        size={15}
                        className="shrink-0 text-slate-300 font-bold"
                      />
                    </button>
                  );
                })}
              </div>
            </Panel>

            {/* Recent KYC Activity */}

            <Panel
              title="Recent Activity"
              subtitle="Latest verification changes"
              className="min-w-0 flex-1"
            >
              <div className="overflow-x-auto px-4 pb-4">
                <table className="w-full min-w-[620px] border-separate border-spacing-0 text-left">
                  <thead>
                    <tr className="bg-slate-50 text-[10px] uppercase tracking-wide text-slate-400">
                      <th className="rounded-l-lg px-3 py-3 font-semibold">
                        Customer
                      </th>

                      <th className="px-3 py-3 font-semibold">Name</th>

                      <th className="px-3 py-3 font-semibold">Status</th>

                      <th className="px-3 py-3 font-semibold">Updated</th>

                      <th className="rounded-r-lg px-3 py-3 text-right font-semibold">
                        Action
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredActivity.map((row) => (
                      <tr key={row.id} className="border-b border-slate-100">
                        <td className="px-3 py-3 text-[11px] font-bold text-slate-800">
                          {row.id}
                        </td>

                        <td className="px-3 py-3 text-[11px] text-slate-500">
                          {row.name}
                        </td>

                        <td className="px-3 py-3">
                          <StatusBadge status={row.status} />
                        </td>

                        <td className="px-3 py-3 text-[10px] text-slate-400">
                          <div>{row.date}</div>
                          <div>{row.time}</div>
                        </td>

                        <td className="px-3 py-3 text-right">
                          <button
                            type="button"
                            className="text-[11px] font-semibold text-violet-600 hover:text-violet-800"
                          >
                            View
                          </button>

                          <button
                            type="button"
                            className="ml-3 text-slate-400 hover:text-slate-700"
                            aria-label={`More options for ${row.id}`}
                          >
                            <MoreVertical size={15} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Panel>
          </div>

          {/* Bottom row */}

          <div className="mt-5 flex flex-col gap-5 xl:flex-row">
            {/* KYC Verification Trends */}

            <Panel
              title="KYC Verification Trends"
              subtitle="Verification activity over the selected period"
              className="min-w-0 flex-[1.1]"
              action={period}
            >
              <div className="px-4 pb-5 pt-2">
                <div className="h-[275px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={dashboardData?.trend ?? []}
                      margin={{
                        top: 10,
                        right: 10,
                        bottom: 0,
                        left: -18,
                      }}
                    >
                      <XAxis
                        dataKey="day"
                        tick={{
                          fill: "#94a3b8",
                          fontSize: 10,
                        }}
                        axisLine={false}
                        tickLine={false}
                      />

                      <YAxis
                        tick={{
                          fill: "#94a3b8",
                          fontSize: 10,
                        }}
                        axisLine={false}
                        tickLine={false}
                      />

                      <Tooltip
                        contentStyle={{
                          borderRadius: 12,
                          border: "1px solid #e2e8f0",
                          boxShadow: "0 8px 24px rgba(15,23,42,.08)",
                          fontSize: 11,
                        }}
                      />

                      <Line
                        type="monotone"
                        dataKey="verified"
                        stroke="#14b8a6"
                        strokeWidth={3}
                        dot={false}
                      />

                      <Line
                        type="monotone"
                        dataKey="pending"
                        stroke="#f59e0b"
                        strokeWidth={2.5}
                        dot={false}
                      />

                      <Line
                        type="monotone"
                        dataKey="action"
                        stroke="#ec4899"
                        strokeWidth={2.5}
                        dot={false}
                      />

                      <Line
                        type="monotone"
                        dataKey="started"
                        stroke="#8b5cf6"
                        strokeWidth={2.5}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div className="flex flex-wrap gap-x-5 gap-y-2 px-2 text-[10px] font-medium text-slate-500">
                  <span className="flex items-center gap-2">
                    <i className="h-2 w-2 rounded-full bg-teal-500" />
                    Verified
                  </span>

                  <span className="flex items-center gap-2">
                    <i className="h-2 w-2 rounded-full bg-amber-400" />
                    Pending
                  </span>

                  <span className="flex items-center gap-2">
                    <i className="h-2 w-2 rounded-full bg-pink-500" />
                    Requires Action
                  </span>

                  <span className="flex items-center gap-2">
                    <i className="h-2 w-2 rounded-full bg-violet-500" />
                    Not Started
                  </span>
                </div>
              </div>
            </Panel>

            {/* KYC Compliance by Document Type */}

            <Panel
              title="KYC Compliance by Document Type"
              subtitle="Verification completion rates"
              className="min-w-0 flex-1"
            >
              <div className="space-y-5 px-5 pb-7 pt-3">
                {(dashboardData?.document_types ?? []).map(({ name, value }, index) => {
                  const color = documentTypeColors[index] ?? "bg-slate-400";
                  return (
                  <div key={name}>
                    <div className="mb-2 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div
                          className={cx(
                            "flex h-7 w-7 items-center justify-center rounded-lg text-white",
                            color,
                          )}
                        >
                          {index === 0 ? (
                            <FileCheck2 size={14} />
                          ) : index === 1 ? (
                            <FileSearch size={14} />
                          ) : index === 2 ? (
                            <ClipboardCheck size={14} />
                          ) : (
                            <UserCheck size={14} />
                          )}
                        </div>

                        <span className="text-xs font-semibold text-slate-600">
                          {name}
                        </span>
                      </div>

                      <span className="text-xs font-bold text-slate-700">
                        {value}
                      </span>
                    </div>

                    <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className={cx("h-full rounded-full", color)}
                        style={{
                          width: value,
                        }}
                      />
                    </div>
                  </div>
                  );
                })}
              </div>
            </Panel>

            {/* Compliance Actions */}

            <Panel
              title="Compliance Actions"
              subtitle="What needs attention today"
              className="min-w-0 flex-[0.72]"
              action=""
            >
              <div className="space-y-3 px-5 pb-5">
                {[
                  {
                    title: "Review pending KYC",
                    detail: "342 customers",
                    tone: "bg-amber-50 text-amber-600",
                    Icon: FileCheck2,
                  },
                  {
                    title: "Resolve KYC exceptions",
                    detail: "612 customers",
                    tone: "bg-pink-50 text-pink-600",
                    Icon: AlertTriangle,
                  },
                  {
                    title: "Run screening review",
                    detail: "37 alerts",
                    tone: "bg-violet-50 text-violet-600",
                    Icon: ShieldCheck,
                  },
                ].map(
                  (action: {
                    title: string;
                    detail: string;
                    tone: string;
                    Icon: LucideIcon;
                  }) => {
                    const ActionIcon = action.Icon;

                    return (
                      <button
                        type="button"
                        key={action.title}
                        className="flex w-full items-center gap-3 rounded-xl border border-slate-100 bg-slate-50/60 p-3 text-left transition hover:border-violet-100 hover:bg-violet-50/50"
                      >
                        <span
                          className={cx(
                            "flex h-9 w-9 shrink-0 items-center justify-center rounded-xl",
                            action.tone,
                          )}
                        >
                          <ActionIcon size={17} />
                        </span>

                        <span className="min-w-0 flex-1">
                          <span className="block text-xs font-bold text-slate-700">
                            {action.title}
                          </span>

                          <span className="mt-0.5 block text-[10px] text-slate-400">
                            {action.detail}
                          </span>
                        </span>

                        <ChevronRight
                          size={15}
                          className="text-slate-400 font-bold"
                        />
                      </button>
                    );
                  },
                )}
              </div>
            </Panel>
          </div>

          {/* Footer banner */}

          <div className="mt-5 overflow-hidden rounded-2xl bg-gradient-to-r from-violet-700 via-indigo-600 to-violet-700 p-5 text-white shadow-[0_12px_35px_rgba(79,70,229,0.2)]">
            <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/15 backdrop-blur">
                  <Gauge size={22} />
                </div>

                <div>
                  <p className="text-sm font-bold">Stay ahead of KYC risk.</p>

                  <p className="text-[11px] text-white/70">
                    Real-time verification monitoring, clear evidence and faster
                    compliance decisions.
                  </p>
                </div>
              </div>

              <button
                type="button"
                className="flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-xs font-bold text-violet-700 shadow-sm hover:bg-violet-50"
              >
                View KYC Guidelines
                <ChevronRight size={15} />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
