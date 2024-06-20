"use client";

import { ClientSafeProvider, LiteralUnion, signIn } from "next-auth/react";
import { BuiltInProviderType } from "next-auth/providers/index";

export const SignInButtons = ({
  providers,
}: {
  providers: Record<
    LiteralUnion<BuiltInProviderType, string>,
    ClientSafeProvider
  > | null;
}) => {
  console.log(providers);

  if (!providers) {
    return <></>;
  }

  return (
    <>
      {Object.values(providers).map((provider) => (
        <button
          className="rounded-3xl bg-azul p-8 text-2xl font-bold text-white"
          key={provider.id}
          onClick={() => signIn(provider.id)}
        >
          Iniciar sesión con {provider.name}
        </button>
      ))}
    </>
  );
};
