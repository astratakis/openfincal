import { Logo } from "./Logo";
import { ThemeToggle } from "./ThemeToggle";
import { UserMenu } from "./UserMenu";

export function AppHeader() {
  return (
    <header
      style={{
        borderBottom: "1px solid var(--border-muted)",
        background: "var(--canvas-default)",
        position: "sticky",
        top: 0,
        zIndex: 10,
      }}
    >
      <div
        className="container"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          height: 56,
        }}
      >
        <Logo href="/dashboard" />
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <ThemeToggle />
          <UserMenu />
        </div>
      </div>
    </header>
  );
}
