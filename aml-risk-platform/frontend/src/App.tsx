import { lazy, Suspense } from "react";
import {
    BrowserRouter,
    Navigate,
    Outlet,
    Route,
    Routes,
} from "react-router-dom";
import { useAuth } from "./services/AuthProvider";

const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const DashboardHome = lazy(() => import("./pages/DashboardHome"));
const RiskScreening = lazy(() => import("./pages/RiskScreening"));
const TransactionMonitoring = lazy(
    () => import("./pages/TransactionMonitoring"),
);
const KycMonitoring = lazy(() => import("./pages/KycMonitoring"));
const NetworkIntelligence = lazy(
    () => import("./pages/NetworkIntelligence"),
);
const AlertQueue = lazy(() => import("./pages/AlertQueue"));
const InvestigationWorkspace = lazy(
    () => import("./pages/InvestigationWorkspace"),
);
const ExecutiveDashboard = lazy(
    () => import("./pages/ExecutiveDashboard"),
);

function NotFoundRedirect() {
    const { authenticated } = useAuth();

    return (
        <Navigate
            to={authenticated ? "/dashboard" : "/login"}
            replace
        />
    );
}

function RequireAuth() {
    const { initialized, authenticated } = useAuth();

    if (!initialized) {
        return (
            <main
                className="p-6 text-sm text-slate-600"
                role="status"
                aria-live="polite"
            >
                Checking your session...
            </main>
        );
    }
    if (!authenticated) {
        return <Navigate to="/login" replace />;
    }
    return <Outlet />;
}

function App() {
    return (
        <BrowserRouter>
            <Suspense
                fallback={
                    <main
                        className="p-6 text-sm text-slate-600"
                        role="status"
                        aria-live="polite"
                    >
                        Loading page...
                    </main>
                }
            >
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route element={<RequireAuth />}>
                        <Route
                            path="/"
                            element={<Navigate to="/dashboard" replace />}
                        />
                        <Route
                            path="/dashboard"
                            element={<DashboardHome />}
                        />
                        <Route
                            path="/screening"
                            element={<RiskScreening />}
                        />
                        <Route
                            path="/transactions"
                            element={<TransactionMonitoring />}
                        />
                        <Route path="/kyc" element={<KycMonitoring />} />
                        <Route
                            path="/network"
                            element={<NetworkIntelligence />}
                        />
                        <Route path="/alerts" element={<AlertQueue />} />
                        <Route
                            path="/investigations"
                            element={<InvestigationWorkspace />}
                        />
                        <Route
                            path="/executive"
                            element={<ExecutiveDashboard />}
                        />
                        <Route
                            path="/intelligence/aml"
                            element={<Navigate to="/transactions" replace />}
                        />
                        <Route
                            path="/intelligence/kyc"
                            element={<Navigate to="/kyc" replace />}
                        />
                        <Route
                            path="/intelligence/media"
                            element={<Navigate to="/screening" replace />}
                        />
                        <Route
                            path="/intelligence/screening"
                            element={<Navigate to="/screening" replace />}
                        />
                        <Route
                            path="/intelligence/network"
                            element={<Navigate to="/network" replace />}
                        />
                        <Route
                            path="/intelligence/rules"
                            element={
                                <Navigate to="/investigations" replace />
                            }
                        />
                        <Route
                            path="/intelligence/risk"
                            element={
                                <Navigate to="/investigations" replace />
                            }
                        />
                        <Route
                            path="/intelligence/geography"
                            element={<Navigate to="/executive" replace />}
                        />
                        <Route
                            path="/intelligence/reports"
                            element={<Navigate to="/executive" replace />}
                        />
                    </Route>
                    <Route
                        path="*"
                        element={<NotFoundRedirect />}
                    />
                </Routes>
            </Suspense>
        </BrowserRouter>
    );
}

export default App;