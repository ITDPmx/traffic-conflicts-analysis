import { z } from "zod";

import {
  createTRPCRouter,
  protectedProcedure,
  publicProcedure,
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
    .input(z.object({ name: z.string(), duration: z.number(), defaultMatrix: z.boolean() }))
    .mutation(async ({ ctx, input }) => {
      
      const lastVideo = await ctx.db.video.findFirst({
        where: {
          userId: ctx.session.user.id,
        },
        orderBy: {
          createdAt: "desc",
        },
      });

      const currentTime = new Date().getTime();

      if (lastVideo && currentTime - lastVideo.createdAt.getTime() < 1000 * 60 * 5) {
        throw new Error("Tienes que esperar por lo menos 5 minutos para subir otro video");
      }

      const video = await ctx.db.video.create({
        data: {
          name: input.name,
          progress: 10,
          duration: input.duration,
          defaultMatrix: input.defaultMatrix,
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

  videoUsesDefaultMatrix: publicProcedure
    .input(z.object({ videoId: z.string() }))
    .query(async ({ ctx, input }) => {
      const data = await ctx.db.video.findUnique({
        where: {
          id: input.videoId,
        },
        select: {
          defaultMatrix: true,
        },
      });

      return data?.defaultMatrix ?? false;
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
