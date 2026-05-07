import Link from "next/link";

export function LogoMark({ size = 28 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <rect
        x="2.5"
        y="5.5"
        width="27"
        height="23"
        rx="4"
        stroke="currentColor"
        strokeWidth="2"
      />
      <path
        d="M2.5 12.5h27"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M9.5 2.5v6M22.5 2.5v6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M9.5 18.5l3 3 6-6"
        stroke="var(--success-fg)"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function Logo({
  href = "/",
  showWordmark = true,
}: {
  href?: string;
  showWordmark?: boolean;
}) {
  return (
    <Link
      href={href}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 10,
        color: "var(--fg-default)",
        textDecoration: "none",
      }}
    >
      <LogoMark />
      {showWordmark && (
        <span style={{ fontWeight: 600, fontSize: 16, letterSpacing: "-0.01em" }}>
          openfincal
        </span>
      )}
    </Link>
  );
}
