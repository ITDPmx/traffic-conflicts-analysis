import Link from "next/link";
import { redirect } from 'next/navigation';

import { CreatePost } from "~/app/_components/create-post";
import { getServerAuthSession } from "~/server/auth";
import { api } from "~/trpc/server";

export default async function Home() {
  const session = await getServerAuthSession();
  
  return (
    <div className="flex h-screen w-screen flex-row">
      <p>Test</p>
    </div>
  );
}
