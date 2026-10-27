import {
    createContext,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from "react";

import keycloak from "./keycloak";

interface AuthContextValue {
    initialized: boolean;
    authenticated: boolean;
    token?: string;
    username?: string;
    roles: string[];
    login: () => Promise<void>;
    logout: () => Promise<void>;
    register: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
    children: ReactNode;
}

let keycloakInitPromise: Promise<boolean> | null = null;

function initializeKeycloak() {
    if (!keycloakInitPromise) {
        keycloakInitPromise = keycloak.init({
            onLoad: "check-sso",
            silentCheckSsoRedirectUri: `${window.location.origin}/silent-check-sso.html`,
            pkceMethod: "S256",
            checkLoginIframe: false,
        });
    }

    return keycloakInitPromise;
}

export function AuthProvider({ children }: AuthProviderProps) {
    const devAuthBypass =
        import.meta.env.VITE_DEV_AUTH_BYPASS === "true";

    const [initialized, setInitialized] = useState(devAuthBypass);
    const [authenticated, setAuthenticated] = useState(devAuthBypass);
    const [token, setToken] = useState<string | undefined>(
        devAuthBypass ? "dev-token" : undefined,
    );
    const [username, setUsername] = useState<string | undefined>(
        devAuthBypass ? "dev" : undefined,
    );
    const [roles, setRoles] = useState<string[]>(
        devAuthBypass ? ["admin", "analyst", "manager"] : [],
    );

    useEffect(() => {
        if (devAuthBypass) {
            return;
        }

        keycloak.onTokenExpired = () => {
            keycloak
                .updateToken(30)
                .then(() => setToken(keycloak.token))
                .catch(() => undefined);
        };
        keycloak.onAuthRefreshSuccess = () => {
            setToken(keycloak.token);
        };

        let mounted = true;

        initializeKeycloak()
            .then((isAuthenticated) => {
                if (!mounted) return;

                setAuthenticated(isAuthenticated);

                if (isAuthenticated) {
                    setToken(keycloak.token);
                    setUsername(
                        keycloak.tokenParsed?.preferred_username,
                    );

                    setRoles(
                        keycloak.tokenParsed?.realm_access?.roles ?? [],
                    );
                }

                setInitialized(true);
            })
            .catch((error) => {
                console.error(
                    "Keycloak initialization failed:",
                    error,
                );

                if (mounted) {
                    setInitialized(true);
                }
            });

        return () => {
            mounted = false;
        };
    }, [devAuthBypass]);

    async function login() {
        if (devAuthBypass) {
            setAuthenticated(true);
            return;
        }
        await keycloak.login({
            redirectUri:
                window.location.origin + "/dashboard",
        });
    }
    async function register() {
        if (devAuthBypass) {
            setAuthenticated(true);
            return;
        }
        await keycloak.register({
            redirectUri: window.location.origin + "/dashboard",
        });
    }

    async function logout() {
        if (devAuthBypass) {
            setAuthenticated(false);
            return;
        }
        await keycloak.logout({
            redirectUri:
                window.location.origin + "/login",
        });
    }

    return (
        <AuthContext.Provider
            value={{
                initialized,
                authenticated,
                token,
                username,
                roles,
                register,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error(
            "useAuth must be used inside AuthProvider",
        );
    }

    return context;
}