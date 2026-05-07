"use client";

import { useEffect, useState } from "react";
import { useTheme } from "./theme";
import { MoonIcon, SunIcon } from "./icons";

export function ThemeToggle() {
  const { theme, toggle } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const label =
    mounted && theme === "light" ? "Switch to dark theme" : "Switch to light theme";

  return (
    <button
      type="button"
      className="btn-icon"
      onClick={toggle}
      aria-label={label}
      title={label}
    >
      {mounted && theme === "light" ? <MoonIcon /> : <SunIcon />}
    </button>
  );
}
