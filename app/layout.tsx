import type { Metadata } from "next";
import localFont from "next/font/local";
import { Fraunces } from "next/font/google";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});
const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  weight: ["500", "600"],
  style: ["normal"],
});

export const metadata: Metadata = {
  title: "SYDAR AI — Stop throwing away food you forgot you had",
  description:
    "A retrofit camera + AI kit that tracks your fridge, flags food before it turns, and turns your leftovers into your next meal. Reserve a founding spot for AUD $16.99, fully refundable.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${fraunces.variable} font-body antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
