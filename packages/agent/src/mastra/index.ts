import { Mastra } from "@mastra/core";
import { mameAgent } from "./agents/mame-agent";

export const mastra = new Mastra({
  agents: { mameAgent },
});
