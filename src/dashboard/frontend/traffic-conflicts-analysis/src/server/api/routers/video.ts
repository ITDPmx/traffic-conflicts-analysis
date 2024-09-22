import { z } from "zod";

import {
  createTRPCRouter,
  protectedProcedure,
  publicProcedure,
  memberProcedure,
  adminProcedure,
} from "~/server/api/trpc";

import { generatePutPresignedUrl } from "~/server/utils/aws";

export const videoRouter = createTRPCRouter({
  getUserVideosIds: protectedProcedure
  .input(z.object({ userId: z.string() }))
  .query(async ({ ctx, input }) => {

    if (input.userId !== ctx.session.user.id && ctx.session.user.role !== "ADMIN") {
      return [];
    }

    return await ctx.db.video.findMany({
      where: {
        userId: input.userId,
      },
      select: {
        id: true,
      },
      orderBy: {
        createdAt: "desc",
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
      const finalName = `videos/${video.id}.${extension}`;

      return await generatePutPresignedUrl({ fileName: finalName });
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

  videoExists: adminProcedure
    .input(z.object({ videoId: z.string() }))
    .query(async ({ ctx, input }) => {
      return await ctx.db.video.findUnique({
        where: {
          id: input.videoId,
        },
      });
    }),

    getLastVideo: protectedProcedure
    .query(async ({ ctx }) => {
      return await ctx.db.video.findFirst({
        where: {
          userId: ctx.session.user.id,
        },
        orderBy: {
          createdAt: "desc",
        },
      });
    }),
    getEmailDataByVideoId: adminProcedure
    .input(z.object({ videoId: z.string() }))
    .query(async ({ ctx, input }) => {
      return await ctx.db.video.findUnique({
        where: {
          id: input.videoId,
        },
        select: {
          user: {
            select: {
              email: true,
              name: true,
            },
          },
          name: true,
          createdAt: true,
        }
      });
    }),
});
