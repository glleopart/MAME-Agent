import { Memory } from "@mastra/memory";
import { LibSQLStore } from "@mastra/libsql";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));

export const storage = new LibSQLStore({
	id: "mame-storage",
	url: `file:${join(__dirname, "../../data/mame.db")}`,
});

export const memory = new Memory({
	storage,
});
