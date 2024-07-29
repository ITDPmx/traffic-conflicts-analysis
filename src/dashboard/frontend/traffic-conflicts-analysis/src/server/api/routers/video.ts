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
  region: env.IAWS_REGION,
  credentials: {
    accessKeyId: env.IAWS_ACCESS_KEY_ID,
    secretAccessKey: env.IAWS_SECRET_ACCESS_KEY,
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
  .input(z.object({ name: z.string(), duration: z.number() }))
  .mutation(async ({ ctx, input }) => {

    const video = await ctx.db.video.create({
      data: {
        name: input.name,
        progress: 0,
        duration: input.duration,
        user: {
          connect: {
            id: ctx.session.user.id,
          },
        },
      },
    });

    const extension = input.name.split(".").at(-1);

    const finalName = `${video.id}.${extension}`;
    
    return await generatePresignedUrl({ name: finalName });
  }),

  updateProgress: adminProcedure
    .input(z.object({ videoId: z.string(), progress: z.number() }))
    .mutation(async ({ ctx, input }) => {
      return await ctx.db.video.update({
        where: {
          id: input.videoId,
        },
        data: {
          progress: input.progress,
        },
      });
    }),
  
});

const generatePresignedUrl = async ({ name }: { name: string }) => {
  const command = new PutObjectCommand({
    Bucket: env.IAWS_BUCKET_NAME,
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
