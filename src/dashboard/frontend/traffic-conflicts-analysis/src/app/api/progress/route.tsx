import { TRPCError } from "@trpc/server";
import { getHTTPStatusCodeFromError } from "@trpc/server/http";
import { appRouter } from "~/server/api/root";
import { createCallerFactory } from "~/server/api/trpc";

import { db } from "~/server/db";
import { type NextRequest, NextResponse } from "next/server";
import { z } from "zod";

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

const updateProgress = async (req: NextRequest) => {
  const searchParams = req.nextUrl.searchParams;
  const id = z.string().safeParse(searchParams.get("id")).data;

  const progress = z
    .number()
    .safeParse(searchParams.get("progress")).data;

  if (!id) {
    return NextResponse.json(
      { error: { message: "No video id provided" } },
      { status: 400 },
    );
  }

  if (!progress) {
    return NextResponse.json(
      { error: { message: "No progress" } },
      { status: 400 },
    );
  }

  try {
    await caller.video.updateProgress({ videoId: id, progress: progress ?? 0 });
    return NextResponse.json({ data: { available: true } });
  } catch (cause) {
    if (cause instanceof TRPCError) {
      const httpStatusCode = getHTTPStatusCodeFromError(cause);
      return NextResponse.json(
        { error: { message: cause.message } },
        { status: httpStatusCode },
      );
    }
    return NextResponse.json({
      error: { message: "Error while searching updating progress" },
      status: 500,
    });
  }
};

export { updateProgress as POST };
