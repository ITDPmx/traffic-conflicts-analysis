import { redirect } from "next/navigation";
import { getServerAuthSession } from "~/server/auth";

import { Navbar } from "~/app/_components/navbar";

export const metadata = {
  title: "Identificador de Conflictos Viales",
  description: "TCA - ITDP - TEC",
  icons: [{ rel: "icon", url: "/favicon-32x32.png" }],
};

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // If the user is not authenticated, redirect to the home page
  const session = await getServerAuthSession();

  if (!session) {
    redirect("/");
  }

  return (
    <>
      <Navbar role={session.user.role}/>
      <div className="mt-20">{children}</div>
    </>
  );
}
