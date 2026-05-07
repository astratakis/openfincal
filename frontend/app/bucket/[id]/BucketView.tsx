"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { AppHeader } from "../../components/AppHeader";
import {
  CalendarIcon,
  CheckIcon,
  CopyIcon,
  PlusIcon,
  SearchIcon,
  TrashIcon,
} from "../../components/icons";
import {
  Bucket,
  Company,
  calendarUrl,
  companyKey,
  loadBuckets,
  parseCompanyQuery,
  saveBuckets,
} from "../../lib/buckets";

export default function BucketView({ bucketId }: { bucketId: string }) {
  const [buckets, setBuckets] = useState<Bucket[]>([]);
  const [hydrated, setHydrated] = useState(false);
  const [adding, setAdding] = useState(false);
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setBuckets(loadBuckets());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated) saveBuckets(buckets);
  }, [buckets, hydrated]);

  const bucket = useMemo(
    () => buckets.find((b) => b.id === bucketId),
    [buckets, bucketId],
  );

  function addCompany(e: React.FormEvent) {
    e.preventDefault();
    const parsed = parseCompanyQuery(query);
    if (!parsed) {
      setError(
        "Use a ticker (e.g. AAPL) or exchange:ticker (e.g. NASDAQ:AAPL).",
      );
      return;
    }
    setBuckets((prev) =>
      prev.map((b) => {
        if (b.id !== bucketId) return b;
        const exists = b.companies.some(
          (c) => companyKey(c) === companyKey(parsed),
        );
        if (exists) return b;
        return { ...b, companies: [...b.companies, parsed] };
      }),
    );
    setQuery("");
    setError(null);
    setAdding(false);
  }

  function removeCompany(c: Company) {
    setBuckets((prev) =>
      prev.map((b) =>
        b.id !== bucketId
          ? b
          : {
              ...b,
              companies: b.companies.filter(
                (x) => companyKey(x) !== companyKey(c),
              ),
            },
      ),
    );
  }

  async function copyUrl() {
    if (!bucket) return;
    try {
      await navigator.clipboard.writeText(calendarUrl(bucket.id));
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {}
  }

  if (!hydrated) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <AppHeader />
      </div>
    );
  }

  if (!bucket) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <AppHeader />
        <main className="container" style={{ paddingTop: 64, textAlign: "center" }}>
          <h1 style={{ fontSize: 20, fontWeight: 600 }}>Bucket not found</h1>
          <p className="muted" style={{ marginTop: 8 }}>
            This bucket doesn't exist on this device.
          </p>
          <Link className="btn" href="/dashboard" style={{ marginTop: 16 }}>
            Back to dashboard
          </Link>
        </main>
      </div>
    );
  }

  const url = calendarUrl(bucket.id);

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <AppHeader />

      <main className="container" style={{ paddingTop: 32, paddingBottom: 64, flex: 1 }}>
        <nav style={{ marginBottom: 16, fontSize: 14 }}>
          <Link
            href="/dashboard"
            style={{ color: "var(--fg-muted)" }}
          >
            Dashboard
          </Link>
          <span style={{ margin: "0 6px", color: "var(--fg-subtle)" }}>/</span>
          <span style={{ color: "var(--fg-default)" }}>{bucket.name}</span>
        </nav>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 12,
            marginBottom: 24,
            flexWrap: "wrap",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ color: "var(--accent-fg)" }}>
              <CalendarIcon size={24} />
            </span>
            <h1 style={{ fontSize: 24, fontWeight: 600, letterSpacing: "-0.01em" }}>
              {bucket.name}
            </h1>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button type="button" className="btn" onClick={copyUrl}>
              {copied ? <CheckIcon /> : <CopyIcon />}
              <span>{copied ? "Copied!" : "Copy calendar URL"}</span>
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setAdding((v) => !v)}
            >
              <PlusIcon />
              <span>Add company</span>
            </button>
          </div>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: "var(--canvas-subtle)",
            border: "1px solid var(--border-default)",
            borderRadius: 8,
            padding: "8px 12px",
            marginBottom: 24,
          }}
        >
          <span style={{ color: "var(--fg-muted)", fontSize: 12, textTransform: "uppercase", letterSpacing: "0.04em" }}>
            iCal
          </span>
          <code
            style={{
              flex: 1,
              overflow: "auto",
              whiteSpace: "nowrap",
              color: "var(--fg-default)",
            }}
          >
            {url}
          </code>
        </div>

        {adding && (
          <form
            onSubmit={addCompany}
            style={{
              padding: 16,
              border: "1px solid var(--border-default)",
              borderRadius: 8,
              background: "var(--canvas-subtle)",
              marginBottom: 24,
            }}
          >
            <label
              style={{
                display: "block",
                fontWeight: 600,
                marginBottom: 6,
                fontSize: 14,
              }}
            >
              Search by ticker
            </label>
            <div style={{ display: "flex", gap: 8 }}>
              <div style={{ position: "relative", flex: 1 }}>
                <span
                  style={{
                    position: "absolute",
                    left: 10,
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "var(--fg-muted)",
                    pointerEvents: "none",
                  }}
                >
                  <SearchIcon />
                </span>
                <input
                  autoFocus
                  className="input"
                  style={{ paddingLeft: 32 }}
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value);
                    setError(null);
                  }}
                  placeholder="AAPL or NASDAQ:AAPL"
                />
              </div>
              <button type="submit" className="btn btn-primary">
                Add
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => {
                  setAdding(false);
                  setQuery("");
                  setError(null);
                }}
              >
                Cancel
              </button>
            </div>
            {error ? (
              <p
                style={{
                  color: "var(--danger-fg)",
                  fontSize: 12,
                  marginTop: 8,
                }}
              >
                {error}
              </p>
            ) : (
              <p className="muted" style={{ fontSize: 12, marginTop: 8 }}>
                Plain ticker (AAPL) or exchange-prefixed (NYSE:BRK.B).
              </p>
            )}
          </form>
        )}

        {bucket.companies.length === 0 ? (
          <div
            style={{
              textAlign: "center",
              padding: "48px 24px",
              border: "1px dashed var(--border-default)",
              borderRadius: 8,
              background: "var(--canvas-subtle)",
            }}
          >
            <h2 style={{ fontWeight: 600, fontSize: 16, marginBottom: 4 }}>
              No companies yet
            </h2>
            <p className="muted" style={{ marginBottom: 16 }}>
              Add companies to this bucket to populate the calendar.
            </p>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setAdding(true)}
            >
              <PlusIcon />
              <span>Add company</span>
            </button>
          </div>
        ) : (
          <ul
            style={{
              listStyle: "none",
              padding: 0,
              border: "1px solid var(--border-default)",
              borderRadius: 8,
              overflow: "hidden",
              background: "var(--canvas-default)",
            }}
          >
            {bucket.companies.map((c, i) => (
              <li
                key={companyKey(c)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "10px 16px",
                  borderTop: i === 0 ? "none" : "1px solid var(--border-muted)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span
                    style={{
                      fontFamily:
                        "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
                      fontWeight: 600,
                    }}
                  >
                    {c.ticker}
                  </span>
                  {c.exchange && (
                    <span
                      style={{
                        fontSize: 11,
                        padding: "2px 6px",
                        borderRadius: 4,
                        background: "var(--btn-bg)",
                        color: "var(--fg-muted)",
                        border: "1px solid var(--border-muted)",
                      }}
                    >
                      {c.exchange}
                    </span>
                  )}
                </div>
                <button
                  type="button"
                  className="btn-icon"
                  onClick={() => removeCompany(c)}
                  aria-label={`Remove ${companyKey(c)}`}
                  title="Remove"
                >
                  <TrashIcon />
                </button>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}
