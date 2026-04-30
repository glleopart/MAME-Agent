import { MCPClient } from "@mastra/mcp";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { z } from "zod";

const __dirname = dirname(fileURLToPath(import.meta.url));
const mcpServerPath = join(__dirname, "../../../mcp-server");

export const mcpClient = new MCPClient({
  servers: {
    "materials-project": {
      command: "uv",
      args: ["run", "mame-mcp"],
      cwd: mcpServerPath,
      env: {
        ...process.env,
        MP_API_KEY: process.env.MP_API_KEY ?? "",
      },
    },
  },
});

// ---------------------------------------------------------------------------
// Workaround for Mastra bug: serializeTool() blindly calls zodToJsonSchema()
// on tool.inputSchema, but MCP tools store schemas as AJV-based StandardSchema
// objects (not Zod), causing a crash in the GET /tools playground endpoint.
//
// Fix: extract the JSON schema from the StandardSchema wrapper, build a proper
// Zod v3 schema, and replace inputSchema so zodToJsonSchema() can handle it.
// ---------------------------------------------------------------------------

type JsonProp = { type?: string; default?: unknown };
type JsonObj = { type?: string; properties?: Record<string, JsonProp>; required?: string[] };

function propToZod(prop: JsonProp): z.ZodTypeAny {
  switch (prop.type) {
    case "integer": return z.number().int();
    case "number":  return z.number();
    case "boolean": return z.boolean();
    case "array":   return z.array(z.any());
    default:        return z.string();
  }
}

function jsonSchemaToZod(schema: JsonObj): z.ZodObject<Record<string, z.ZodTypeAny>> {
  const required = new Set(schema.required ?? []);
  const shape: Record<string, z.ZodTypeAny> = {};
  for (const [key, prop] of Object.entries(schema.properties ?? {})) {
    let field = propToZod(prop);
    if (prop.default !== undefined) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      field = (field as any).default(prop.default);
    } else if (!required.has(key)) {
      field = field.optional();
    }
    shape[key] = field;
  }
  return z.object(shape);
}

/** Get the raw JSON schema from an AJV-based StandardSchema wrapper. */
function extractJsonSchema(standardSchema: unknown): JsonObj | null {
  try {
    // StandardSchemaWithJSON exposes ~standard.jsonSchema.input()
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const fn = (standardSchema as any)?.["~standard"]?.jsonSchema?.input;
    if (typeof fn === "function") {
      return fn({ target: "draft-07", libraryOptions: {} }) as JsonObj;
    }
  } catch {
    // fall through
  }
  return null;
}

/**
 * Like mcpClient.listTools() but replaces each tool's inputSchema with a
 * proper Zod v3 schema so Mastra's serializeTool() doesn't crash.
 */
export async function listToolsFixed() {
  const tools = await mcpClient.listTools();
  for (const tool of Object.values(tools)) {
    const jsonSchema = extractJsonSchema((tool as unknown as Record<string, unknown>).inputSchema);
    if (jsonSchema?.type === "object") {
      // Replace with a Zod schema — serializeTool calls zodToJsonSchema() on
      // this and Zod v3 schemas have ._def so the conversion succeeds.
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (tool as any).inputSchema = jsonSchemaToZod(jsonSchema);
    }
  }
  return tools;
}
