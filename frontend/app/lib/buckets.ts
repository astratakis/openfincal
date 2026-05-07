export type Company = {
  ticker: string;
  exchange?: string;
};

export type Bucket = {
  id: string;
  name: string;
  companies: Company[];
  createdAt: number;
};

const STORAGE_KEY = "openfincal:buckets:v1";

export function makeId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID().slice(0, 8);
  }
  return Math.random().toString(36).slice(2, 10);
}

export function loadBuckets(): Bucket[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed as Bucket[];
  } catch {
    return [];
  }
}

export function saveBuckets(buckets: Bucket[]): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(buckets));
  } catch {}
}

export function parseCompanyQuery(input: string): Company | null {
  const trimmed = input.trim().toUpperCase();
  if (!trimmed) return null;
  if (trimmed.includes(":")) {
    const [exchange, ticker] = trimmed.split(":", 2);
    if (!exchange || !ticker) return null;
    if (!/^[A-Z0-9.]{1,12}$/.test(exchange)) return null;
    if (!/^[A-Z0-9.\-]{1,12}$/.test(ticker)) return null;
    return { exchange, ticker };
  }
  if (!/^[A-Z0-9.\-]{1,12}$/.test(trimmed)) return null;
  return { ticker: trimmed };
}

export function companyKey(c: Company): string {
  return c.exchange ? `${c.exchange}:${c.ticker}` : c.ticker;
}

export function calendarUrl(bucketId: string): string {
  const origin =
    typeof window !== "undefined" ? window.location.origin : "https://openfincal.com";
  return `${origin}/calendars/${bucketId}.ics`;
}
