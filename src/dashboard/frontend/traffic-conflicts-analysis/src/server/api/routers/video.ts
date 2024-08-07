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
  getUserVideosIds: protectedProcedure.query(async ({ ctx }) => {
    return await ctx.db.video.findMany({
      where: {
        userId: ctx.session.user.id,
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
});
