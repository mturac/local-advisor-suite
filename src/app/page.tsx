"use client"

import { useEffect, useState } from "react"
import { Github, Loader2, Play, Terminal } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LangToggle } from "@/components/lang-toggle"
import { ThemeToggle } from "@/components/theme-toggle"
import { useLang } from "@/lib/i18n"
import type { Catalog } from "@/lib/console-types"
import { DoctorPanel } from "@/components/console/doctor-panel"
import { HistoryPanel } from "@/components/console/history-panel"
import { Runner } from "@/components/console/runner"
import { SkillsBrowser } from "@/components/console/skills-browser"
import { Walkthroughs } from "@/components/console/walkthroughs"
import { WorkspacePanel } from "@/components/console/workspace-panel"

const REPO_URL = "https://github.com/turacistanbul/local-advisor-suite"

function Hero() {
  const { t } = useLang()

  const steps = [
    {
      title: t("hero.step1.title"),
      desc: t("hero.step1.desc"),
    },
    {
      title: t("hero.step2.title"),
      desc: t("hero.step2.desc"),
    },
    {
      title: t("hero.step3.title"),
      desc: t("hero.step3.desc"),
    },
  ]

  return (
    <section className="relative border-b border-border overflow-hidden">
      <div className="hero-glow absolute inset-0" aria-hidden />
      <div className="dot-grid absolute inset-0 text-foreground" aria-hidden />
      <div className="relative mx-auto max-w-7xl px-4 md:px-6 pt-10 pb-8 md:pt-14 md:pb-10">
        <div className="grid grid-cols-1 lg:grid-cols-[1.05fr_0.95fr] gap-8 lg:gap-10 items-center">
          {/* left: pitch + steps */}
          <div className="min-w-0">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-400">
              <span className="relative flex size-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-60" />
                <span className="relative inline-flex rounded-full size-2 bg-emerald-500" />
              </span>
              {t("hero.badge")}
            </div>
            <h1 className="mt-4 text-3xl md:text-5xl font-bold tracking-tight leading-[1.15]">
              <span className="block">{t("hero.titleA")}</span>
              <span className="block hero-gradient-text text-[0.78em] mt-1.5">
                {t("hero.titleB")}
              </span>
            </h1>
            <p className="mt-3 text-muted-foreground text-base md:text-lg max-w-xl leading-relaxed">
              {t("hero.sub")}
            </p>
            <div className="mt-5">
              <button
                type="button"
                onClick={() =>
                  document
                    .querySelector("main")
                    ?.scrollIntoView({ behavior: "smooth", block: "start" })
                }
                className="inline-flex items-center gap-2 h-11 px-6 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-[15px] shadow-lg shadow-emerald-950/30 transition-colors"
              >
                <Play className="size-4" />
                {t("hero.cta")}
              </button>
            </div>
            <div className="mt-7 space-y-3 max-w-xl">
              {steps.map((step, i) => (
                <div key={step.title} className="flex items-start gap-3">
                  <div className="size-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center shrink-0 font-mono text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                    {i + 1}
                  </div>
                  <div className="min-w-0 pt-0.5">
                    <h2 className="text-sm font-semibold leading-tight">{step.title}</h2>
                    <p className="mt-1 text-[13px] text-muted-foreground leading-relaxed">
                      {step.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* right: terminal mock */}
          <div className="hidden lg:block min-w-0">
            <div className="term-block rounded-xl overflow-hidden shadow-2xl shadow-emerald-950/20 rotate-[0.5deg] hover:rotate-0 transition-transform duration-300">
              <div className="flex items-center gap-2 px-4 py-2.5 border-b border-border/60 bg-muted/40">
                <span className="size-3 rounded-full bg-rose-500/70" />
                <span className="size-3 rounded-full bg-amber-500/70" />
                <span className="size-3 rounded-full bg-emerald-500/70" />
                <span className="ml-2 text-[11px] font-mono text-muted-foreground">
                  demo-workspace — workbench
                </span>
                <span className="ml-auto inline-flex items-center gap-1.5 text-[10px] font-mono text-emerald-600 dark:text-emerald-400">
                  <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  DEMO
                </span>
              </div>
              <div className="p-4 md:p-5 font-mono text-[12.5px] leading-relaxed">
                <p className="break-all">
                  <span className="text-emerald-600 dark:text-emerald-400 select-none">$ </span>
                  <span className="text-emerald-700 dark:text-emerald-300">workbench research-init</span>
                  <span className="text-muted-foreground"> --topic</span>
                  <span className="text-foreground/80"> "DuckDB or SQLite?"</span>
                </p>
                <p className="text-foreground/75">
                  <span className="text-emerald-500">✓</span> status: OK · topic registered
                </p>
                <p className="mt-2.5 break-all">
                  <span className="text-emerald-600 dark:text-emerald-400 select-none">$ </span>
                  <span className="text-emerald-700 dark:text-emerald-300">workbench research-add-claim</span>
                  <span className="text-muted-foreground"> --quote "…"</span>
                </p>
                <p className="text-foreground/75">
                  <span className="text-emerald-500">✓</span> claim C1 — VERIFIED · confidence
                  HIGH
                </p>
                <p className="mt-2.5 break-all">
                  <span className="text-emerald-600 dark:text-emerald-400 select-none">$ </span>
                  <span className="text-emerald-700 dark:text-emerald-300">workbench wide-table</span>
                  <span className="text-muted-foreground"> --entity DuckDB --entity SQLite</span>
                </p>
                <p className="text-foreground/75">
                  <span className="text-emerald-500">✓</span> verified cells: 2 · contested: 1
                </p>
                <p className="mt-2.5 break-all">
                  <span className="text-emerald-600 dark:text-emerald-400 select-none">$ </span>
                  <span className="text-emerald-700 dark:text-emerald-300">workbench audit-report</span>
                </p>
                <p className="text-foreground/75">
                  <span className="text-emerald-500">✓</span> status: PASS · blocking_count: 0
                </p>
                <p className="mt-2.5">
                  <span className="text-emerald-600 dark:text-emerald-400 select-none">$ </span>
                  <span className="inline-block w-2 h-4 align-middle bg-emerald-500/80 term-cursor" />
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default function Home() {
  const { t } = useLang()
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [catalogError, setCatalogError] = useState<string | null>(null)
  const [historyKey, setHistoryKey] = useState(0)

  useEffect(() => {
    fetch("/api/catalog")
      .then(async (res) => {
        const data = await res.json()
        if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`)
        setCatalog(data)
      })
      .catch((err) => setCatalogError(String(err)))
  }, [])

  const version = catalog?.version?.replace(/^workbench\s+/i, "") ?? null

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      <header className="border-b border-border sticky top-0 z-40 bg-background/85 backdrop-blur supports-[backdrop-filter]:bg-background/70">
        <div className="mx-auto max-w-7xl px-4 md:px-6">
          <div className="flex items-center gap-3 h-14">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="size-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center shrink-0">
                <Terminal className="size-4 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div className="min-w-0">
                <h1 className="text-sm font-semibold tracking-tight truncate">
                  Local Advisor Suite
                  <span className="text-muted-foreground font-normal">
                    {" "}
                    — {t("header.subtitle")}
                  </span>
                </h1>
              </div>
              {version && (
                <Badge
                  variant="outline"
                  className="hidden sm:inline-flex font-mono text-[10px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30"
                >
                  v{version}
                </Badge>
              )}
              {!catalog && !catalogError && (
                <Loader2 className="size-3.5 animate-spin text-muted-foreground" />
              )}
            </div>
            <div className="ml-auto flex items-center gap-2">
              {catalog && (
                <span className="hidden md:inline text-xs text-muted-foreground">
                  {t("header.meta", { commands: catalog.commands.length })}
                </span>
              )}
              <a
                href={REPO_URL}
                target="_blank"
                rel="noreferrer"
                aria-label="GitHub repository"
                className="inline-flex items-center justify-center size-9 rounded-md hover:bg-muted text-muted-foreground transition-colors"
              >
                <Github className="size-4" />
              </a>
              <LangToggle />
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      <Hero />

      <main className="flex-1 mx-auto w-full max-w-7xl px-4 md:px-6 py-5">
        <Tabs defaultValue="walkthroughs" className="w-full">
          <TabsList className="mb-4 h-10 w-full justify-start overflow-x-auto rounded-lg bg-muted/60 p-1">
            <TabsTrigger value="walkthroughs" className="gap-1.5 text-xs sm:text-sm">
              <Play className="size-3.5" />
              {t("tab.stories")}
            </TabsTrigger>
            <TabsTrigger value="runner" className="gap-1.5 text-xs sm:text-sm">
              <Terminal className="size-3.5" />
              {t("tab.runner")}
            </TabsTrigger>
            <TabsTrigger value="skills" className="gap-1.5 text-xs sm:text-sm">
              {t("tab.skills")}
            </TabsTrigger>
            <TabsTrigger value="doctor" className="gap-1.5 text-xs sm:text-sm">
              {t("tab.doctor")}
            </TabsTrigger>
            <TabsTrigger value="workspace" className="gap-1.5 text-xs sm:text-sm">
              {t("tab.workspace")}
            </TabsTrigger>
            <TabsTrigger value="history" className="gap-1.5 text-xs sm:text-sm">
              {t("tab.history")}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="walkthroughs">
            <Walkthroughs onRan={() => setHistoryKey((k) => k + 1)} />
          </TabsContent>
          <TabsContent value="runner">
            {catalogError ? (
              <div className="rounded-lg border border-rose-500/30 bg-rose-500/5 p-4 text-sm text-rose-600 dark:text-rose-400">
                {t("catalog.error", { err: catalogError })}
              </div>
            ) : (
              <Runner catalog={catalog} onRan={() => setHistoryKey((k) => k + 1)} />
            )}
          </TabsContent>
          <TabsContent value="skills">
            <SkillsBrowser />
          </TabsContent>
          <TabsContent value="doctor">
            <DoctorPanel onRan={() => setHistoryKey((k) => k + 1)} />
          </TabsContent>
          <TabsContent value="workspace">
            <WorkspacePanel />
          </TabsContent>
          <TabsContent value="history">
            <HistoryPanel refreshKey={historyKey} />
          </TabsContent>
        </Tabs>
      </main>

      <footer className="mt-auto border-t border-border">
        <div className="mx-auto max-w-7xl px-4 md:px-6 py-3.5 flex flex-wrap items-center justify-between gap-2 text-[11px] text-muted-foreground">
          <span className="font-mono">
            Local Advisor Suite {version ? `v${version}` : ""} — {t("footer.line")}
          </span>
          <span>{t("footer.note")}</span>
        </div>
      </footer>
    </div>
  )
}
