import { Queue } from "bullmq";

const connection = {
  host: process.env.REDIS_HOST ?? "127.0.0.1",
  port: Number(process.env.REDIS_PORT ?? 6379),
};

export const emailQueue = new Queue("emails", { connection });

export function scheduleEmail(payload, delayMs) {
  return emailQueue.add("send", payload, {
    attempts: 5,
    backoff: { type: "exponential", delay: 1_000 },
    delay: delayMs,
    removeOnComplete: 500,
  });
}
