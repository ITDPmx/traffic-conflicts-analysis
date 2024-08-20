"use client";

import {
  type ClientSafeProvider,
  type LiteralUnion,
  signIn,
} from "next-auth/react";
import { type BuiltInProviderType } from "next-auth/providers/index";
import { twMerge } from "tailwind-merge";

export const SignInButtons = ({
  providers,
}: {
  providers: Record<
    LiteralUnion<BuiltInProviderType, string>,
    ClientSafeProvider
  > | null;
}) => {
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

export const GetProviderLink = ({
  name,
  providers,
}: {
  name: string;
  providers: Record<
    LiteralUnion<BuiltInProviderType, string>,
    ClientSafeProvider
  > | null;
}) => {
  if (!providers) {
    return null;
  }

  const provider = Object.values(providers).find(
    (provider) => provider.name === name,
  );

  if (!provider) {
    return null;
  }

  return provider.id;
};

export const GoogleButton = ({
  providers,
  className
}: {
  className?: string,
  providers: Record<
    LiteralUnion<BuiltInProviderType, string>,
    ClientSafeProvider
  > | null;
}) => {
  const googleLink = GetProviderLink({ name: "Google", providers });

  return (
    <button
      className={twMerge("flex h-14 items-center space-x-2 rounded-sm bg-white px-14 py-3 font-semibold text-gray-800 shadow-md", className)}
      onClick={() => signIn(googleLink ?? "")}
    >
      <img src="/google_logo.png" alt="Google Logo" className="h-5" />
      <span className="text-xl">Sign in with Google</span>
    </button>
  );
};
