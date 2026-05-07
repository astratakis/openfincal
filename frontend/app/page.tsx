import Link from "next/link";
import { Logo } from "./components/Logo";
import { ThemeToggle } from "./components/ThemeToggle";
import { GitHubIcon, SignOutIcon } from "./components/icons";

const GITHUB_URL = "https://github.com/astratakis/openfincal";

export default function LandingPage() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <header
        style={{
          borderBottom: "1px solid var(--border-muted)",
        }}
      >
        <div
          className="container"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            height: 64,
          }}
        >
          <Logo />
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <ThemeToggle />
            <a
              className="btn"
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
            >
              <GitHubIcon />
              <span>GitHub</span>
            </a>
            <button
              type="button"
              className="btn btn-primary"
              disabled
              title="Sign-in is not wired up yet — will redirect to Keycloak"
              aria-disabled
            >
              <SignOutIcon />
              <span>Sign in</span>
            </button>
          </div>
        </div>
      </header>

      <main
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "64px 24px",
        }}
      >
        <div style={{ maxWidth: 720, textAlign: "center" }}>
          <span
            style={{
              display: "inline-block",
              padding: "4px 10px",
              borderRadius: 999,
              border: "1px solid var(--border-default)",
              background: "var(--canvas-subtle)",
              color: "var(--fg-muted)",
              fontSize: 12,
              fontWeight: 500,
              marginBottom: 24,
            }}
          >
            Open Source · Self-hostable
          </span>
          <h1
            style={{
              fontSize: 48,
              lineHeight: 1.1,
              fontWeight: 700,
              letterSpacing: "-0.02em",
              marginBottom: 16,
            }}
          >
            The financial calendar,
            <br />
            <span style={{ color: "var(--accent-fg)" }}>built in the open.</span>
          </h1>
          <p
            style={{
              fontSize: 18,
              color: "var(--fg-muted)",
              marginBottom: 32,
              maxWidth: 560,
              marginLeft: "auto",
              marginRight: "auto",
            }}
          >
            openfincal lets you organize tickers into buckets and subscribe to
            their earnings, dividends, and macro events from any calendar app —
            Google, Apple, Outlook — over a single iCal URL.
          </p>
          <div
            style={{
              display: "flex",
              gap: 12,
              justifyContent: "center",
              flexWrap: "wrap",
            }}
          >
            <Link className="btn btn-primary" href="/dashboard">
              View demo dashboard
            </Link>
            <a
              className="btn"
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
            >
              <GitHubIcon />
              <span>Star on GitHub</span>
            </a>
          </div>
        </div>
      </main>

      <footer
        style={{
          borderTop: "1px solid var(--border-muted)",
          padding: "24px",
          textAlign: "center",
          color: "var(--fg-muted)",
          fontSize: 12,
        }}
      >
        Open Source Financial Calendar · MIT
      </footer>
    </div>
  );
}
