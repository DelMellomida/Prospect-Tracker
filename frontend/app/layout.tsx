import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
    title: "Prospect — Your personal pipeline",
    description: "A focused workspace to track prospective clients, conversations, and follow-ups.",
};
export default function RootLayout({ children }: {
    children: React.ReactNode;
}) {
    return (<html lang="en">
      <body>{children}</body>
    </html>);
}
