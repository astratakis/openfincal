"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { AppHeader } from "../components/AppHeader";
import { CalendarIcon, PlusIcon } from "../components/icons";
import {
  Bucket,
  loadBuckets,
  makeId,
  saveBuckets,
} from "../lib/buckets";

export default function DashboardPage() {
  const [buckets, setBuckets] = useState<Bucket[]>([]);
  const [hydrated, setHydrated] = useState(false);
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");

  useEffect(() => {
    setBuckets(loadBuckets());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated) saveBuckets(buckets);
  }, [buckets, hydrated]);

  const sorted = useMemo(
    () => [...buckets].sort((a, b) => b.createdAt - a.createdAt),
    [buckets],
  );

  function createBucket(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;
    setBuckets((prev) => [
      ...prev,
      { id: makeId(), name: trimmed, companies: [], createdAt: Date.now() },
    ]);
    setName("");
    setCreating(false);
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <AppHeader />

      <main className="container" style={{ paddingTop: 32, paddingBottom: 64, flex: 1 }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 24,
            gap: 12,
            flexWrap: "wrap",
          }}
        >
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 600, letterSpacing: "-0.01em" }}>
              Your buckets
            </h1>
            <p className="muted" style={{ marginTop: 4 }}>
              Group tickers into buckets and subscribe to each as a calendar.
            </p>
          </div>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => setCreating((v) => !v)}
          >
            <PlusIcon />
            <span>Create bucket</span>
          </button>
        </div>

        {creating && (
          <form
            onSubmit={createBucket}
            style={{
              display: "flex",
              gap: 8,
              marginBottom: 24,
              padding: 16,
              border: "1px solid var(--border-default)",
              borderRadius: 8,
              background: "var(--canvas-subtle)",
            }}
          >
            <input
              autoFocus
              className="input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Bucket name (e.g. Tech Mega Caps)"
            />
            <button type="submit" className="btn btn-primary">
              Create
            </button>
            <button
              type="button"
              className="btn"
              onClick={() => {
                setCreating(false);
                setName("");
              }}
            >
              Cancel
            </button>
          </form>
        )}

        {!hydrated ? null : sorted.length === 0 ? (
          <EmptyState onCreate={() => setCreating(true)} />
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
              gap: 16,
            }}
          >
            {sorted.map((b) => (
              <BucketCard key={b.id} bucket={b} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function BucketCard({ bucket }: { bucket: Bucket }) {
  return (
    <Link
      href={`/bucket/${bucket.id}`}
      style={{
        display: "block",
        padding: 16,
        background: "var(--canvas-subtle)",
        border: "1px solid var(--border-default)",
        borderRadius: 8,
        color: "var(--fg-default)",
        textDecoration: "none",
        transition: "border-color 80ms ease, background-color 80ms ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = "var(--accent-emphasis)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "var(--border-default)";
      }}
    >
      <div
        style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}
      >
        <span style={{ color: "var(--accent-fg)" }}>
          <CalendarIcon />
        </span>
        <span style={{ fontWeight: 600, fontSize: 16 }}>{bucket.name}</span>
      </div>
      <div style={{ color: "var(--fg-muted)", fontSize: 12 }}>
        {bucket.companies.length}{" "}
        {bucket.companies.length === 1 ? "company" : "companies"}
      </div>
      {bucket.companies.length > 0 && (
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 4,
            marginTop: 12,
          }}
        >
          {bucket.companies.slice(0, 6).map((c) => (
            <span
              key={c.exchange ? `${c.exchange}:${c.ticker}` : c.ticker}
              style={{
                padding: "2px 8px",
                borderRadius: 999,
                background: "var(--accent-subtle)",
                color: "var(--accent-fg)",
                fontSize: 12,
                fontFamily:
                  "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
              }}
            >
              {c.ticker}
            </span>
          ))}
          {bucket.companies.length > 6 && (
            <span
              style={{
                padding: "2px 8px",
                color: "var(--fg-muted)",
                fontSize: 12,
              }}
            >
              +{bucket.companies.length - 6} more
            </span>
          )}
        </div>
      )}
    </Link>
  );
}

function EmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <div
      style={{
        textAlign: "center",
        padding: "64px 24px",
        border: "1px dashed var(--border-default)",
        borderRadius: 8,
        background: "var(--canvas-subtle)",
      }}
    >
      <div style={{ color: "var(--fg-muted)", marginBottom: 16 }}>
        <CalendarIcon size={32} />
      </div>
      <h2 style={{ fontWeight: 600, fontSize: 18, marginBottom: 4 }}>
        No buckets yet
      </h2>
      <p className="muted" style={{ marginBottom: 16 }}>
        Create your first bucket to start tracking companies on your calendar.
      </p>
      <button type="button" className="btn btn-primary" onClick={onCreate}>
        <PlusIcon />
        <span>Create bucket</span>
      </button>
    </div>
  );
}
