"use client";

import type { Session } from "next-auth";
import { redirect, usePathname } from "next/navigation";

export const RedirectDashboard = ({session}: {session: Session | null}) => {
    const pathname = usePathname();  

    if (session && pathname === '/'){
        redirect('/test');
    }
  return (
    <>
    </>
  );
};
