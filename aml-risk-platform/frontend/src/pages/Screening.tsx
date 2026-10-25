import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Bell,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  CircleAlert,
  FileSearch,
  Gauge,
  LayoutDashboard,
  LogOut,
  Menu,
  MoreVertical,
  Search,
  Settings,
  ShieldAlert,
  ShieldCheck,
  UserCheck,
  Users,
  X,
} from "lucide-react";

import {
  Area,
  AreaChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  NavLink,
} from "react-router-dom";

import {
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { LucideIcon } from "lucide-react";
import { getScreeningDashboard, type ScreeningDashboardResponse } from "../services/api";

type NavItem = {
  label: string;
  icon: LucideIcon;
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
    icon: ShieldAlert,
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

const screeningKpiIcons: Record<string, LucideIcon> = {
  "Total Screened": ShieldCheck,
  "Potential Matches": CircleAlert,
  Cleared: CheckCircle2,
  Escalated: AlertTriangle,
};

const breakdownColors: Record<string, string> = {
  "No Match": "#14b8a6",
  "Potential Match": "#f59e0b",
  "Confirmed Match": "#ef4444",
  "Under Review": "#8b5cf6",
};

const sourcePresentation: Record<string, { icon: LucideIcon; color: string; iconColor: string }> = {
  Sanctions: { icon: ShieldAlert, color: "bg-red-500", iconColor: "bg-red-50 text-red-500" },
  PEP: { icon: Users, color: "bg-amber-400", iconColor: "bg-amber-50 text-amber-500" },
  "Adverse Media": { icon: FileSearch, color: "bg-violet-500", iconColor: "bg-violet-50 text-violet-600" },
  "Law Enforcement": { icon: ShieldCheck, color: "bg-indigo-500", iconColor: "bg-indigo-50 text-indigo-600" },
  "Other Watchlists": { icon: AlertTriangle, color: "bg-pink-500", iconColor: "bg-pink-50 text-pink-500" },
};

const screeningQueueIcons: Record<string, LucideIcon> = {
  "Potential sanctions match": ShieldAlert,
  "PEP matches detected": UserCheck,
  "Adverse media review": FileSearch,
};

const cx = (
  ...classes: Array<string | false | undefined>
) => classes.filter(Boolean).join(" ");

function ScreeningStatus({
  status,
}: {
  status: string;
}) {
  const styles: Record<string, string> = {
    Clear:
      "bg-emerald-50 text-emerald-700 ring-emerald-100",
    "Potential Match":
      "bg-amber-50 text-amber-700 ring-amber-100",
    Escalated:
      "bg-red-50 text-red-700 ring-red-100",
    "Under Review":
      "bg-violet-50 text-violet-700 ring-violet-100",
  };

  return (
    <span
      className={cx(
        "inline-flex rounded-full px-3 py-1 text-[10px] font-semibold ring-1",
        styles[status] ??
          "bg-slate-50 text-slate-600 ring-slate-100",
      )}
    >
      {status}
    </span>
  );
}

function ScreeningPanel({
  title,
  subtitle,
  children,
  className,
  action = "View all",
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
            <h2 className="text-[15px] font-bold text-slate-900">
              {title}
            </h2>

            {subtitle && (
              <p className="mt-0.5 text-[11px] text-slate-400">
                {subtitle}
              </p>
            )}
          </div>
        </div>

        {action && (
          <button
            type="button"
            className="flex shrink-0 items-center gap-1 text-[11px] font-semibold text-violet-600 hover:text-violet-800"
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

function Sidebar({
  mobile = false,
  onClose,
}: {
  mobile?: boolean;
  onClose?: () => void;
}) {
  return (
    <div className="flex h-full flex-col bg-white">
      <div className="flex h-[82px] items-center gap-3 border-b border-slate-100 px-6">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 via-indigo-500 to-purple-700 text-white shadow-[0_8px_25px_rgba(109,40,217,0.28)]">
          <ShieldCheck
            size={24}
            strokeWidth={2.4}
          />
        </div>

        <div>
          <div className="text-[19px] font-black tracking-tight text-slate-950">
            BET
          </div>

          <div className="-mt-1 text-[9px] font-bold tracking-[0.18em] text-violet-600">
            SOFTWARE
          </div>
        </div>

        {mobile && (
          <button
            type="button"
            onClick={onClose}
            className="ml-auto rounded-lg p-2 text-slate-500 hover:bg-slate-100"
            aria-label="Close navigation"
          >
            <X size={19} />
          </button>
        )}
      </div>

      <nav className="flex-1 space-y-1 px-3 py-5">
        {navItems.map((item) => {
            const Icon = item.icon;

            if (item.expandable) {
                return (
                <button
                    type="button"
                    key={item.label}
                    className="group flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-[13px] font-medium text-slate-500 transition hover:bg-violet-50 hover:text-violet-700"
                >
                    <Icon size={18} />

                    <span className="flex-1">
                    {item.label}
                    </span>

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

                    <span className="flex-1">
                        {item.label}
                    </span>

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

          <ChevronRight
            size={15}
            className="text-slate-400"
          />
        </div>

        <button
          type="button"
          className="flex w-full items-center gap-3 px-2 py-2 text-xs font-medium text-slate-500 hover:text-violet-600"
        >
          <LogOut size={17} />
          Logout
        </button>
      </div>
    </div>
  );
}

export function ScreeningDashboard() {
  const [mobileNav, setMobileNav] = useState(false);
  const [query, setQuery] = useState("");
  const [period, setPeriod] =
    useState("Last 30 Days");
  const [screeningData, setScreeningData] = useState<ScreeningDashboardResponse | null>(null);
  const [apiError, setApiError] = useState("");

  useEffect(() => {
    getScreeningDashboard()
      .then(setScreeningData)
      .catch((error: unknown) => {
        setApiError(error instanceof Error ? error.message : "Unable to load screening results");
      });
  }, []);

  const filteredResults = useMemo(
  () =>
    (screeningData?.results ?? []).filter((row) =>
      [
        row.id,
        row.customer,
        row.customerId,
        row.source,
        row.status,
        row.score,
        row.time,
      ]
        .join(" ")
        .toLowerCase()
        .includes(query.toLowerCase()),
    ),
  [query, screeningData],
);

  return (
    <div className="min-h-screen bg-[#f7f7fb] text-slate-900">
      {/* Desktop sidebar */}

      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[236px] border-r border-slate-200 bg-white lg:flex lg:flex-col">
        <Sidebar />
      </aside>

      {/* Mobile sidebar */}

      {mobileNav && (
        <div
          className="fixed inset-0 z-50 bg-slate-950/30 lg:hidden"
          onClick={() => setMobileNav(false)}
        >
          <div
            className="h-full w-[270px] bg-white shadow-2xl"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <Sidebar
              mobile
              onClose={() => setMobileNav(false)}
            />
          </div>
        </div>
      )}

      <main className="min-h-screen lg:pl-[236px]">
        {/* Header */}

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
                onChange={(event) =>
                  setQuery(event.target.value)
                }
                placeholder="Search customers, screening results..."
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
                  onChange={(event) =>
                    setPeriod(event.target.value)
                  }
                  className="h-10 appearance-none rounded-xl border border-slate-200 bg-white pl-9 pr-8 text-xs font-semibold text-slate-700 outline-none focus:border-violet-300"
                >
                  <option>
                    Last 30 Days
                  </option>
                  <option>
                    Last 7 Days
                  </option>
                  <option>
                    Last 90 Days
                  </option>
                </select>

                <ChevronDown
                  className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400"
                  size={14}
                />
              </div>

              <button
                type="button"
                className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-500 hover:text-violet-600"
                aria-label="Notifications"
              >
                <Bell size={17} />

                <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-pink-500 px-1 text-[9px] font-bold text-white">
                  3
                </span>
              </button>

              <button
                type="button"
                className="flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-2.5"
                aria-label="User menu"
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-[10px] font-bold text-white">
                  NG
                </span>

                <ChevronDown
                  size={14}
                  className="text-slate-400"
                />
              </button>
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-[1600px] px-4 py-6 sm:px-6 lg:px-8">
          {/* Heading */}

          <div className="mb-6">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-[0_10px_30px_rgba(109,40,217,0.22)]">
                <ShieldCheck size={23} />
              </div>

              <div>
                <h1 className="text-2xl font-black tracking-tight text-slate-950 sm:text-[30px]">
                  AML Screening Dashboard
                </h1>

                <p className="text-xs text-slate-400 sm:text-sm">
                  Monitor sanctions, PEP, adverse media and watchlist screening activity.
                </p>
              </div>
            </div>
            {apiError && (
              <p role="alert" className="mt-3 text-sm text-red-600">
                Screening API unavailable: {apiError}
              </p>
            )}
          </div>

          {/* KPI Cards */}

          <div className="mb-5 flex flex-wrap gap-4">
            {(screeningData?.kpis ?? []).map((item) => {
              const Icon = screeningKpiIcons[item.label] ?? ShieldCheck;

              const iconClass =
                item.tone === "purple"
                  ? "bg-violet-50 text-violet-600"
                  : item.tone === "pink"
                    ? "bg-pink-50 text-pink-500"
                    : item.tone === "blue"
                      ? "bg-indigo-50 text-indigo-600"
                      : "bg-amber-50 text-amber-500";

              return (
                <div
                  key={item.label}
                  className="min-w-[220px] flex-1 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-[0_10px_30px_rgba(31,24,74,0.05)]"
                >
                  <div className="flex items-start justify-between">
                    <div
                      className={cx(
                        "flex h-10 w-10 items-center justify-center rounded-xl",
                        iconClass,
                      )}
                    >
                      <Icon size={19} />
                    </div>

                    <BarChart3
                      size={22}
                      className="text-slate-200"
                    />
                  </div>

                  <p className="mt-4 text-xs font-medium text-slate-500">
                    {item.label}
                  </p>

                  <div className="mt-1 flex items-end justify-between">
                    <p className="text-2xl font-black tracking-tight text-slate-900">
                      {item.value}
                    </p>

                    <span
                      className={cx(
                        "flex items-center text-[11px] font-bold",
                        item.positive
                          ? "text-emerald-500"
                          : "text-pink-500",
                      )}
                    >
                      {item.positive ? (
                        <ArrowUpRight size={14} />
                      ) : (
                        <ArrowDownRight size={14} />
                      )}

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

          {/* Charts */}

          <div className="mb-5 flex flex-col gap-5 xl:flex-row">
            {/* Screening activity */}

            <ScreeningPanel
              title="Screening Activity"
              subtitle="Screening volume and potential matches"
              className="min-w-0 flex-[1.4]"
              action={period}
            >
              <div className="px-4 pb-5">
                <div className="h-[285px]">
                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >
                    <AreaChart
                      data={screeningData?.trend ?? []}
                      margin={{
                        top: 10,
                        right: 10,
                        left: -20,
                        bottom: 0,
                      }}
                    >
                      <defs>
                        <linearGradient
                          id="screenedGradient"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stopColor="#7c3aed"
                            stopOpacity={0.28}
                          />

                          <stop
                            offset="100%"
                            stopColor="#7c3aed"
                            stopOpacity={0.02}
                          />
                        </linearGradient>

                        <linearGradient
                          id="matchGradient"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stopColor="#ec4899"
                            stopOpacity={0.2}
                          />

                          <stop
                            offset="100%"
                            stopColor="#ec4899"
                            stopOpacity={0.01}
                          />
                        </linearGradient>
                      </defs>

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
                          border:
                            "1px solid #e2e8f0",
                          boxShadow:
                            "0 8px 24px rgba(15,23,42,.08)",
                          fontSize: 11,
                        }}
                      />

                      <Area
                        type="monotone"
                        dataKey="screened"
                        stroke="#7c3aed"
                        strokeWidth={3}
                        fill="url(#screenedGradient)"
                      />

                      <Area
                        type="monotone"
                        dataKey="matches"
                        stroke="#ec4899"
                        strokeWidth={2.5}
                        fill="url(#matchGradient)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                <div className="flex gap-6 px-2 text-[10px] font-medium text-slate-500">
                  <span className="flex items-center gap-2">
                    <i className="h-2 w-2 rounded-full bg-violet-600" />
                    Customers Screened
                  </span>

                  <span className="flex items-center gap-2">
                    <i className="h-2 w-2 rounded-full bg-pink-500" />
                    Potential Matches
                  </span>
                </div>
              </div>
            </ScreeningPanel>

            {/* Match breakdown */}

            <ScreeningPanel
              title="Screening Match Breakdown"
              subtitle="Current screening outcomes"
              className="min-w-0 flex-1"
              action=""
            >
              <div className="flex flex-col items-center px-5 pb-5 sm:flex-row">
                <div className="h-[235px] w-full sm:w-[52%]">
                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >
                    <PieChart>
                      <Pie
                        data={(screeningData?.breakdown ?? []).map((item) => ({
                          ...item,
                          color: breakdownColors[item.name] ?? "#94a3b8",
                        }))}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={58}
                        outerRadius={88}
                        paddingAngle={3}
                        stroke="none"
                      >
                        {(screeningData?.breakdown ?? []).map(
                          (entry) => (
                            <Cell
                              key={entry.name}
                              fill={breakdownColors[entry.name] ?? "#94a3b8"}
                            />
                          ),
                        )}
                      </Pie>

                      <Tooltip
                        contentStyle={{
                          borderRadius: 12,
                          border:
                            "1px solid #e2e8f0",
                          fontSize: 11,
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="w-full space-y-4 sm:w-[48%]">
                  {(screeningData?.breakdown ?? []).map(
                    (item) => (
                      <div
                        key={item.name}
                        className="flex items-center justify-between gap-3"
                      >
                        <div className="flex items-center gap-2">
                          <span
                            className="h-2.5 w-2.5 rounded-full"
                            style={{
                              backgroundColor:
                                breakdownColors[item.name] ?? "#94a3b8",
                            }}
                          />

                          <span className="text-[11px] text-slate-500">
                            {item.name}
                          </span>
                        </div>

                        <span className="text-[11px] font-bold text-slate-700">
                          {item.value.toLocaleString()}
                        </span>
                      </div>
                    ),
                  )}
                </div>
              </div>
            </ScreeningPanel>
          </div>

          {/* Watchlists + Recent results */}

          <div className="mb-5 flex flex-col gap-5 xl:flex-row">
            {/* Watchlist sources */}

            <ScreeningPanel
              title="Watchlist Match Sources"
              subtitle="Where potential matches are being detected"
              className="min-w-0 flex-[0.75]"
            >
              <div className="space-y-4 px-5 pb-5">
                {(screeningData?.sources ?? []).map(
                  (item) => {
                    const presentation = sourcePresentation[item.name];
                    const Icon = presentation?.icon ?? ShieldCheck;

                    return (
                      <div key={item.name}>
                        <div className="mb-2 flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span
                              className={cx(
                                "flex h-8 w-8 items-center justify-center rounded-lg",
                                presentation?.iconColor,
                              )}
                            >
                              <Icon size={15} />
                            </span>

                            <span className="text-xs font-semibold text-slate-600">
                              {item.name}
                            </span>
                          </div>

                          <span className="text-xs font-bold text-slate-700">
                            {item.matches}
                          </span>
                        </div>

                        <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                          <div
                            className={cx(
                              "h-full rounded-full",
                              presentation?.color,
                            )}
                            style={{
                              width: `${item.percentage}%`,
                            }}
                          />
                        </div>
                      </div>
                    );
                  },
                )}
              </div>
            </ScreeningPanel>

            {/* Recent screening results */}

            <ScreeningPanel
              title="Recent Screening Results"
              subtitle="Latest AML screening activity"
              className="min-w-0 flex-[1.4]"
            >
              <div className="overflow-x-auto px-4 pb-4">
                <table className="w-full min-w-[700px] border-separate border-spacing-0 text-left">
                  <thead>
                    <tr className="bg-slate-50 text-[10px] uppercase tracking-wide text-slate-400">
                      <th className="rounded-l-lg px-3 py-3 font-semibold">
                        Screening
                      </th>

                      <th className="px-3 py-3 font-semibold">
                        Customer
                      </th>

                      <th className="px-3 py-3 font-semibold">
                        Source
                      </th>

                      <th className="px-3 py-3 font-semibold">
                        Risk
                      </th>

                      <th className="px-3 py-3 font-semibold">
                        Status
                      </th>

                      <th className="rounded-r-lg px-3 py-3 text-right font-semibold">
                        Action
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredResults.map(
                      (row) => (
                        <tr
                          key={row.id}
                          className="border-b border-slate-100"
                        >
                          <td className="px-3 py-3">
                            <p className="text-[11px] font-bold text-slate-800">
                              {row.id}
                            </p>

                            <p className="mt-0.5 text-[9px] text-slate-400">
                              {row.time ?? "—"}
                            </p>
                          </td>

                          <td className="px-3 py-3">
                            <p className="text-[11px] font-semibold text-slate-700">
                              {row.customer}
                            </p>

                            <p className="mt-0.5 text-[9px] text-slate-400">
                              {row.customerId}
                            </p>
                          </td>

                          <td className="px-3 py-3 text-[11px] text-slate-500">
                            {row.source ?? "—"}
                          </td>

                          <td className="px-3 py-3">
                            <span
                              className={cx(
                                "text-[11px] font-bold",
                                Number(
                                  (row.score ?? "").replace(
                                    "%",
                                    "",
                                  ),
                                ) >= 75
                                  ? "text-red-500"
                                  : Number(
                                        (row.score ?? "").replace(
                                          "%",
                                          "",
                                        ),
                                      ) >= 50
                                    ? "text-amber-500"
                                    : "text-emerald-500",
                              )}
                            >
                              {row.score ?? "—"}
                            </span>
                          </td>

                          <td className="px-3 py-3">
                            <ScreeningStatus
                              status={row.status ?? "Unknown"}
                            />
                          </td>

                          <td className="px-3 py-3 text-right">
                            <button
                              type="button"
                              className="text-[11px] font-semibold text-violet-600 hover:text-violet-800"
                            >
                              Review
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
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            </ScreeningPanel>
          </div>

          {/* Operational section */}

          <div className="flex flex-col gap-5 xl:flex-row">
            {/* Screening Queue */}

            <ScreeningPanel
              title="Screening Queue"
              subtitle="Items requiring compliance attention"
              className="min-w-0 flex-[1.1]"
            >
              <div className="space-y-3 px-5 pb-5">
                {(screeningData?.queue ?? []).map(
                  (item) => {
                    const Icon = screeningQueueIcons[item.title] ?? AlertTriangle;

                    const iconTone =
                      item.tone === "red"
                        ? "bg-red-50 text-red-500"
                        : item.tone === "amber"
                          ? "bg-amber-50 text-amber-500"
                          : "bg-violet-50 text-violet-600";

                    const priorityTone =
                      item.priority === "High"
                        ? "bg-red-50 text-red-600"
                        : "bg-amber-50 text-amber-600";

                    return (
                      <button
                        type="button"
                        key={item.title}
                        className="flex w-full items-center gap-3 rounded-xl border border-slate-100 bg-slate-50/60 p-3 text-left transition hover:border-violet-100 hover:bg-violet-50/50"
                      >
                        <div
                          className={cx(
                            "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
                            iconTone,
                          )}
                        >
                          <Icon size={18} />
                        </div>

                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between gap-3">
                            <p className="truncate text-xs font-bold text-slate-800">
                              {item.title}
                            </p>

                            <span
                              className={cx(
                                "shrink-0 rounded-full px-2.5 py-1 text-[10px] font-semibold",
                                priorityTone,
                              )}
                            >
                              {item.priority}
                            </span>
                          </div>

                          <p className="mt-1 text-[11px] text-slate-400">
                            {item.detail}
                          </p>
                        </div>

                        <ChevronRight
                          size={15}
                          className="shrink-0 text-slate-300"
                        />
                      </button>
                    );
                  },
                )}
              </div>
            </ScreeningPanel>

            {/* Screening performance */}

            <ScreeningPanel
              title="Screening Performance"
              subtitle="Current operational metrics"
              className="min-w-0 flex-1"
              action=""
            >
              <div className="grid grid-cols-2 gap-3 px-5 pb-5">
                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-violet-50 text-violet-600">
                    <Gauge size={16} />
                  </div>

                  <p className="text-[10px] text-slate-400">
                    Avg. Screening Time
                  </p>

                  <p className="mt-1 text-xl font-black text-slate-900">
                    1.8s
                  </p>

                  <p className="mt-1 text-[10px] font-semibold text-emerald-500">
                    ↓ 12% faster
                  </p>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                    <CheckCircle2 size={16} />
                  </div>

                  <p className="text-[10px] text-slate-400">
                    Auto-Clear Rate
                  </p>

                  <p className="mt-1 text-xl font-black text-slate-900">
                    97.6%
                  </p>

                  <p className="mt-1 text-[10px] font-semibold text-emerald-500">
                    ↑ 2.4% this month
                  </p>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-pink-50 text-pink-500">
                    <AlertTriangle size={16} />
                  </div>

                  <p className="text-[10px] text-slate-400">
                    False Positive Rate
                  </p>

                  <p className="mt-1 text-xl font-black text-slate-900">
                    3.1%
                  </p>

                  <p className="mt-1 text-[10px] font-semibold text-emerald-500">
                    ↓ 0.8% this month
                  </p>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                    <ShieldCheck size={16} />
                  </div>

                  <p className="text-[10px] text-slate-400">
                    Screening Coverage
                  </p>

                  <p className="mt-1 text-xl font-black text-slate-900">
                    99.8%
                  </p>

                  <p className="mt-1 text-[10px] font-semibold text-emerald-500">
                    ↑ 0.6% this month
                  </p>
                </div>
              </div>
            </ScreeningPanel>
          </div>

          {/* Footer */}

          <div className="mt-5 overflow-hidden rounded-2xl bg-gradient-to-r from-violet-700 via-indigo-600 to-violet-700 p-5 text-white shadow-[0_12px_35px_rgba(79,70,229,0.2)]">
            <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/15 backdrop-blur">
                  <ShieldCheck size={22} />
                </div>

                <div>
                  <p className="text-sm font-bold">
                    AML screening is operating normally.
                  </p>

                  <p className="text-[11px] text-white/70">
                    All configured watchlists are available and screening coverage is currently at 99.8%.
                  </p>
                </div>
              </div>

              <button
                type="button"
                className="flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-xs font-bold text-violet-700 shadow-sm hover:bg-violet-50"
              >
                Screening Configuration
                <ChevronRight size={15} />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default ScreeningDashboard;