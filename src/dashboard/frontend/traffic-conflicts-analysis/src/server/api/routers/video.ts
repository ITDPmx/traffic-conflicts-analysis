import { z } from "zod";
import { env } from "~/env";

import {
  createTRPCRouter,
  protectedProcedure,
  publicProcedure,
  memberProcedure,
  adminProcedure,
} from "~/server/api/trpc";

import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import path from "path";

const VIDEO_DIR = "videos";

// Create an S3 client service object
const expiration = 3600; // The expiration time of the presigned URL (in seconds)
const s3Client = new S3Client({
  region: env.AWS_REGION,
  credentials: {
    accessKeyId: env.AWS_ACCESS_KEY_ID,
    secretAccessKey: env.AWS_SECRET_ACCESS_KEY,
  },
});

export const videoRouter = createTRPCRouter({
  getUserVideosIds: protectedProcedure.query(async ({ ctx }) => {
    return await ctx.db.video.findMany({
      where: {
        id: ctx.session.user.id,
      },
      select: {
        id: true,
      },
    });
  }),
  getUserVideosById: protectedProcedure

    .input(z.object({ videoId: z.string() }))
    .query(async ({ ctx, input }) => {
      return await ctx.db.video.findUnique({
        where: {
          id: input.videoId,
        },
        select: {
          id: true,
        },
      });
    }),
  getSignedUrl: protectedProcedure
  .input(z.object({ name: z.string() }))
  .mutation(async ({ input }) => {
    const now = new Date();
    const finalName = `${input.name.split(".")[0] + now.toISOString()}.mp4`;
    return await generatePresignedUrl({ name: finalName });
  }),
});

const generatePresignedUrl = async ({ name }: { name: string }) => {
  const command = new PutObjectCommand({
    Bucket: env.AWS_BUCKET_NAME,
    Key: path.join(VIDEO_DIR, name)
  });
  try {
    const url = await getSignedUrl(s3Client, command, {
      expiresIn: expiration,
    });
    return url;
  } catch (err) {
    console.error("Error generating presigned URL", err);
  }
  return "";
};
