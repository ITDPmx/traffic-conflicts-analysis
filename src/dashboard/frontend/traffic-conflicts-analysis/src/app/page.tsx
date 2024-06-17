import Link from "next/link";
import { redirect } from 'next/navigation';

import { CreatePost } from "~/app/_components/create-post";
import { getServerAuthSession } from "~/server/auth";
import { api } from "~/trpc/server";

export default async function Home() {
  const session = await getServerAuthSession();
  
  return (
    <main className="flex h-screen w-screen flex-row">
      <div className="w-full bg-[url('/Interseccion.png')] bg-cover">
        <div className="flex flex-col items-center justify-around h-full">
          <h1 className="text-white text-8xl text-center font-semibold">Ciudades Inteligentes</h1>
          <div className="flex flex-row gap-x-24">
            <img
              src="/TEC_Logo.png"
              alt="Logo"
              className="h-56 w-auto"
            />
            <img
              src="/ITDP_Logo.png"
              alt="Logo"
              className="h-56 w-auto"
            />
          </div>
        </div>
      </div>

      <div className="w-full">
      <div className="flex flex-col items-center justify-around h-full">
          <h1 className="text-black text-8xl text-center font-semibold mx-28">Inicio de sesión</h1>
          <div className="flex flex-col gap-y-6">
            <Link
              href={session ? "/api/auth/signout" : "/api/auth/signin"}
              className="text-3xl font-bold  bg-azul p-8 rounded-3xl text-white"
            >
              {session ? "Sign out" : "Ingresar con OAuth"}
            </Link>
            <p className="text-center text-xl text-gray-400">
              Analiza tus videos en minutos
            </p>
          </div>
        </div>

      </div>
    </main>
  );
}
