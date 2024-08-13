import { getProviders } from "next-auth/react";

import { SignInButtons } from "~/app/_components/signin-buttons";
import { RedirectDashboard } from "~/app/_components/redirect-dashboard";
import { getServerAuthSession } from "~/server/auth";

export default async function Home() {
  const session = await getServerAuthSession();
  const providers = await getProviders();

  return (
    <main className="flex h-screen w-screen flex-row">
      <div className="w-full bg-[url('/Interseccion.png')] bg-cover">
        <div className="flex h-full flex-col items-center justify-around">
          <h1 className="text-center text-8xl font-semibold text-white">
            Analítica de Conflictos Viales
          </h1>
          <div className="flex flex-col items-center">
            <img src="/FIAF_Logo.png" alt="Logo" className="h-40 w-auto" />

            <div className="flex flex-row gap-x-24">
              <img src="/TEC_Logo.png" alt="Logo" className="h-40 w-auto" />
              <img src="/ITDP_Logo.png" alt="Logo" className="h-40 w-auto" />
            </div>
          </div>
        </div>
      </div>

      <div className="w-full">
        <div className="flex h-full flex-col items-center justify-around">
          <h1 className="mx-28 text-center text-8xl font-semibold text-black">
            Inicio de sesión
          </h1>
          <div className="flex flex-col gap-y-6">
            <SignInButtons providers={providers} />
            <p className="text-center text-xl text-gray-400">
              Analiza tus videos en minutos
            </p>
          </div>
        </div>
      </div>
      <RedirectDashboard session={session} />
    </main>
  );
}
