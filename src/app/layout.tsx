import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import "./globals.css"
import { Toaster } from "@/components/ui/toaster"
import { ThemeProvider } from "@/components/theme-provider"
import { LangProvider } from "@/lib/i18n"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
})

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
})

export const metadata: Metadata = {
  title: "Local Advisor Suite — Konsol / Console",
  description:
    "Local Advisor Suite'in web test konsolu: 39 workbench komutunun tamamını, 13 beceriyi ve 6 aracın kurulum sağlığını tarayıcıda dene; Deep Research hikâyesi Firecrawl ile canlı web'i araştır. Beceriler AI agent'ınla hazır — ek kurulum yok. / Web test console for the Local Advisor Suite: try all 39 commands, 13 skills and 6-host health in the browser; the Deep Research story searches the live web via Firecrawl. Skills are ready via your AI agent — no extra setup.",
  icons: {
    icon: "https://z-cdn.chatglm.cn/z-ai/static/logo.svg",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="tr" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          <LangProvider>
            {children}
            <Toaster />
          </LangProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
