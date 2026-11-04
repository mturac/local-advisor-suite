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
    "Local Advisor Suite'in web test konsolu: 38 workbench komutunun tamamını, 13 beceriyi ve 6 aracın kurulum sağlığını tarayıcıda dene — tamamen çevrimdışı. / Web test console for the Local Advisor Suite: try all 38 commands, 13 skills and 6-host health — fully offline.",
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
