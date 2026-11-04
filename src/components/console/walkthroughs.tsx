"use client"

import { useMemo, useState } from "react"
import {
  Bug,
  Check,
  ChevronDown,
  Copy,
  Eye,
  FlaskConical,
  Gift,
  Loader2,
  MousePointerClick,
  Play,
  RotateCcw,
  Rocket,
  Scale,
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
  result: RunResponse | null
  /** true when exit code and status matched the step's expectation */
  matched: boolean
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

function stepMatched(step: WalkthroughStep, result: RunResponse): boolean {
  if (result.exitCode !== 0) return false
  if (step.expectStatus && statusOf(result) !== step.expectStatus) return false
  return true
}

function formatPick(value: unknown): string {
  if (typeof value === "boolean") return value ? "yes ✓" : "no"
  if (value === null || value === undefined) return "—"
  return String(value)
}

function fullCommand(step: WalkthroughStep): string {
  return `workbench ${step.command}${step.argv.length > 0 ? ` ${step.argv.join(" ")}` : ""}`
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

  const flowStates: StepState[] =
    states[flow.id] ?? flow.steps.map(() => ({ phase: "idle", result: null, matched: false }))

  const doneCount = flowStates.filter((s) => s.phase === "done").length
  const allDone = doneCount === flow.steps.length && flow.steps.length > 0

  function setStepState(index: number, next: Partial<StepState>) {
    setStates((prev) => {
      const current =
        prev[flow.id] ?? flow.steps.map(() => ({ phase: "idle" as Phase, result: null, matched: false }))
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
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: step.command, argv: step.argv }),
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
        command: step.command,
        argv: step.argv,
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

  function copyCommand(step: WalkthroughStep, key: string) {
    void navigator.clipboard?.writeText(fullCommand(step)).then(() => {
      setCopiedKey(key)
      window.setTimeout(() => setCopiedKey(null), 1500)
    })
  }

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

        <ol className="space-y-3">
          {flow.steps.map((step, i) => {
            const st = flowStates[i]
            const isRunning = stepRunning === i
            const key = `${flow.id}:${i}`
            const title = pickLocalized(lang, step.title, step.titleTr)
            const explain = pickLocalized(lang, step.explain, step.explainTr)
            const see = pickLocalized(lang, step.see, step.seeTr)
            const pickLabel = pickLocalized(lang, step.pickLabel, step.pickLabelTr)
            const picked =
              st.result?.json && step.pick ? resolvePick(st.result.json, step.pick) : undefined
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
                        st.phase === "idle" && "border-border text-muted-foreground bg-muted/50",
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
                    {i < flow.steps.length - 1 && (
                      <div className="step-rail-line w-px flex-1 mt-1.5" aria-hidden />
                    )}
                  </div>

                  {/* content */}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-2 flex-wrap">
                      <h3 className="text-[15px] font-semibold leading-snug">
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
                      </h3>
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
                    </div>

                    <p className="mt-1.5 text-sm leading-relaxed text-foreground/80">{explain}</p>

                    {/* command */}
                    <div className="mt-2.5 term-block rounded-lg overflow-hidden">
                      <div className="flex items-center justify-between gap-2 pl-3 pr-1.5 py-1 border-b border-border/60">
                        <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                          {t("wt.commandLabel")}
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
                        <span className="text-emerald-600 dark:text-emerald-400 select-none">
                          ${" "}
                        </span>
                        <span className="text-emerald-700 dark:text-emerald-300">
                          workbench {step.command}
                        </span>
                        {step.argv.length > 0 && (
                          <span className="text-muted-foreground">
                            {" "}
                            {step.argv
                              .map((a) =>
                                /\s/.test(a) ? `"${a}"` : a
                              )
                              .join(" ")}
                          </span>
                        )}
                      </pre>
                    </div>

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

                    {/* result */}
                    {st.result && (
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
                            <span className="text-xs text-muted-foreground">{pickLabel}:</span>
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
                                  {st.result.stdout || st.result.stderr || "(no output)"}
                                </pre>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </li>
            )
          })}
        </ol>

        <p className="text-xs text-muted-foreground px-1 leading-relaxed">{t("wt.note")}</p>
      </div>
    </div>
  )
}
