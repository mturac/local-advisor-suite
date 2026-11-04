"use client"

import { useMemo, useState } from "react"
import {
  BookOpen,
  Bug,
  Check,
  ChevronDown,
  Copy,
  Eye,
  FlaskConical,
  Gift,
  Globe,
  Loader2,
  MousePointerClick,
  Play,
  RotateCcw,
  Rocket,
  Scale,
  Search,
  Trophy,
  X,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { cn } from "@/lib/utils"
import { pickLocalized, useLang } from "@/lib/i18n"
import type { RunResponse } from "@/lib/console-types"
import {
  WALKTHROUGH_FLOWS,
  type WalkthroughFlow,
  type WalkthroughStep,
} from "@/lib/walkthroughs"
import { ExitBadge, StatusBadge } from "./status-badge"
import { JsonViewer } from "./json-viewer"

const FLOW_ICONS: Record<string, typeof FlaskConical> = {
  flask: FlaskConical,
  rocket: Rocket,
  bug: Bug,
  scale: Scale,
}

type Phase = "idle" | "running" | "done" | "failed"

interface StepState {
  phase: Phase
  /** workbench result (command output) */
  result: RunResponse | null
  /** firecrawl result (normalized by /api/firecrawl) */
  fc: Record<string, unknown> | null
  /** true when the outcome matched the step's expectation */
  matched: boolean
  /** human-readable failure reason for template/dependency problems */
  note?: string
}

interface FirecrawlSearchResult {
  title: string
  url: string
  description: string
}

function resolvePick(obj: unknown, path: string): unknown {
  let cur: unknown = obj
  for (const part of path.split(".")) {
    if (Array.isArray(cur)) {
      const idx = Number(part)
      if (!Number.isInteger(idx) || idx < 0 || idx >= cur.length) return undefined
      cur = cur[idx]
    } else if (cur !== null && typeof cur === "object") {
      cur = (cur as Record<string, unknown>)[part]
    } else {
      return undefined
    }
  }
  return cur
}

function statusOf(result: RunResponse | null): string | null {
  const json = result?.json
  if (json && typeof json === "object" && "status" in (json as Record<string, unknown>)) {
    return String((json as Record<string, unknown>).status)
  }
  return null
}

const TOKEN_RE = /^\{\{([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\}\}$/

interface ResolvedArgv {
  argv: string[]
  missing: string[]
}

/** Replace whole-token {{stepId.field}} references with earlier step results. */
function resolveArgv(argv: string[], states: StepState[], flow: WalkthroughFlow): ResolvedArgv {
  const byId = new Map<string, StepState>()
  flow.steps.forEach((s, i) => {
    if (s.id) byId.set(s.id, states[i])
  })
  const out: string[] = []
  const missing: string[] = []
  for (const arg of argv) {
    const m = TOKEN_RE.exec(arg)
    if (!m) {
      out.push(arg)
      continue
    }
    const [, id, field] = m
    const st = byId.get(id)
    const src = st?.fc ?? st?.result?.json ?? null
    const val = src ? resolvePick(src, field) : undefined
    if (typeof val === "string" && val.length > 0) {
      out.push(val)
    } else if (typeof val === "number" || typeof val === "boolean") {
      out.push(String(val))
    } else {
      out.push(arg)
      missing.push(id)
    }
  }
  return { argv: out, missing: [...new Set(missing)] }
}

function stepMatched(step: WalkthroughStep, result: RunResponse): boolean {
  if (result.exitCode !== (step.expectExit ?? 0)) return false
  if (step.expectStatus && statusOf(result) !== step.expectStatus) return false
  return true
}

function formatPick(value: unknown): string {
  if (typeof value === "boolean") return value ? "✓ true" : "✗ false"
  if (value === null || value === undefined) return "—"
  if (Array.isArray(value)) return value.length ? JSON.stringify(value) : "[] (empty)"
  return String(value)
}

function hasTokens(argv: string[]): boolean {
  return argv.some((a) => TOKEN_RE.test(a))
}

function pseudoCommand(step: WalkthroughStep): string {
  const p = step.params ?? {}
  if (step.action === "search") {
    return `firecrawl search ${JSON.stringify(String(p.query ?? ""))} --limit ${Number(p.limit ?? 5)}`
  }
  if (step.action === "scrape") {
    const quote = typeof p.quote === "string" && p.quote ? ` --quote ${JSON.stringify(p.quote)}` : ""
    return `firecrawl scrape ${String(p.url ?? "")}${quote}`
  }
  return `firecrawl ${step.action ?? ""} ${JSON.stringify(p)}`
}

function quotedArg(a: string): string {
  return /\s/.test(a) ? `"${a}"` : a
}

export function Walkthroughs({ onRan }: { onRan?: () => void }) {
  const { lang, t } = useLang()
  const [flowId, setFlowId] = useState<string>(WALKTHROUGH_FLOWS[0].id)
  const [states, setStates] = useState<Record<string, StepState[]>>({})
  const [runningAll, setRunningAll] = useState(false)
  const [stepRunning, setStepRunning] = useState<number | null>(null)
  const [resetFirst, setResetFirst] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})
  const [copiedKey, setCopiedKey] = useState<string | null>(null)

  const flow = useMemo(
    () => WALKTHROUGH_FLOWS.find((f) => f.id === flowId) ?? WALKTHROUGH_FLOWS[0],
    [flowId]
  )

  const idleStates = (): StepState[] =>
    flow.steps.map(() => ({ phase: "idle", result: null, fc: null, matched: false }))

  const flowStates: StepState[] = states[flow.id] ?? idleStates()

  const doneCount = flowStates.filter((s) => s.phase === "done").length
  const allDone = doneCount === flow.steps.length && flow.steps.length > 0

  function setStepState(index: number, next: Partial<StepState>) {
    setStates((prev) => {
      const current = prev[flow.id] ?? idleStates()
      const copy = [...current]
      copy[index] = { ...copy[index], ...next }
      return { ...prev, [flow.id]: copy }
    })
  }

  async function executeStep(step: WalkthroughStep, index: number): Promise<boolean> {
    setStepRunning(index)
    setError(null)
    setExpanded((prev) => ({ ...prev, [`${flow.id}:${index}`]: true }))
    try {
      if (step.kind === "explain") {
        setStepState(index, { phase: "done", matched: true })
        return true
      }
      if (step.kind === "firecrawl") {
        const res = await fetch("/api/firecrawl", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action: step.action, ...(step.params ?? {}) }),
        })
        const data = (await res.json()) as Record<string, unknown>
        if (!res.ok) {
          setStepState(index, {
            phase: "failed",
            fc: data,
            matched: false,
            note: String(data.error ?? `HTTP ${res.status}`),
          })
          return false
        }
        let matched = true
        if (step.action === "search") {
          const results = (data.results as FirecrawlSearchResult[] | undefined) ?? []
          matched = results.length > 0
        }
        if (step.action === "scrape" && step.params?.quote) {
          matched = data.quoteFound === true
        }
        setStepState(index, { phase: matched ? "done" : "failed", fc: data, matched })
        onRan?.()
        return matched
      }

      // workbench step — resolve {{id.field}} against earlier results first
      const argv = step.argv ?? []
      const { argv: resolved, missing } = resolveArgv(argv, flowStates, flow)
      if (missing.length > 0) {
        setStepState(index, {
          phase: "failed",
          matched: false,
          note: t("wt.needsEarlier", { ids: missing.join(", ") }),
        })
        return false
      }
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: step.command, argv: resolved }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`)
      const result = data as RunResponse
      const matched = stepMatched(step, result)
      setStepState(index, { phase: matched ? "done" : "failed", result, matched })
      onRan?.()
      return matched
    } catch (err) {
      const result: RunResponse = {
        command: step.command ?? "",
        argv: step.argv ?? [],
        exitCode: -1,
        stdout: "",
        stderr: String(err instanceof Error ? err.message : err),
        durationMs: 0,
        json: null,
        truncated: false,
        timedOut: false,
      }
      setStepState(index, { phase: "failed", result, matched: false })
      return false
    } finally {
      setStepRunning(null)
    }
  }

  async function reseedWorkspace(): Promise<boolean> {
    setResetting(true)
    try {
      const res = await fetch("/api/workspace", { method: "POST" })
      if (!res.ok) throw new Error(`reseed failed (HTTP ${res.status})`)
      return true
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err))
      return false
    } finally {
      setResetting(false)
    }
  }

  async function runAll() {
    setRunningAll(true)
    setError(null)
    try {
      if (resetFirst) {
        const ok = await reseedWorkspace()
        if (!ok) return
      }
      for (let i = 0; i < flow.steps.length; i++) {
        const ok = await executeStep(flow.steps[i], i)
        if (!ok) {
          setError(
            t("wt.stoppedAt", {
              n: i + 1,
              title: pickLocalized(lang, flow.steps[i].title, flow.steps[i].titleTr),
            })
          )
          break
        }
      }
    } finally {
      setRunningAll(false)
    }
  }

  function resetFlow() {
    setStates((prev) => {
      const copy = { ...prev }
      delete copy[flow.id]
      return copy
    })
    setExpanded({})
    setError(null)
  }

  function selectFlow(id: string) {
    setFlowId(id)
    setError(null)
  }

  function commandText(step: WalkthroughStep, index: number): string {
    if (step.kind === "firecrawl") return pseudoCommand(step)
    const argv = step.argv ?? []
    const resolved = hasTokens(argv)
      ? resolveArgv(argv, flowStates, flow).argv
      : argv
    void index
    return `workbench ${step.command ?? ""}${
      resolved.length > 0 ? ` ${resolved.map(quotedArg).join(" ")}` : ""
    }`
  }

  function copyCommand(step: WalkthroughStep, key: string) {
    void navigator.clipboard?.writeText(commandText(step, 0)).then(() => {
      setCopiedKey(key)
      window.setTimeout(() => setCopiedKey(null), 1500)
    })
  }

  /* ── chapter-aware step grouping ──────────────────────────────────── */
  const chapterGroups = useMemo(() => {
    const groups: { chapter: number | null; steps: { step: WalkthroughStep; index: number }[] }[] =
      []
    flow.steps.forEach((step, index) => {
      const ch = step.chapter ?? null
      const last = groups[groups.length - 1]
      if (last && last.chapter === ch) {
        last.steps.push({ step, index })
      } else {
        groups.push({ chapter: ch, steps: [{ step, index }] })
      }
    })
    return groups
  }, [flow])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-5 items-start">
      {/* ── Story picker ─────────────────────────────────────────────── */}
      <aside className="lg:sticky lg:top-[72px]">
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <div className="p-4 border-b border-border bg-muted/30">
            <div className="flex items-center gap-2">
              <MousePointerClick className="size-4 text-emerald-500" />
              <h2 className="text-sm font-semibold">{t("wt.title")}</h2>
              <Badge variant="secondary" className="font-mono text-xs ml-auto">
                {WALKTHROUGH_FLOWS.length}
              </Badge>
            </div>
            <p className="mt-1.5 text-xs text-muted-foreground leading-relaxed">
              {t("wt.pickHint")}
            </p>
          </div>
          <div className="p-2.5 space-y-2 scroll-polite max-h-[70vh] overflow-y-auto">
            {WALKTHROUGH_FLOWS.map((f) => {
              const Icon = FLOW_ICONS[f.icon] ?? FlaskConical
              const st = states[f.id]
              const fDone = st ? st.filter((s) => s.phase === "done").length : 0
              const complete = st != null && fDone === f.steps.length
              return (
                <button
                  key={f.id}
                  onClick={() => selectFlow(f.id)}
                  className={cn(
                    "w-full text-left rounded-lg border p-3 transition-all",
                    flowId === f.id
                      ? "border-emerald-500/50 bg-emerald-500/5 shadow-sm"
                      : "border-border hover:border-emerald-500/30 hover:bg-muted/50"
                  )}
                >
                  <div className="flex items-start gap-2.5">
                    <div
                      className={cn(
                        "size-9 rounded-lg flex items-center justify-center shrink-0 border",
                        complete
                          ? "bg-emerald-500/20 border-emerald-500/40"
                          : flowId === f.id
                            ? "bg-emerald-500/10 border-emerald-500/30"
                            : "bg-muted border-border"
                      )}
                    >
                      {complete ? (
                        <Trophy className="size-4 text-emerald-600 dark:text-emerald-400" />
                      ) : (
                        <Icon
                          className={cn(
                            "size-4",
                            flowId === f.id
                              ? "text-emerald-600 dark:text-emerald-400"
                              : "text-muted-foreground"
                          )}
                        />
                      )}
                    </div>
                    <div className="min-w-0">
                      <div className="text-sm font-medium leading-snug">
                        {pickLocalized(lang, f.title, f.titleTr)}
                      </div>
                      <div className="mt-1 text-[11px] text-muted-foreground">
                        {t("wt.flowMeta", { n: f.steps.length, m: f.timeMin ?? 2 })}
                      </div>
                      <div className="mt-0.5 text-[11px] text-muted-foreground line-clamp-1">
                        {t("wt.endsWith", {
                          outcome: pickLocalized(lang, f.outcome, f.outcomeTr),
                        })}
                      </div>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      </aside>

      {/* ── Selected story ───────────────────────────────────────────── */}
      <div className="space-y-4 min-w-0">
        {/* story intro — the "you play the AI" card */}
        <div className="rounded-xl border border-border bg-card p-5 relative overflow-hidden">
          <div className="hero-glow absolute inset-0 opacity-60" aria-hidden />
          <div className="relative">
            <div className="flex items-start justify-between gap-3 flex-wrap">
              <div className="min-w-0">
                <h2 className="text-lg font-semibold leading-tight">
                  {pickLocalized(lang, flow.title, flow.titleTr)}
                </h2>
                <p className="mt-1.5 text-sm text-muted-foreground leading-relaxed max-w-2xl">
                  {pickLocalized(lang, flow.subtitle, flow.subtitleTr)}
                </p>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <Badge
                variant="outline"
                className="font-mono text-[10px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 gap-1"
              >
                <Gift className="size-3" />
                {pickLocalized(lang, flow.outcome, flow.outcomeTr)}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {t("wt.flowMeta", { n: flow.steps.length, m: flow.timeMin ?? 2 })} ·{" "}
                {t("wt.realCli")}
              </span>
            </div>
            {(flow.storyIntro || flow.storyIntroTr) && (
              <div className="mt-4 rounded-lg border border-emerald-500/25 bg-emerald-500/5 px-4 py-3 flex items-start gap-3">
                <BookOpen className="size-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                <p className="text-[13px] leading-relaxed text-foreground/85">
                  {pickLocalized(lang, flow.storyIntro, flow.storyIntroTr)}
                </p>
              </div>
            )}
            {flow.chapters && flow.chapters.length > 0 && (
              <div className="mt-3 flex flex-wrap items-center gap-1.5">
                {flow.chapters.map((c, i) => (
                  <span
                    key={c.title}
                    className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/40 px-2.5 py-0.5 text-[11px] text-muted-foreground"
                  >
                    <span className="font-mono text-[10px] text-emerald-600 dark:text-emerald-400">
                      {i + 1}
                    </span>
                    {pickLocalized(lang, c.title, c.titleTr)}
                  </span>
                ))}
              </div>
            )}
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <Button
                onClick={() => void runAll()}
                disabled={runningAll || resetting}
                size="lg"
                className="gap-2 h-11 px-6 text-base"
              >
                {runningAll ? (
                  <Loader2 className="size-4.5 animate-spin" />
                ) : (
                  <Play className="size-4.5" />
                )}
                {runningAll ? t("wt.running") : t("wt.runAll")}
              </Button>
              <Button
                variant="outline"
                onClick={resetFlow}
                disabled={runningAll || resetting}
                className="gap-2"
              >
                <RotateCcw className="size-4" />
                {t("wt.clear")}
              </Button>
              <div className="flex items-center gap-2 ml-auto">
                <Switch
                  id="reset-first"
                  checked={resetFirst}
                  onCheckedChange={setResetFirst}
                  disabled={runningAll || resetting}
                />
                <Label
                  htmlFor="reset-first"
                  className="text-xs text-muted-foreground cursor-pointer"
                >
                  {resetting ? t("wt.reseeding") : t("wt.resetFirst")}
                </Label>
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2.5">
              <div className="h-2 flex-1 rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500"
                  style={{ width: `${(doneCount / flow.steps.length) * 100}%` }}
                />
              </div>
              <span className="font-mono text-xs text-muted-foreground shrink-0 tabular-nums">
                {doneCount}/{flow.steps.length}
              </span>
            </div>
          </div>
        </div>

        {allDone && (
          <div className="rounded-xl border border-emerald-500/40 bg-gradient-to-br from-emerald-500/15 to-teal-500/5 p-4 flex items-start gap-3">
            <div className="size-9 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center shrink-0">
              <Trophy className="size-4.5 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div className="text-sm leading-relaxed">
              <span className="font-semibold text-emerald-700 dark:text-emerald-300">
                {t("wt.complete.title")}
              </span>{" "}
              {t("wt.complete.body", {
                n: flow.steps.length,
                outcome: pickLocalized(lang, flow.outcome, flow.outcomeTr),
              })}
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-rose-500/30 bg-rose-500/5 p-3 text-sm text-rose-600 dark:text-rose-400">
            {error}
          </div>
        )}

        <div className="space-y-5">
          {chapterGroups.map((group, gi) => {
            const chapter = group.chapter
            const chapterTitle =
              chapter != null && flow.chapters?.[chapter - 1]
                ? pickLocalized(
                    lang,
                    flow.chapters[chapter - 1].title,
                    flow.chapters[chapter - 1].titleTr
                  )
                : null
            return (
              <section key={`${flow.id}-ch-${chapter ?? "x"}-${gi}`} className="space-y-3">
                {chapterTitle && (
                  <div className="flex items-center gap-3 pt-1">
                    <span className="inline-flex items-center justify-center size-6 rounded-md bg-emerald-500/15 border border-emerald-500/30 font-mono text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                      {chapter}
                    </span>
                    <h3 className="text-sm font-semibold tracking-tight">{chapterTitle}</h3>
                    <div className="h-px flex-1 bg-border" aria-hidden />
                  </div>
                )}
                <ol className="space-y-3">
                  {group.steps.map(({ step, index: i }) => {
                    const st = flowStates[i]
                    const isRunning = stepRunning === i
                    const key = `${flow.id}:${i}`
                    const title = pickLocalized(lang, step.title, step.titleTr)
                    const explain = pickLocalized(lang, step.explain, step.explainTr)
                    const see = pickLocalized(lang, step.see, step.seeTr)
                    const pickLabel = pickLocalized(lang, step.pickLabel, step.pickLabelTr)
                    const pickSrc = st.fc ?? st.result?.json ?? null
                    const picked = pickSrc && step.pick ? resolvePick(pickSrc, step.pick) : undefined
                    const argv = step.argv ?? []
                    const showTokens = step.kind !== "firecrawl" && hasTokens(argv)
                    return (
                      <li
                        key={key}
                        className={cn(
                          "rounded-xl border bg-card transition-colors",
                          st.phase === "done" && "border-emerald-500/40",
                          st.phase === "failed" && "border-rose-500/40",
                          isRunning && "border-emerald-500/60"
                        )}
                      >
                        <div className="p-4 flex gap-3.5">
                          {/* number rail */}
                          <div className="flex flex-col items-center shrink-0">
                            <div
                              className={cn(
                                "size-8 rounded-full border flex items-center justify-center font-mono text-xs font-semibold",
                                st.phase === "idle" &&
                                  "border-border text-muted-foreground bg-muted/50",
                                isRunning &&
                                  "border-emerald-500/60 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 animate-pulse",
                                st.phase === "done" &&
                                  "border-emerald-500/60 bg-emerald-500 text-white",
                                st.phase === "failed" &&
                                  "border-rose-500/60 bg-rose-500/10 text-rose-600 dark:text-rose-400"
                              )}
                            >
                              {isRunning ? (
                                <Loader2 className="size-3.5 animate-spin" />
                              ) : st.phase === "done" ? (
                                <Check className="size-4" />
                              ) : st.phase === "failed" ? (
                                <X className="size-4" />
                              ) : (
                                <span>{i + 1}</span>
                              )}
                            </div>
                          </div>

                          {/* content */}
                          <div className="min-w-0 flex-1">
                            <div className="flex items-start justify-between gap-2 flex-wrap">
                              <h4 className="text-[15px] font-semibold leading-snug">
                                {title}
                                {step.deliverable && (
                                  <Badge
                                    variant="outline"
                                    className="ml-2 font-mono text-[9px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 gap-1 align-middle"
                                  >
                                    <Gift className="size-2.5" />
                                    {t("wt.deliverable")}
                                  </Badge>
                                )}
                                {step.kind === "firecrawl" && (
                                  <Badge
                                    variant="outline"
                                    className="ml-2 font-mono text-[9px] bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/30 gap-1 align-middle"
                                  >
                                    <Globe className="size-2.5" />
                                    firecrawl {step.action}
                                  </Badge>
                                )}
                                {step.kind === "explain" && (
                                  <Badge
                                    variant="outline"
                                    className="ml-2 font-mono text-[9px] bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30 gap-1 align-middle"
                                  >
                                    <BookOpen className="size-2.5" />
                                    {t("wt.readBadge")}
                                  </Badge>
                                )}
                              </h4>
                              {step.kind !== "explain" && (
                                <Button
                                  size="sm"
                                  className="gap-1.5 shrink-0"
                                  onClick={() => void executeStep(step, i)}
                                  disabled={runningAll || stepRunning !== null || resetting}
                                >
                                  {isRunning ? (
                                    <Loader2 className="size-3.5 animate-spin" />
                                  ) : (
                                    <Play className="size-3.5" />
                                  )}
                                  {t("wt.run")}
                                </Button>
                              )}
                            </div>

                            {/* explain steps: teaching card */}
                            {step.kind === "explain" ? (
                              <div className="mt-2.5 space-y-2.5">
                                <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 px-4 py-3">
                                  <p className="text-[13px] leading-relaxed whitespace-pre-line text-foreground/85">
                                    {pickLocalized(lang, step.body, step.bodyTr)}
                                  </p>
                                </div>
                                {(step.example || step.exampleTr) && (
                                  <div className="rounded-lg border border-border bg-muted/30 px-4 py-3">
                                    <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                                      {t("wt.exampleLabel")}
                                    </p>
                                    <p className="text-[13px] leading-relaxed text-foreground/80">
                                      {pickLocalized(lang, step.example, step.exampleTr)}
                                    </p>
                                  </div>
                                )}
                              </div>
                            ) : (
                              <>
                                {explain && (
                                  <p className="mt-1.5 text-sm leading-relaxed text-foreground/80">
                                    {explain}
                                  </p>
                                )}

                                {/* command */}
                                <div className="mt-2.5 term-block rounded-lg overflow-hidden">
                                  <div className="flex items-center justify-between gap-2 pl-3 pr-1.5 py-1 border-b border-border/60">
                                    <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                                      {step.kind === "firecrawl"
                                        ? t("wt.apiCallLabel")
                                        : t("wt.commandLabel")}
                                    </span>
                                    <button
                                      type="button"
                                      onClick={() => copyCommand(step, key)}
                                      className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-[11px] text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors"
                                      aria-label={t("wt.copy")}
                                    >
                                      {copiedKey === key ? (
                                        <>
                                          <Check className="size-3 text-emerald-500" />
                                          {t("wt.copied")}
                                        </>
                                      ) : (
                                        <>
                                          <Copy className="size-3" />
                                          {t("wt.copy")}
                                        </>
                                      )}
                                    </button>
                                  </div>
                                  <pre className="font-mono text-[11.5px] leading-relaxed whitespace-pre-wrap break-all px-3 py-2.5 max-h-40 overflow-y-auto scroll-polite">
                                    <span
                                      className={cn(
                                        "select-none",
                                        step.kind === "firecrawl"
                                          ? "text-sky-600 dark:text-sky-400"
                                          : "text-emerald-600 dark:text-emerald-400"
                                      )}
                                    >
                                      ${" "}
                                    </span>
                                    <span
                                      className={cn(
                                        step.kind === "firecrawl"
                                          ? "text-sky-700 dark:text-sky-300"
                                          : "text-emerald-700 dark:text-emerald-300"
                                      )}
                                    >
                                      {commandText(step, i)}
                                    </span>
                                  </pre>
                                </div>

                                {showTokens && (
                                  <p className="mt-1.5 text-[11px] text-muted-foreground leading-relaxed">
                                    {t("wt.templateNote")}
                                  </p>
                                )}

                                {/* you'll see */}
                                {see && (
                                  <div className="mt-2.5 rounded-lg border border-emerald-500/30 bg-emerald-500/5 px-3 py-2 flex items-start gap-2">
                                    <Eye className="size-3.5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                                    <p className="text-[13px] leading-relaxed text-emerald-800 dark:text-emerald-200">
                                      <span className="font-semibold">
                                        {t("wt.youWillSee")}:{" "}
                                      </span>
                                      {see}
                                    </p>
                                  </div>
                                )}

                                {/* dependency failure note */}
                                {st.phase === "failed" && st.note && (
                                  <div className="mt-2.5 rounded-lg border border-rose-500/30 bg-rose-500/5 px-3 py-2 text-[13px] text-rose-700 dark:text-rose-300">
                                    {st.note}
                                  </div>
                                )}

                                {/* firecrawl result rendering */}
                                {st.fc && step.kind === "firecrawl" && (
                                  <FirecrawlResult state={st} step={step} t={t} />
                                )}

                                {/* workbench result rendering */}
                                {st.result && step.kind !== "firecrawl" && (
                                  <div
                                    className={cn(
                                      "mt-2.5 rounded-lg border overflow-hidden",
                                      st.matched
                                        ? "border-emerald-500/30 bg-emerald-500/5"
                                        : "border-rose-500/30 bg-rose-500/5"
                                    )}
                                  >
                                    <div className="flex items-center gap-2 flex-wrap px-3 py-2 border-b border-border/50">
                                      {st.matched ? (
                                        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-700 dark:text-emerald-300">
                                          <Check className="size-3.5" />
                                          {t("wt.stepOk")}
                                        </span>
                                      ) : (
                                        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-rose-600 dark:text-rose-400">
                                          <X className="size-3.5" />
                                          {t("wt.stepMismatch")}
                                        </span>
                                      )}
                                      <span className="ml-auto flex items-center gap-1.5">
                                        <StatusBadge status={statusOf(st.result)} />
                                        <ExitBadge code={st.result.exitCode} />
                                        <span className="font-mono text-[11px] text-muted-foreground">
                                          {st.result.durationMs} {t("common.ms")}
                                        </span>
                                      </span>
                                    </div>
                                    {step.pick && (
                                      <div className="px-3 py-2 flex items-center gap-2 flex-wrap border-b border-border/50">
                                        <span className="text-xs text-muted-foreground">
                                          {pickLabel}:
                                        </span>
                                        <code
                                          className={cn(
                                            "font-mono text-xs rounded-md px-1.5 py-0.5 border max-w-full break-all",
                                            st.matched
                                              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-700 dark:text-emerald-300"
                                              : "bg-rose-500/10 border-rose-500/30 text-rose-700 dark:text-rose-300"
                                          )}
                                        >
                                          {formatPick(picked)}
                                        </code>
                                        {step.expectStatus && (
                                          <span className="text-[10px] text-muted-foreground">
                                            {t("wt.expected", { status: step.expectStatus })}
                                          </span>
                                        )}
                                      </div>
                                    )}
                                    <div className="px-3 py-2">
                                      <button
                                        type="button"
                                        onClick={() =>
                                          setExpanded((prev) => ({
                                            ...prev,
                                            [key]: !prev[key],
                                          }))
                                        }
                                        className="inline-flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground transition-colors"
                                      >
                                        <ChevronDown
                                          className={cn(
                                            "size-3.5 transition-transform",
                                            expanded[key] && "rotate-180"
                                          )}
                                        />
                                        {t("wt.rawOutput")}
                                      </button>
                                      {expanded[key] && (
                                        <div className="mt-2 rounded-lg border border-border bg-muted/30 p-3 max-h-72 overflow-y-auto overflow-x-auto scroll-polite">
                                          {st.result.json ? (
                                            <JsonViewer data={st.result.json} />
                                          ) : (
                                            <pre className="font-mono text-xs whitespace-pre-wrap break-all">
                                              {st.result.stdout ||
                                                st.result.stderr ||
                                                "(no output)"}
                                            </pre>
                                          )}
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                )}
                              </>
                            )}
                          </div>
                        </div>
                      </li>
                    )
                  })}
                </ol>
              </section>
            )
          })}
        </div>

        <p className="text-xs text-muted-foreground px-1 leading-relaxed">{t("wt.note")}</p>
      </div>
    </div>
  )
}

/* ── Firecrawl step result panel ─────────────────────────────────────── */

function FirecrawlResult({
  state,
  step,
  t,
}: {
  state: StepState
  step: WalkthroughStep
  t: (key: string, vars?: Record<string, string | number>) => string
}) {
  const fc = state.fc
  if (!fc) return null
  const ok = state.matched

  if (step.action === "search") {
    const results = (fc.results as FirecrawlSearchResult[] | undefined) ?? []
    return (
      <div
        className={cn(
          "mt-2.5 rounded-lg border overflow-hidden",
          ok ? "border-sky-500/30 bg-sky-500/5" : "border-rose-500/30 bg-rose-500/5"
        )}
      >
        <div className="flex items-center gap-2 flex-wrap px-3 py-2 border-b border-border/50">
          <Search className="size-3.5 text-sky-600 dark:text-sky-400" />
          <span className="text-xs font-medium text-sky-700 dark:text-sky-300">
            {t("fc.searchResults", { n: results.length })}
          </span>
          <span className="ml-auto font-mono text-[11px] text-muted-foreground">
            {t("fc.liveWeb")}
          </span>
        </div>
        <ul className="divide-y divide-border/50">
          {results.slice(0, 5).map((r, idx) => (
            <li key={`${r.url}-${idx}`} className="px-3 py-2">
              <a
                href={r.url}
                target="_blank"
                rel="noreferrer"
                className="text-[13px] font-medium text-foreground hover:text-emerald-600 dark:hover:text-emerald-400 leading-snug"
              >
                {r.title || r.url}
              </a>
              <p className="font-mono text-[10.5px] text-muted-foreground mt-0.5 break-all">
                {r.url}
              </p>
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

  if (step.action === "scrape") {
    const quote = typeof fc.quote === "string" ? fc.quote : null
    const excerpt = typeof fc.excerpt === "string" ? fc.excerpt : ""
    const markdown = typeof fc.markdown === "string" ? fc.markdown : ""
    return (
      <div
        className={cn(
          "mt-2.5 rounded-lg border overflow-hidden",
          ok ? "border-sky-500/30 bg-sky-500/5" : "border-rose-500/30 bg-rose-500/5"
        )}
      >
        <div className="flex items-center gap-2 flex-wrap px-3 py-2 border-b border-border/50">
          <Globe className="size-3.5 text-sky-600 dark:text-sky-400" />
          <span className="text-xs font-medium text-sky-700 dark:text-sky-300 truncate">
            {String(fc.title ?? fc.url ?? "")}
          </span>
          <span className="ml-auto flex items-center gap-1.5">
            {fc.quoteFound === true && (
              <Badge
                variant="outline"
                className="font-mono text-[9px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30"
              >
                <Check className="size-2.5" /> {t("fc.quoteFound")}
              </Badge>
            )}
            <Badge
              variant="outline"
              className="font-mono text-[9px] bg-muted text-muted-foreground border-border"
            >
              {String(fc.markdownLength ?? 0).toLocaleString()} chars
            </Badge>
          </span>
        </div>
        {quote && (
          <div className="px-3 py-2 border-b border-border/50">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-1">
              {t("fc.markedQuote")}
            </p>
            <p className="text-[13px] leading-relaxed text-foreground/85 border-l-2 border-emerald-500/50 pl-2.5">
              “{quote}”
            </p>
          </div>
        )}
        {excerpt && (
          <div className="px-3 py-2 border-b border-border/50">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-1">
              {t("fc.excerptForLedger")}
            </p>
            <p className="font-mono text-[11px] leading-relaxed text-muted-foreground break-all">
              {excerpt.slice(0, 420)}
              {excerpt.length > 420 ? " …" : ""}
            </p>
          </div>
        )}
        <details className="px-3 py-2">
          <summary className="text-[11px] text-muted-foreground cursor-pointer hover:text-foreground transition-colors">
            {t("fc.pagePreview")}
          </summary>
          <pre className="mt-2 rounded-lg border border-border bg-muted/30 p-3 font-mono text-[10.5px] leading-relaxed whitespace-pre-wrap break-words max-h-64 overflow-y-auto scroll-polite">
            {markdown.slice(0, 2500)}
            {markdown.length > 2500 ? "\n…" : ""}
          </pre>
        </details>
      </div>
    )
  }

  // map / extract / crawl — generic JSON view
  return (
    <div
      className={cn(
        "mt-2.5 rounded-lg border overflow-hidden",
        ok ? "border-sky-500/30 bg-sky-500/5" : "border-rose-500/30 bg-rose-500/5"
      )}
    >
      <div className="px-3 py-3 max-h-72 overflow-y-auto scroll-polite">
        <JsonViewer data={fc} />
      </div>
    </div>
  )
}
