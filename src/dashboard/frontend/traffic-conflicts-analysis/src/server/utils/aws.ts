// Functions for AWS services
import { env } from "~/env";

// S3

import {
  S3Client,
  PutObjectCommand,
  GetObjectCommand,
} from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

// Create an S3 client service object
const expiration = 3600; // The expiration time of the presigned URL (in seconds)
const s3Client = new S3Client({
  region: env.IAWS_REGION,
  credentials: {
    accessKeyId: env.IAWS_ACCESS_KEY_ID,
    secretAccessKey: env.IAWS_SECRET_ACCESS_KEY,
  },
});

const MAX_FILE_SIZE = 1024 * 1024 * 300; // 300 MB

export const generatePutPresignedUrl = async ({
  fileName,
}: {
  fileName: string;
}) => {
  const command = new PutObjectCommand({
    Bucket: env.IAWS_BUCKET_NAME,
    Key: fileName,
    ContentLength: MAX_FILE_SIZE,
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

export const generateGetPresignedUrl = async ({
  fileName,
}: {
  fileName: string;
}) => {
  const command = new GetObjectCommand({
    Bucket: env.IAWS_BUCKET_NAME,
    Key: fileName,
  });

  try {
    const url = await getSignedUrl(s3Client, command, {
      expiresIn: expiration,

    });
    return url;
  } catch (err) {
    console.error("Error generating presigned URL", err);
  }
  return null;
};
