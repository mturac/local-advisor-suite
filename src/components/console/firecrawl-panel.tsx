"use client"

import { useState } from "react"
import {
  Check,
  FileSearch,
  Globe,
  Layers,
  Link2,
  Loader2,
  Play,
  Search,
  Sparkles,
  X,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { useLang } from "@/lib/i18n"
import { JsonViewer } from "./json-viewer"

type FcAction = "search" | "scrape" | "map" | "extract" | "crawl"

interface FcState {
  phase: "idle" | "running" | "done" | "failed"
  data: Record<string, unknown> | null
  error: string | null
}

const IDLE: FcState = { phase: "idle", data: null, error: null }

const FEATURES: {
  action: FcAction
  icon: typeof Search
  accent: string
}[] = [
  { action: "search", icon: Search, accent: "text-sky-600 dark:text-sky-400" },
  { action: "scrape", icon: Globe, accent: "text-emerald-600 dark:text-emerald-400" },
  { action: "crawl", icon: Layers, accent: "text-amber-600 dark:text-amber-400" },
  { action: "map", icon: Link2, accent: "text-violet-600 dark:text-violet-400" },
  { action: "extract", icon: Sparkles, accent: "text-rose-600 dark:text-rose-400" },
]

function defaultForm(action: FcAction): Record<string, string> {
  switch (action) {
    case "search":
      return { query: "duckdb vs sqlite", limit: "5" }
    case "scrape":
      return { url: "https://www.sqlite.org/wal.html" }
    case "map":
      return { url: "https://duckdb.org/docs/stable/", limit: "20" }
    case "extract":
      return {
        url: "https://news.ycombinator.com/",
        prompt: "List the top 3 stories on the front page with their titles and point counts.",
      }
    case "crawl":
      return { url: "https://docs.firecrawl.dev/introduction", limit: "5" }
  }
}

export function FirecrawlPanel() {
  const { t } = useLang()
  const [action, setAction] = useState<FcAction>("search")
  const [form, setForm] = useState<Record<string, string>>(defaultForm("search"))
  const [state, setState] = useState<FcState>(IDLE)

  function pick(next: FcAction) {
    setAction(next)
    setForm(defaultForm(next))
    setState(IDLE)
  }

  async function run() {
    setState({ phase: "running", data: null, error: null })
    try {
      const body: Record<string, unknown> = { action }
      for (const [k, v] of Object.entries(form)) {
        if (!v.trim()) continue
        body[k] = k === "limit" ? Number(v) : v
      }
      const res = await fetch("/api/firecrawl", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })
      const data = (await res.json()) as Record<string, unknown>
      if (!res.ok) {
        setState({
          phase: "failed",
          data,
          error: String(data.error ?? `HTTP ${res.status}`) + (data.detail ? ` — ${data.detail}` : ""),
        })
        return
      }
      setState({ phase: "done", data, error: null })
    } catch (err) {
      setState({
        phase: "failed",
        data: null,
        error: String(err instanceof Error ? err.message : err),
      })
    }
  }

  const busy = state.phase === "running"

  return (
    <div className="space-y-4">
      {/* intro */}
      <div className="rounded-xl border border-border bg-card p-5 relative overflow-hidden">
        <div className="hero-glow absolute inset-0 opacity-50" aria-hidden />
        <div className="relative">
          <div className="flex items-center gap-2">
            <FileSearch className="size-4 text-sky-600 dark:text-sky-400" />
            <h2 className="text-lg font-semibold leading-tight">{t("fc.title")}</h2>
          </div>
          <p className="mt-1.5 text-sm text-muted-foreground leading-relaxed max-w-3xl">
            {t("fc.intro")}
          </p>
          <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-2 max-w-3xl">
            {["fc.point1", "fc.point2", "fc.point3"].map((k) => (
              <div
                key={k}
                className="rounded-lg border border-border bg-muted/30 px-3 py-2 text-[12px] leading-relaxed text-foreground/80"
              >
                {t(k)}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* feature grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
        {FEATURES.map(({ action: a, icon: Icon, accent }) => {
          const selected = action === a
          return (
            <button
              key={a}
              onClick={() => pick(a)}
              className={cn(
                "text-left rounded-xl border bg-card p-4 transition-all",
                selected
                  ? "border-sky-500/50 shadow-sm ring-1 ring-sky-500/20"
                  : "border-border hover:border-sky-500/30 hover:bg-muted/40"
              )}
            >
              <div className="flex items-center gap-2.5">
                <div
                  className={cn(
                    "size-8 rounded-lg border flex items-center justify-center shrink-0",
                    selected ? "bg-sky-500/10 border-sky-500/30" : "bg-muted border-border"
                  )}
                >
                  <Icon className={cn("size-4", selected ? accent : "text-muted-foreground")} />
                </div>
                <div className="min-w-0">
                  <div className="text-sm font-semibold font-mono">{a}</div>
                  <div className="text-[11px] text-muted-foreground">{t(`fc.${a}.tag`)}</div>
                </div>
              </div>
              <p className="mt-2 text-[12px] leading-relaxed text-foreground/75">
                {t(`fc.${a}.what`)}
              </p>
              <p className="mt-1.5 text-[11px] leading-relaxed text-muted-foreground">
                <span className="font-medium text-foreground/70">{t("fc.whenLabel")}</span>{" "}
                {t(`fc.${a}.when`)}
              </p>
              {a === "crawl" && (
                <Badge
                  variant="outline"
                  className="mt-2 font-mono text-[9px] bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30"
                >
                  {t("fc.slowBadge")}
                </Badge>
              )}
              {a === "extract" && (
                <Badge
                  variant="outline"
                  className="mt-2 font-mono text-[9px] bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30"
                >
                  {t("fc.llmBadge")}
                </Badge>
              )}
            </button>
          )
        })}
      </div>

      {/* try-it */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <div className="px-4 py-3 border-b border-border bg-muted/30 flex items-center gap-2 flex-wrap">
          <Play className="size-3.5 text-sky-600 dark:text-sky-400" />
          <h3 className="text-sm font-semibold">
            {t("fc.tryTitle")} — <span className="font-mono text-sky-600 dark:text-sky-400">{action}</span>
          </h3>
          <span className="ml-auto text-[11px] text-muted-foreground">{t("fc.tryHint")}</span>
        </div>
        <div className="p-4 space-y-3">
          {action === "search" && (
            <div className="grid grid-cols-1 sm:grid-cols-[1fr_120px] gap-3">
              <div>
                <Label htmlFor="fc-query" className="text-xs text-muted-foreground">
                  {t("fc.fieldQuery")}
                </Label>
                <Input
                  id="fc-query"
                  value={form.query}
                  onChange={(e) => setForm({ ...form, query: e.target.value })}
                  placeholder="duckdb vs sqlite"
                  className="mt-1 font-mono text-sm"
                />
              </div>
              <div>
                <Label htmlFor="fc-limit" className="text-xs text-muted-foreground">
                  {t("fc.fieldLimit")}
                </Label>
                <Input
                  id="fc-limit"
                  type="number"
                  min={1}
                  max={10}
                  value={form.limit}
                  onChange={(e) => setForm({ ...form, limit: e.target.value })}
                  className="mt-1 font-mono text-sm"
                />
              </div>
            </div>
          )}
          {(action === "scrape" || action === "map" || action === "crawl" || action === "extract") && (
            <div className="grid grid-cols-1 gap-3">
              <div>
                <Label htmlFor="fc-url" className="text-xs text-muted-foreground">
                  {t("fc.fieldUrl")}
                </Label>
                <Input
                  id="fc-url"
                  value={form.url}
                  onChange={(e) => setForm({ ...form, url: e.target.value })}
                  placeholder="https://example.com/page"
                  className="mt-1 font-mono text-sm"
                />
              </div>
              {action === "map" && (
                <div className="max-w-[160px]">
                  <Label htmlFor="fc-map-limit" className="text-xs text-muted-foreground">
                    {t("fc.fieldLimit")}
                  </Label>
                  <Input
                    id="fc-map-limit"
                    type="number"
                    min={1}
                    max={50}
                    value={form.limit}
                    onChange={(e) => setForm({ ...form, limit: e.target.value })}
                    className="mt-1 font-mono text-sm"
                  />
                </div>
              )}
              {action === "crawl" && (
                <div className="max-w-[160px]">
                  <Label htmlFor="fc-crawl-limit" className="text-xs text-muted-foreground">
                    {t("fc.fieldPages")}
                  </Label>
                  <Input
                    id="fc-crawl-limit"
                    type="number"
                    min={1}
                    max={10}
                    value={form.limit}
                    onChange={(e) => setForm({ ...form, limit: e.target.value })}
                    className="mt-1 font-mono text-sm"
                  />
                </div>
              )}
              {action === "extract" && (
                <div>
                  <Label htmlFor="fc-prompt" className="text-xs text-muted-foreground">
                    {t("fc.fieldPrompt")}
                  </Label>
                  <textarea
                    id="fc-prompt"
                    value={form.prompt}
                    onChange={(e) => setForm({ ...form, prompt: e.target.value })}
                    rows={2}
                    className="mt-1 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  />
                </div>
              )}
            </div>
          )}
          <div className="flex items-center gap-2">
            <Button onClick={() => void run()} disabled={busy} className="gap-2">
              {busy ? <Loader2 className="size-4 animate-spin" /> : <Play className="size-4" />}
              {busy ? t("fc.running") : t("fc.runAction", { action })}
            </Button>
            {state.phase === "done" && (
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-700 dark:text-emerald-300">
                <Check className="size-3.5" />
                {t("fc.done")}
              </span>
            )}
            {state.phase === "failed" && (
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-rose-600 dark:text-rose-400">
                <X className="size-3.5" />
                {t("fc.failed")}
              </span>
            )}
          </div>

          {state.error && (
            <div className="rounded-lg border border-rose-500/30 bg-rose-500/5 px-3 py-2 text-[13px] text-rose-600 dark:text-rose-400 break-words">
              {state.error}
            </div>
          )}

          {state.data && state.phase !== "failed" && (
            <FcResult action={action} data={state.data} t={t} />
          )}
        </div>
      </div>

      <p className="text-xs text-muted-foreground px-1 leading-relaxed">{t("fc.footnote")}</p>
    </div>
  )
}

function FcResult({
  action,
  data,
  t,
}: {
  action: FcAction
  data: Record<string, unknown>
  t: (key: string, vars?: Record<string, string | number>) => string
}) {
  if (action === "search") {
    const results =
      (data.results as { title: string; url: string; description: string }[] | undefined) ?? []
    return (
      <div className="rounded-lg border border-sky-500/30 bg-sky-500/5 overflow-hidden">
        <div className="px-3 py-2 border-b border-border/50 text-xs font-medium text-sky-700 dark:text-sky-300">
          {t("fc.searchResults", { n: results.length })}
        </div>
        <ul className="divide-y divide-border/50 max-h-80 overflow-y-auto scroll-polite">
          {results.map((r, i) => (
            <li key={`${r.url}-${i}`} className="px-3 py-2">
              <a
                href={r.url}
                target="_blank"
                rel="noreferrer"
                className="text-[13px] font-medium hover:text-emerald-600 dark:hover:text-emerald-400 leading-snug"
              >
                {r.title || r.url}
              </a>
              <p className="font-mono text-[10.5px] text-muted-foreground mt-0.5 break-all">{r.url}</p>
              {r.description && (
                <p className="text-[12px] text-muted-foreground leading-relaxed mt-1 line-clamp-2">
                  {r.description}
                </p>
              )}
            </li>
          ))}
        </ul>
      </div>
    )
  }

  if (action === "scrape") {
    const title = String(data.title ?? "")
    const markdown = String(data.markdown ?? "")
    return (
      <div className="rounded-lg border border-sky-500/30 bg-sky-500/5 overflow-hidden">
        <div className="px-3 py-2 border-b border-border/50 text-xs font-medium text-sky-700 dark:text-sky-300">
          {title} · {String(data.markdownLength ?? 0).toLocaleString()} chars
        </div>
        <pre className="px-3 py-2.5 font-mono text-[11px] leading-relaxed whitespace-pre-wrap break-words max-h-80 overflow-y-auto scroll-polite text-foreground/80">
          {markdown.slice(0, 3000)}
          {markdown.length > 3000 ? "\n…" : ""}
        </pre>
      </div>
    )
  }

  if (action === "map") {
    const links = (data.links as string[] | undefined) ?? []
    return (
      <div className="rounded-lg border border-violet-500/30 bg-violet-500/5 overflow-hidden">
        <div className="px-3 py-2 border-b border-border/50 text-xs font-medium text-violet-700 dark:text-violet-300">
          {t("fc.mapResults", { n: links.length })}
        </div>
        <ul className="px-3 py-2 max-h-80 overflow-y-auto scroll-polite space-y-1">
          {links.map((l, i) => (
            <li key={`${l}-${i}`} className="font-mono text-[11px] text-muted-foreground break-all">
              {l}
            </li>
          ))}
        </ul>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-border bg-muted/30 p-3 max-h-96 overflow-y-auto scroll-polite">
      <JsonViewer data={data} />
    </div>
  )
}
