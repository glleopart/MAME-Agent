import { Memory } from "@mastra/memory";
import { LibSQLStore } from "@mastra/libsql";
import { join } from "path";

export const storage = new LibSQLStore({
	id: "mame-storage",
	url: `file:${join(process.cwd(), "data", "mame.db")}`,
});

export const memory = new Memory({
	storage,
});
