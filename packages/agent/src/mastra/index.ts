import { Mastra } from "@mastra/core";
import { mameAgent } from "./agents/mame-agent";
import { memory } from "./memory";

export const mastra = new Mastra({
  agents: { mameAgent },
  memory: { "mame-memory": memory },
});
