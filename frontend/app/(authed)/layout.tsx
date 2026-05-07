import { AuthGate } from "../components/AuthGate";

export default function AuthedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthGate>{children}</AuthGate>;
}
