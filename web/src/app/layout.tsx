import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "TripCanvas AI",
  description: "Turn your travel ideas into a visual canvas \u2013 AI\u2011crafted itineraries, budgets, and moodboards, all in one place.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
