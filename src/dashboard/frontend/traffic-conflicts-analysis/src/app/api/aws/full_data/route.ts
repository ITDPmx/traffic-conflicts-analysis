import { generateGetPresignedUrl } from "~/server/utils/aws";
import { hasAccess } from "~/server/utils/idAccess";
import { z } from "zod";
import type { NextRequest } from "next/server";

const getUrl = async (req: NextRequest) => {
  const searchParams = req.nextUrl.searchParams;
  const id = z.string().safeParse(searchParams.get("id")).data;
  const asset = z.string().safeParse(searchParams.get("asset")).data;

  if (!id) {
    return Response.json(
      { error: { message: "Missing video ID" } },
      { status: 400 },
    );
  }

  const hasResourceAccess = await hasAccess(id);

  if (!hasResourceAccess) {
    return Response.json(
      { error: { message: "Unauthorized" } },
      { status: 401 },
    );
  }

  let fileName = "";

  switch (asset) {
    case "original_video":
      fileName = `videos/${id}.mp4`;
      break;
    case "summary":
      fileName = `csvs/summary${id}.csv`;
      break;
    case "full_data":
      fileName = `csvs/${id}.csv`;
      break;
    case "processed_video":
      fileName = `processed_videos/${id}.mp4`;
      break;
    default:
      return Response.json(
        { error: { message: "Invalid asset type" } },
        { status: 400 },
      );
  }
  
  const location = await generateGetPresignedUrl({ fileName: fileName });

  if (!location) {
    return Response.json(
      { error: { message: "Error getting presigned URL" } },
      { status: 500 },
    );
  }

  return Response.redirect(location);
};

export { getUrl as GET };
