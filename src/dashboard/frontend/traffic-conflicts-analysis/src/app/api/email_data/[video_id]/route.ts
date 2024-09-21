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

const emailData = async (
  req: NextRequest,
  { params }: { params: { video_id: string } },
) => {
  const { video_id } = params;
  const idProcessed = z.string().safeParse(video_id).data;

  if (!idProcessed) {
    return NextResponse.json(
      { error: { message: "No video id provided" } },
      { status: 400 },
    );
  }

  try {
    const emailInfo = await caller.video.getEmailDataByVideoId({
      videoId: idProcessed,
    });
    return NextResponse.json({ data: { emailInfo } });
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

export { emailData as GET };
