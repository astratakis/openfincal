import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider, THEME_BOOTSTRAP_SCRIPT } from "./components/theme";

export const metadata: Metadata = {
  title: "openfincal",
  description: "Open Source Financial Calendar",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{ __html: THEME_BOOTSTRAP_SCRIPT }}
        />
      </head>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
