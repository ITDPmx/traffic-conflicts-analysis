import { env } from "~/env";

import {
  createTRPCRouter,
  protectedProcedure,
} from "~/server/api/trpc";

import { EC2 } from "@aws-sdk/client-ec2";
import { stat } from "fs";

const ec2 = new EC2({
    region: 'us-east-1',

    credentials: {
        accessKeyId: env.IAWS_EC2_ACCESS_KEY_ID,
        secretAccessKey: env.IAWS_EC2_SECRET_ACCESS_KEY,
    },
});

export const awsRouter = createTRPCRouter({
  isInstanceOn: protectedProcedure
  .query(async () => {

    return await isInstanceOn();
  }),
});

async function isInstanceOn() {
    try {
        // Describe instance status
        const data = await ec2.describeInstanceStatus({
            InstanceIds: [env.IAWS_INSTANCE_ID],
            IncludeAllInstances: true // This ensures you get the status even for stopped instances
        });

        if (data?.InstanceStatuses?.length === 0) {
            console.log(`Instance ${env.IAWS_INSTANCE_ID} is stopped or does not exist.`);
            return false
        } else {
            const state = data?.InstanceStatuses ? data?.InstanceStatuses[0]?.InstanceState?.Name : "undefined";
            console.log(`Instance ${env.IAWS_INSTANCE_ID} is ${state}.`);
            return state === "running";
        }
    } catch (error) {
        console.error(`Error checking instance status: ${JSON.stringify(error)}`);
        return false;
    }
}

