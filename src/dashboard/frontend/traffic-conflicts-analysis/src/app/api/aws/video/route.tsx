import { generateGetPresignedUrl } from "~/server/utils/aws";
import { db } from "~/server/db";
import { getServerAuthSession } from "~/server/auth";

import { z } from "zod";
import type { NextRequest } from "next/server";

const getUrl = async (req: NextRequest) => {
  const searchParams = req.nextUrl.searchParams;
  const id = z.string().safeParse(searchParams.get("id")).data;

  const session = await getServerAuthSession();

  if (!session?.user) {
    return Response.json(
      { error: { message: "Unauthorized" } },
      { status: 401 },
    );
  }

  if (!id) {
    return Response.json(
      { error: { message: "No video id provided" } },
      { status: 400 },
    );
  }

  let exists = null;
  if (session?.user.role === "ADMIN") {
    exists = await db.video.findUnique({ where: { id }, select: { id: true } });
  } else {
    exists = await db.video.findUnique({
      where: { id: id, userId: session?.user.id ?? "" },
      select: { id: true },
    });
  }

  if (!exists) {
    return Response.json(
      { error: { message: `Video with id ${id} not found` } },
      { status: 404 },
    );
  }

  const filename = `${id}.mp4`;

  const location = await generateGetPresignedUrl({ fileName: filename });

  if (!location) {
    return Response.json(
      { error: { message: "Error getting presigned URL" } },
      { status: 500 },
    );
  }

  return Response.redirect(location);
};

export { getUrl as GET };
