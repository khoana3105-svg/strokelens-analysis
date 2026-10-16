import en from "./en.json";
import vi from "./vi.json";

export type Lang = "en" | "vi";
export type Key = keyof typeof en;
const vietnamese: Record<Key, string> = vi;
export const dictionary = { en, vi: vietnamese };
