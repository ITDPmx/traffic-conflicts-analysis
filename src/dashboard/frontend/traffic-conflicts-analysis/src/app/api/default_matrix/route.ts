import { z } from "zod";
import type { NextRequest } from "next/server";

import { appRouter } from "~/server/api/root";
import { db } from "~/server/db";

import { createCallerFactory } from "~/server/api/trpc";


const createCaller = createCallerFactory(appRouter);

const caller = createCaller({
    db: db,
    session: {
      expires: "",
      user: {
        id: "1",
        role: "ADMIN",
      },
    },
    headers: null,
  });


const usesDefaultMatrix = async (req: NextRequest) => {
  const searchParams = req.nextUrl.searchParams;
  const id = z.string().safeParse(searchParams.get("id")).data;

  if (!id) {
    return Response.json(
      { error: { message: "Missing video ID" } },
      { status: 400 },
    );
  }

  const defaultMatrix = await caller.video.videoUsesDefaultMatrix({ videoId: id });
  return Response.json({ data: { usesDefaultMatrix: defaultMatrix } });
};

export { usesDefaultMatrix as GET };
