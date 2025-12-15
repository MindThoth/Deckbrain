import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DeckBrain Dashboard",
  description: "Map-based dashboard for fishing vessel trip tracking and analysis",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

