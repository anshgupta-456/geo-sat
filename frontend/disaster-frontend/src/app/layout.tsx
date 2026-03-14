
import "@/app/globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Geo-Intelligent Disaster Dashboard",
  description: "Real-time AI monitoring for floods and heatwaves",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}