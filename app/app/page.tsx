"use client";

import { useState } from "react";

type Bucket = {
  id: string;
  name: string;
  tickers: string[];
};

function makeId() {
  return Math.random().toString(36).slice(2, 10);
}

function calendarUrl(bucketId: string) {
  const base =
    typeof window !== "undefined" ? window.location.origin : "https://openfincal.local";
  return `${base.replace(/^https?:/, "webcal:")}/calendars/${bucketId}.ics`;
}

export default function Home() {
  const [buckets, setBuckets] = useState<Bucket[]>([]);
  const [newBucketName, setNewBucketName] = useState("");
  const [tickerDrafts, setTickerDrafts] = useState<Record<string, string>>({});
  const [copied, setCopied] = useState<string | null>(null);

  function addBucket(e: React.FormEvent) {
    e.preventDefault();
    const name = newBucketName.trim();
    if (!name) return;
    setBuckets((prev) => [...prev, { id: makeId(), name, tickers: [] }]);
    setNewBucketName("");
  }

  function removeBucket(id: string) {
    setBuckets((prev) => prev.filter((b) => b.id !== id));
  }

  function addTicker(bucketId: string, e: React.FormEvent) {
    e.preventDefault();
    const raw = (tickerDrafts[bucketId] ?? "").trim().toUpperCase();
    if (!raw) return;
    setBuckets((prev) =>
      prev.map((b) =>
        b.id === bucketId && !b.tickers.includes(raw)
          ? { ...b, tickers: [...b.tickers, raw] }
          : b,
      ),
    );
    setTickerDrafts((prev) => ({ ...prev, [bucketId]: "" }));
  }

  function removeTicker(bucketId: string, ticker: string) {
    setBuckets((prev) =>
      prev.map((b) =>
        b.id === bucketId ? { ...b, tickers: b.tickers.filter((t) => t !== ticker) } : b,
      ),
    );
  }

  async function copyUrl(bucketId: string) {
    const url = calendarUrl(bucketId);
    try {
      await navigator.clipboard.writeText(url);
      setCopied(bucketId);
      setTimeout(() => setCopied((c) => (c === bucketId ? null : c)), 1500);
    } catch {
      // ignore
    }
  }

  return (
    <main style={styles.main}>
      <header style={styles.header}>
        <h1 style={styles.title}>openfincal</h1>
        <p style={styles.subtitle}>
          Build buckets of tickers and subscribe to them from Google Calendar.
        </p>
      </header>

      <section style={styles.section}>
        <form onSubmit={addBucket} style={styles.row}>
          <input
            value={newBucketName}
            onChange={(e) => setNewBucketName(e.target.value)}
            placeholder="New bucket name (e.g. Tech Mega Caps)"
            style={styles.input}
          />
          <button type="submit" style={styles.primaryBtn}>
            Create bucket
          </button>
        </form>
      </section>

      <section style={styles.bucketList}>
        {buckets.length === 0 && (
          <p style={styles.empty}>No buckets yet. Create your first one above.</p>
        )}

        {buckets.map((bucket) => {
          const url = calendarUrl(bucket.id);
          return (
            <article key={bucket.id} style={styles.bucket}>
              <div style={styles.bucketHeader}>
                <h2 style={styles.bucketTitle}>{bucket.name}</h2>
                <button
                  onClick={() => removeBucket(bucket.id)}
                  style={styles.deleteBtn}
                  aria-label="Delete bucket"
                >
                  Delete
                </button>
              </div>

              <form onSubmit={(e) => addTicker(bucket.id, e)} style={styles.row}>
                <input
                  value={tickerDrafts[bucket.id] ?? ""}
                  onChange={(e) =>
                    setTickerDrafts((prev) => ({ ...prev, [bucket.id]: e.target.value }))
                  }
                  placeholder="Add ticker (e.g. AAPL)"
                  style={styles.input}
                />
                <button type="submit" style={styles.secondaryBtn}>
                  Add
                </button>
              </form>

              <ul style={styles.tickerList}>
                {bucket.tickers.length === 0 && (
                  <li style={styles.emptySmall}>No tickers yet.</li>
                )}
                {bucket.tickers.map((t) => (
                  <li key={t} style={styles.ticker}>
                    <span>{t}</span>
                    <button
                      onClick={() => removeTicker(bucket.id, t)}
                      style={styles.tickerRemove}
                      aria-label={`Remove ${t}`}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>

              <div style={styles.urlBox}>
                <span style={styles.urlLabel}>Calendar subscription URL</span>
                <code style={styles.url}>{url}</code>
                <button onClick={() => copyUrl(bucket.id)} style={styles.copyBtn}>
                  {copied === bucket.id ? "Copied!" : "Copy"}
                </button>
              </div>
            </article>
          );
        })}
      </section>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  main: {
    maxWidth: 880,
    margin: "0 auto",
    padding: "48px 24px 96px",
  },
  header: { marginBottom: 32 },
  title: { fontSize: 32, fontWeight: 700, letterSpacing: "-0.02em" },
  subtitle: { color: "#9aa0a6", marginTop: 8 },
  section: { marginBottom: 32 },
  row: { display: "flex", gap: 8 },
  input: {
    flex: 1,
    padding: "10px 12px",
    background: "#1a1d24",
    border: "1px solid #2a2f3a",
    borderRadius: 8,
    color: "#e6e6e6",
    outline: "none",
  },
  primaryBtn: {
    padding: "10px 16px",
    background: "#3b82f6",
    border: "none",
    borderRadius: 8,
    color: "white",
    fontWeight: 600,
  },
  secondaryBtn: {
    padding: "10px 16px",
    background: "#2a2f3a",
    border: "none",
    borderRadius: 8,
    color: "#e6e6e6",
  },
  bucketList: { display: "flex", flexDirection: "column", gap: 16 },
  empty: { color: "#9aa0a6", textAlign: "center", padding: 32 },
  emptySmall: { color: "#6b7280", fontSize: 14, listStyle: "none" },
  bucket: {
    background: "#161922",
    border: "1px solid #232734",
    borderRadius: 12,
    padding: 20,
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  bucketHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  bucketTitle: { fontSize: 18, fontWeight: 600 },
  deleteBtn: {
    background: "transparent",
    border: "1px solid #3a2a2a",
    color: "#ef4444",
    borderRadius: 6,
    padding: "4px 10px",
    fontSize: 13,
  },
  tickerList: {
    display: "flex",
    flexWrap: "wrap",
    gap: 8,
    listStyle: "none",
    padding: 0,
  },
  ticker: {
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
    background: "#1f2330",
    border: "1px solid #2a2f3a",
    borderRadius: 999,
    padding: "4px 10px",
    fontSize: 14,
  },
  tickerRemove: {
    background: "transparent",
    border: "none",
    color: "#9aa0a6",
    fontSize: 16,
    lineHeight: 1,
    padding: 0,
  },
  urlBox: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    background: "#10131a",
    border: "1px dashed #2a2f3a",
    borderRadius: 8,
    padding: 10,
    flexWrap: "wrap",
  },
  urlLabel: { fontSize: 12, color: "#9aa0a6", textTransform: "uppercase" },
  url: {
    flex: 1,
    fontSize: 13,
    color: "#cbd5e1",
    overflow: "auto",
    whiteSpace: "nowrap",
  },
  copyBtn: {
    padding: "6px 12px",
    background: "#2a2f3a",
    border: "none",
    borderRadius: 6,
    color: "#e6e6e6",
    fontSize: 13,
  },
};
