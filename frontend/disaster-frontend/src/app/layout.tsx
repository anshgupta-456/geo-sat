import "./globals.css"; // <-- This line activates Tailwind!
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Disaster Dashboard",
  description: "Geo-Intelligent AI System",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="m-0 p-0 h-screen w-screen overflow-hidden bg-slate-50">
        {children}
      </body>
    </html>
  );
}