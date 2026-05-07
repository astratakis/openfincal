"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronDownIcon, GearIcon, SignOutIcon } from "./icons";

type Props = {
  name?: string;
  email?: string;
};

function initials(name: string) {
  const parts = name.trim().split(/\s+/);
  const letters = parts.slice(0, 2).map((p) => p[0]?.toUpperCase() ?? "");
  return letters.join("") || "?";
}

export function UserMenu({ name = "Demo User", email = "demo@openfincal.local" }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onDocClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDocClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label="Open user menu"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 4,
          padding: 2,
          borderRadius: 999,
          border: "1px solid var(--border-default)",
          background: "transparent",
        }}
      >
        <span
          style={{
            width: 28,
            height: 28,
            borderRadius: "50%",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            background: "var(--avatar-gradient)",
            color: "#fff",
            fontWeight: 600,
            fontSize: 12,
            letterSpacing: "0.02em",
          }}
        >
          {initials(name)}
        </span>
        <ChevronDownIcon size={12} />
      </button>

      {open && (
        <div
          role="menu"
          style={{
            position: "absolute",
            top: "calc(100% + 6px)",
            right: 0,
            minWidth: 220,
            background: "var(--canvas-overlay)",
            border: "1px solid var(--border-default)",
            borderRadius: 8,
            boxShadow: "var(--shadow-overlay)",
            padding: 4,
            zIndex: 20,
          }}
        >
          <div style={{ padding: "8px 12px" }}>
            <div style={{ fontWeight: 600 }}>{name}</div>
            <div style={{ fontSize: 12, color: "var(--fg-muted)" }}>{email}</div>
          </div>
          <hr className="divider" style={{ margin: "4px 0" }} />
          <MenuItem icon={<GearIcon />} label="Settings" onClick={() => setOpen(false)} />
          <MenuItem
            icon={<SignOutIcon />}
            label="Sign out"
            danger
            onClick={() => setOpen(false)}
          />
        </div>
      )}
    </div>
  );
}

function MenuItem({
  icon,
  label,
  onClick,
  danger,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  danger?: boolean;
}) {
  return (
    <button
      type="button"
      role="menuitem"
      onClick={onClick}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        width: "100%",
        textAlign: "left",
        padding: "6px 12px",
        borderRadius: 6,
        color: danger ? "var(--danger-fg)" : "var(--fg-default)",
        background: "transparent",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "var(--btn-hover-bg)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "transparent";
      }}
    >
      <span style={{ display: "inline-flex", color: "var(--fg-muted)" }}>{icon}</span>
      <span>{label}</span>
    </button>
  );
}
