import { TRPCError } from "@trpc/server";
import { getHTTPStatusCodeFromError } from "@trpc/server/http";
import { appRouter } from "~/server/api/root";
import { createCallerFactory } from "~/server/api/trpc";

import { db } from "~/server/db";
import type { NextApiRequest, NextApiResponse } from "next";
import {z} from "zod"

type ResponseData = {
  data?: {
    available: boolean;
  };
  error?: {
    message: string;
  };
};

const createCaller = createCallerFactory(appRouter);

const caller = createCaller({
    db: db,
    session: {
        expires: "",
        user: {
            id: "1",
            role: "ADMIN"
        }
    },
    headers: null
});

const updateProgress = async (
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>
) => {
  const id = req.query.id as string;
  const progress = z.number().safeParse(req.query.progress as string).data;

  if (!id) {
    res.status(400).json({ error: { message: "No video id provided" } });
  }

  if (!progress){
    res.status(400).json({ error: { message: "No progress" } });
  }

  try {
    await caller.video.updateProgress({ videoId: id, progress: progress ?? 0 });

    res.status(200).json({data: {available: true}});
  } catch (cause) {
    if (cause instanceof TRPCError) {
      const httpStatusCode = getHTTPStatusCodeFromError(cause);

      res.status(httpStatusCode).json({ error: { message: cause.message } });
    }
    res.status(500).json({
      error: { message: `Error while searching updating progress of ${id}` },
    });
  }
};

export default updateProgress;
