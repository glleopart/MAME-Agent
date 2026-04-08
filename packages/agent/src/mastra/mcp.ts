import { MCPClient } from "@mastra/mcp";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const mcpServerPath = join(__dirname, "../../../mcp-server");

export const mcpClient = new MCPClient({
  servers: {
    "materials-project": {
      command: "uv",
      args: ["run", "mame-mcp"],
      cwd: mcpServerPath,
      env: {
        MP_API_KEY: process.env.MP_API_KEY ?? "",
      },
    },
  },
});
