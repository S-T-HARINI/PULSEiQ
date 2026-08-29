import type { Metadata } from "next";
import "@xyflow/react/dist/style.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "PULSEiQ",
  description: "AI-Powered Grid Risk Simulation & Optimization",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#07090e] text-slate-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
