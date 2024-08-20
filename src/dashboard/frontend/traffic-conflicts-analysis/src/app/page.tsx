import { getProviders } from "next-auth/react";

import {
  GetProviderLink,
  SignInButtons,
  GoogleButton,
} from "~/app/_components/signin-buttons";
import { RedirectDashboard } from "~/app/_components/redirect-dashboard";
import { getServerAuthSession } from "~/server/auth";

export default async function Home() {
  const session = await getServerAuthSession();
  const providers = await getProviders();

  return (
    <>
      <div className="hidden md:block">
        <main className="flex h-screen w-screen flex-row">
          <div className="flex w-1/2 flex-row px-10">
            <div className="mt-44 flex flex-col gap-y-2">
              <h1 className="border-b-4 border-solid border-verde font-fira-sans pb-6 text-7xl font-bold text-gris">
                Identificador de conflictos viales
              </h1>
              <p className="pt-4 text-lg font-medium text-gray-600">
                Herramienta gratuita para identificar conflictos viales mediante
                el análisis de videos capturados por cámaras instaladas en
                intersecciones viales.
              </p>
              <p className="pt-4 text-lg font-medium text-gray-600">
                Basado en el <span className="underline">Manual de observación de conflictos viales para la
                prevención de siniestros de tránsito en ciudades de América
                Latina (ITDP, 2024).</span>
              </p>
              <div className="mb-10 mt-auto">
                <p className="mt-12 text-lg font-medium text-gray-600">
                  Una colaboración de:
                </p>
                <div className="mt-4 flex space-x-4">
                  <img
                    src="/ITDP_logo_completo.png"
                    alt="ITDP Logo"
                    className="w-[27%] object-contain"
                  />
                  <img
                    src="/TEC_logo_completo.png"
                    alt="Tec Logo"
                    className="h-auto w-[30%] object-contain"
                  />
                  <img
                    src="/FIA_logo_completo.png"
                    alt="FIA Foundation Logo"
                    className="h-auto w-[35%] object-contain"
                  />
                </div>
                <p className="mt-12 text-center text-sm text-gray-600">
                  Si tienes alguna duda o comentario, no dudes en contactarnos a
                  través de este <a className="underline" href="mailto:berenice.perez@itdp.org">mail</a>.
                </p>
              </div>
            </div>
          </div>

          <div
            className="w-1/2 bg-black bg-cover bg-center border-l-[20px] border-verde"
            style={{ backgroundImage: `url('/Portada.png')` }}
          >
            <div className="flex h-full justify-center">
              <GoogleButton className="mt-[80%]" providers={providers} />
            </div>
          </div>
        </main>
        <RedirectDashboard session={session} />
      </div>
    </>
  );
}
