"use client";

import { useEffect, useState } from "react";
import { LockIcon, SignInIcon } from "./icons";
import { Logo } from "./Logo";
import { ThemeToggle } from "./ThemeToggle";

const LOGIN_URL = "/api/v1/system/login";
const VERIFY_URL = "/api/v1/system/verify";

type Status = "loading" | "ok" | "denied";

export function AuthGate({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<Status>("loading");

  useEffect(() => {
    const ctrl = new AbortController();
    fetch(VERIFY_URL, {
      method: "GET",
      credentials: "include",
      signal: ctrl.signal,
    })
      .then((res) => setStatus(res.ok ? "ok" : "denied"))
      .catch(() => setStatus("denied"));
    return () => ctrl.abort();
  }, []);

  if (status === "ok") return <>{children}</>;
  if (status === "denied") return <ForbiddenScreen />;
  return <LoadingScreen />;
}

function MinimalHeader() {
  return (
    <header style={{ borderBottom: "1px solid var(--border-muted)" }}>
      <div
        className="container"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          height: 56,
        }}
      >
        <Logo href="/" />
        <ThemeToggle />
      </div>
    </header>
  );
}

function LoadingScreen() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <MinimalHeader />
      <main
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Spinner />
      </main>
    </div>
  );
}

function ForbiddenScreen() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <MinimalHeader />
      <main
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "32px 24px",
        }}
      >
        <div
          style={{
            maxWidth: 420,
            width: "100%",
            textAlign: "center",
            padding: 32,
            border: "1px solid var(--border-default)",
            borderRadius: 12,
            background: "var(--canvas-subtle)",
          }}
        >
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: "50%",
              background: "var(--canvas-default)",
              border: "1px solid var(--border-default)",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--fg-muted)",
              marginBottom: 16,
            }}
          >
            <LockIcon size={20} />
          </div>
          <h1 style={{ fontSize: 20, fontWeight: 600, marginBottom: 6 }}>
            Forbidden
          </h1>
          <p className="muted" style={{ marginBottom: 20 }}>
            You need to sign in to view this page.
          </p>
          <a className="btn btn-primary" href={LOGIN_URL}>
            <SignInIcon />
            <span>Sign in</span>
          </a>
        </div>
      </main>
    </div>
  );
}

function Spinner() {
  return (
    <>
      <span
        aria-label="Loading"
        role="status"
        style={{
          width: 24,
          height: 24,
          borderRadius: "50%",
          border: "2px solid var(--border-default)",
          borderTopColor: "var(--accent-fg)",
          display: "inline-block",
          animation: "openfincal-spin 0.8s linear infinite",
        }}
      />
      <style>{`
        @keyframes openfincal-spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
}
