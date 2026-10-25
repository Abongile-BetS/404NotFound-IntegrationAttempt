import type { ReactNode } from "react";

import RiskEnginePanel from "./RiskEnginePanel";

interface AuthLayoutProps {
  children: ReactNode;
}

function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <main className="min-h-screen bg-[#f4f1fb] p-4 sm:p-6 lg:p-8">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] w-full max-w-[1400px] overflow-hidden rounded-3xl bg-white shadow-2xl shadow-purple-900/10 sm:min-h-[calc(100vh-3rem)] lg:min-h-[calc(100vh-4rem)]">
        <section className="flex w-full flex-col justify-center lg:w-1/2">
          {children}
        </section>
        <RiskEnginePanel />
      </div>
    </main>
  );
}

export default AuthLayout;
