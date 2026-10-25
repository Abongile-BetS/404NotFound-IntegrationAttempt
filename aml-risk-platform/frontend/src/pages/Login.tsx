import { Link } from "react-router-dom";

import AuthLayout from "../components/auth/AuthLayout";
import AuthLogo from "../components/auth/AuthLogo";
import { useAuth } from "../services/AuthProvider";

function Login() {
  const { login } = useAuth();

  return (
    <AuthLayout>
      <div className="mx-auto w-full max-w-xl px-6 py-10 sm:px-10 lg:px-14 xl:px-20">
        <div className="mb-10">
          <AuthLogo />
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Welcome Back
          </h1>

          <p className="mt-3 text-sm leading-6 text-gray-500">
            Sign in to your account to access your AML and KYC risk management
            platform.
          </p>
        </div>

        <div className="space-y-5">
          <button
            type="button"
            onClick={login}
            className="flex h-12 w-full items-center justify-center rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-sm font-semibold text-white shadow-lg shadow-purple-500/20 transition hover:from-violet-700 hover:to-indigo-700 focus:outline-none focus:ring-4 focus:ring-purple-500/20"
          >
            Sign In
          </button>
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            Don't have an account?{" "}
            <Link
              to="/register"
              className="font-semibold text-purple-600 hover:text-purple-700"
            >
              Create an account
            </Link>
          </p>
        </div>

        <p className="mt-10 text-center text-xs text-gray-400">
          © 2026 BET SOFTWARE. All rights reserved.
        </p>
      </div>
    </AuthLayout>
  );
}

export default Login;
