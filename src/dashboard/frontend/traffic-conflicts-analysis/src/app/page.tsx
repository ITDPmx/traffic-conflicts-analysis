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
      <div>
        <main className="flex h-screen w-screen flex-row">
          <div className="flex w-full flex-row px-10 lg:w-1/2">
            <div className="mt-10 flex flex-col gap-y-2 lg:mt-44">
              <h1 className="border-b-4 border-solid border-verde pb-6 font-fira-sans text-2xl font-bold text-gris lg:text-7xl">
                Identificador de conflictos viales
              </h1>
              <p className="pt-4 font-medium text-gray-600 lg:text-lg">
                Herramienta gratuita para identificar conflictos viales mediante
                el análisis de videos capturados por cámaras instaladas en
                intersecciones viales.
              </p>
              <p className="pt-4 font-medium text-gray-600 lg:text-lg">
                Basado en el{" "}
                <span className="underline">
                  Manual de observación de conflictos viales para la prevención
                  de siniestros de tránsito en ciudades de América Latina (ITDP,
                  2024).
                </span>
              </p>
              <div className="lg:hidden flex h-full justify-center mt-6 bg-gray-100 items-center">
                <GoogleButton className="" providers={providers} />
              </div>
              <div className="mb-10 mt-auto">
                <p className="mt-12 font-medium text-gray-600 lg:text-lg">
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
                  través de este{" "}
                  <a
                    className="underline"
                    href="mailto:berenice.perez@itdp.org"
                  >
                    mail
                  </a>
                  .
                </p>
              </div>
            </div>
          </div>

          <div
            className="hidden w-1/2 border-l-[20px] border-verde bg-black bg-cover bg-center lg:block"
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
