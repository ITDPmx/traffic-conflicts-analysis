import { z } from "zod";

import {
  createTRPCRouter,
  adminProcedure,
} from "~/server/api/trpc";

export const userRouter = createTRPCRouter({
  getUserIds: adminProcedure.query(async ({ ctx }) => {
    return await ctx.db.user.findMany({
      select: {
        id: true,
      },
    });
  }),
 
  getUserDataById: adminProcedure
    .input(z.object({ userId: z.string() }))
    .query(async ({ ctx, input }) => {
        return ctx.db.user.findUnique({
            where: {
                id: input.userId,
            },
            select: {
                id: true,
                registered: true,
                name: true,
                lastLogin: true,
                role: true,
                videos: {
                    select: {
                        id: true,
                    },
                },
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

    modifyUserRole: adminProcedure
    .input(z.object({ userId: z.string(), isAdmin: z.boolean() }))
    .mutation(async ({ ctx, input }) => {
        if (input.userId === ctx.session.user.id) {
            throw new Error("No puedes modificar tu propio rol.");
        }
        await ctx.db.user.update({
            where: {
                id: input.userId,
            },
            data: {
                role: input.isAdmin ? "ADMIN" : "USER",
            },
        });
    }),
});
