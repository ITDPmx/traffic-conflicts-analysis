
import { getServerAuthSession } from "~/server/auth";
import { db } from "~/server/db";

export const hasAccess = async (videoId: string): Promise<boolean> => {
  const session = await getServerAuthSession();

  if (!session?.user) {
    return false;
  }

  const exists = session?.user.role === "ADMIN" ? await db.video.findUnique({
    where: { id: videoId },
    select: { id: true },
  }) : await db.video.findUnique({
    where: { id: videoId, userId: session.user.id },
    select: { id: true },
  });

  return exists?.id === videoId;
}