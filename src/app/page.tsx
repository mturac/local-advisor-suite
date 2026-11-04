"use client"

import { useEffect, useState } from "react"
import { Github, Loader2, Play, Terminal } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ThemeToggle } from "@/components/theme-toggle"
import type { Catalog } from "@/lib/console-types"
import { DoctorPanel } from "@/components/console/doctor-panel"
import { HistoryPanel } from "@/components/console/history-panel"
import { Runner } from "@/components/console/runner"
import { SkillsBrowser } from "@/components/console/skills-browser"
import { Walkthroughs } from "@/components/console/walkthroughs"
import { WorkspacePanel } from "@/components/console/workspace-panel"

const REPO_URL = "https://github.com/turacistanbul/local-advisor-suite"

export default function Home() {
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
                  <span className="text-muted-foreground font-normal"> — Console</span>
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
            <div className="ml-auto flex items-center gap-1">
              {catalog && (
                <span className="hidden md:inline text-xs text-muted-foreground mr-2">
                  {catalog.commands.length} commands · offline · zero-vendor
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
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 mx-auto w-full max-w-7xl px-4 md:px-6 py-5">
        <Tabs defaultValue="walkthroughs" className="w-full">
          <TabsList className="mb-4 h-10 w-full justify-start overflow-x-auto rounded-lg bg-muted/60 p-1">
            <TabsTrigger value="walkthroughs" className="gap-1.5 text-xs sm:text-sm">
              <Play className="size-3.5" />
              Walkthroughs
            </TabsTrigger>
            <TabsTrigger value="runner" className="gap-1.5 text-xs sm:text-sm">
              <Terminal className="size-3.5" />
              Runner
            </TabsTrigger>
            <TabsTrigger value="skills" className="gap-1.5 text-xs sm:text-sm">
              Skills
            </TabsTrigger>
            <TabsTrigger value="doctor" className="gap-1.5 text-xs sm:text-sm">
              Doctor
            </TabsTrigger>
            <TabsTrigger value="workspace" className="gap-1.5 text-xs sm:text-sm">
              Workspace
            </TabsTrigger>
            <TabsTrigger value="history" className="gap-1.5 text-xs sm:text-sm">
              History
            </TabsTrigger>
          </TabsList>

          <TabsContent value="walkthroughs">
            <Walkthroughs onRan={() => setHistoryKey((k) => k + 1)} />
          </TabsContent>
          <TabsContent value="runner">
            {catalogError ? (
              <div className="rounded-lg border border-rose-500/30 bg-rose-500/5 p-4 text-sm text-rose-600 dark:text-rose-400">
                Failed to load command catalog: {catalogError}
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
            Local Advisor Suite {version ? `v${version}` : ""} — 6 hosts · 13 skills · 95
            tests
          </span>
          <span>
            Demo workspace: every command runs against a seeded, disposable ledger in{" "}
            <code className="font-mono">.workspace/</code>
          </span>
        </div>
      </footer>
    </div>
  )
}
