import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EROI | Enterprise Intelligence",
  description:
    "Enterprise Revenue & Operations Intelligence Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}