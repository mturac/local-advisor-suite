"use client"

import { useMemo, useState } from "react"
import {
  Bug,
  Check,
  ChevronDown,
  CircleDashed,
  FlaskConical,
  Loader2,
  Play,
  Rocket,
  RotateCcw,
  Scale,
  Trophy,
  X,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { cn } from "@/lib/utils"
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
  if (typeof value === "boolean") return value ? "yes" : "no"
  if (value === null || value === undefined) return "—"
  return String(value)
}

export function Walkthroughs({ onRan }: { onRan?: () => void }) {
  const [flowId, setFlowId] = useState<string>(WALKTHROUGH_FLOWS[0].id)
  const [states, setStates] = useState<Record<string, StepState[]>>({})
  const [runningAll, setRunningAll] = useState(false)
  const [stepRunning, setStepRunning] = useState<number | null>(null)
  const [resetFirst, setResetFirst] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

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
      const current = prev[flow.id] ?? flow.steps.map(() => ({ phase: "idle" as Phase, result: null, matched: false }))
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
            `Step ${i + 1} (“${flow.steps[i].title}”) did not produce the expected result — the run stopped there.`
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

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-4 items-start">
      {/* Flow picker */}
      <Card className="lg:sticky lg:top-20">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Play className="size-4 text-emerald-500" />
            Walkthroughs
            <Badge variant="secondary" className="font-mono text-xs ml-auto">
              {WALKTHROUGH_FLOWS.length}
            </Badge>
          </CardTitle>
          <CardDescription className="text-xs">
            Complete stories, start to finish. Each one does real work against the
            demo workspace and ends with a real artifact.
          </CardDescription>
        </CardHeader>
        <CardContent className="pb-3">
          <div className="space-y-2">
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
                        "size-8 rounded-lg flex items-center justify-center shrink-0",
                        complete
                          ? "bg-emerald-500/20"
                          : "bg-muted"
                      )}
                    >
                      {complete ? (
                        <Trophy className="size-4 text-emerald-600 dark:text-emerald-400" />
                      ) : (
                        <Icon className="size-4 text-muted-foreground" />
                      )}
                    </div>
                    <div className="min-w-0">
                      <div className="text-sm font-medium leading-tight">{f.title}</div>
                      <div className="mt-1 text-[11px] text-muted-foreground">
                        {f.steps.length} steps · ends with {f.outcome}
                      </div>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Stepper */}
      <div className="space-y-4 min-w-0">
        <Card>
          <CardHeader className="pb-4">
            <div className="flex items-start justify-between gap-3 flex-wrap">
              <div className="min-w-0">
                <CardTitle className="text-base">{flow.title}</CardTitle>
                <CardDescription className="mt-1.5 max-w-2xl">
                  {flow.subtitle}
                </CardDescription>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Button
                  onClick={() => void runAll()}
                  disabled={runningAll || resetting}
                  className="gap-2"
                >
                  {runningAll ? (
                    <Loader2 className="size-4 animate-spin" />
                  ) : (
                    <Play className="size-4" />
                  )}
                  {runningAll ? "Running…" : "Run all steps"}
                </Button>
                <Button
                  variant="outline"
                  onClick={resetFlow}
                  disabled={runningAll || resetting}
                  className="gap-2"
                >
                  <RotateCcw className="size-4" />
                  Clear
                </Button>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-2 pt-1">
              <Badge
                variant="outline"
                className="font-mono text-[10px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 gap-1"
              >
                <Trophy className="size-3" />
                {flow.outcome}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {flow.steps.length} steps · every click runs the real CLI
              </span>
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
                  {resetting ? "Reseeding…" : "Reset workspace first"}
                </Label>
              </div>
            </div>
            {(flow.steps.length > 0 || runningAll) && (
              <div className="flex items-center gap-2 pt-1">
                <div className="h-1.5 flex-1 rounded-full bg-muted overflow-hidden">
                  <div
                    className="h-full rounded-full bg-emerald-500 transition-all"
                    style={{ width: `${(doneCount / flow.steps.length) * 100}%` }}
                  />
                </div>
                <span className="font-mono text-[11px] text-muted-foreground shrink-0">
                  {doneCount}/{flow.steps.length}
                </span>
              </div>
            )}
          </CardHeader>
        </Card>

        {allDone && (
          <div className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 p-4 flex items-start gap-3">
            <Trophy className="size-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
            <div className="text-sm">
              <span className="font-medium text-emerald-700 dark:text-emerald-300">
                Flow complete.
              </span>{" "}
              All {flow.steps.length} steps ran against the real CLI and the story
              ended with <span className="font-medium">{flow.outcome}</span>. Open
              the Workspace tab to see the files this run produced.
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-rose-500/30 bg-rose-500/5 p-3 text-sm text-rose-600 dark:text-rose-400">
            {error}
          </div>
        )}

        <div className="space-y-3">
          {flow.steps.map((step, i) => {
            const st = flowStates[i]
            const isRunning = stepRunning === i
            const key = `${flow.id}:${i}`
            const picked =
              st.result?.json && step.pick
                ? resolvePick(st.result.json, step.pick)
                : undefined
            const hasPick = st.phase !== "idle" && st.phase !== "running" && step.pick
            return (
              <Card
                key={key}
                className={cn(
                  "transition-colors",
                  st.phase === "done" && step.deliverable && "border-emerald-500/40",
                  st.phase === "failed" && "border-rose-500/40",
                  isRunning && "border-emerald-500/50"
                )}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div
                      className={cn(
                        "size-8 rounded-full border flex items-center justify-center shrink-0 font-mono text-xs",
                        st.phase === "idle" &&
                          "border-border text-muted-foreground bg-muted/50",
                        isRunning &&
                          "border-emerald-500/50 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10",
                        st.phase === "done" &&
                          "border-emerald-500/50 bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
                        st.phase === "failed" &&
                          "border-rose-500/50 bg-rose-500/10 text-rose-600 dark:text-rose-400"
                      )}
                    >
                      {isRunning ? (
                        <Loader2 className="size-4 animate-spin" />
                      ) : st.phase === "done" ? (
                        <Check className="size-4" />
                      ) : st.phase === "failed" ? (
                        <X className="size-4" />
                      ) : (
                        <CircleDashed className="size-3.5" />
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-start justify-between gap-2 flex-wrap">
                        <h3 className="text-sm font-semibold leading-snug">
                          <span className="text-muted-foreground font-mono text-xs mr-1.5">
                            {String(i + 1).padStart(2, "0")}
                          </span>
                          {step.title}
                          {step.deliverable && (
                            <Badge
                              variant="outline"
                              className="ml-2 font-mono text-[9px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 gap-1 align-middle"
                            >
                              <Trophy className="size-2.5" />
                              deliverable
                            </Badge>
                          )}
                        </h3>
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-7 text-xs gap-1.5 shrink-0"
                          onClick={() => void executeStep(step, i)}
                          disabled={runningAll || stepRunning !== null || resetting}
                        >
                          <Play className="size-3" />
                          Run
                        </Button>
                      </div>
                      <p className="mt-1.5 text-[13px] text-muted-foreground leading-relaxed">
                        {step.explain}
                      </p>
                      <pre className="mt-2.5 font-mono text-[11px] text-muted-foreground whitespace-pre-wrap break-all bg-muted/50 rounded-md p-2 border border-border">
                        <span className="text-emerald-600 dark:text-emerald-400">
                          workbench
                        </span>{" "}
                        {step.command}
                        {step.argv.length > 0 && ` ${step.argv.join(" ")}`}
                      </pre>

                      {hasPick && (
                        <div className="mt-2.5 flex items-center gap-2 flex-wrap">
                          <span className="text-[11px] text-muted-foreground">
                            {step.pickLabel ?? step.pick}:
                          </span>
                          <code
                            className={cn(
                              "font-mono text-xs rounded-md px-1.5 py-0.5 border",
                              st.matched
                                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-700 dark:text-emerald-300"
                                : "bg-rose-500/10 border-rose-500/30 text-rose-700 dark:text-rose-300"
                            )}
                          >
                            {formatPick(picked)}
                          </code>
                          {step.expectStatus && (
                            <span className="text-[10px] text-muted-foreground">
                              expected status: {step.expectStatus}
                            </span>
                          )}
                        </div>
                      )}

                      {st.result && (
                        <div className="mt-2.5">
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
                            raw output
                            <StatusBadge status={statusOf(st.result)} />
                            <ExitBadge code={st.result.exitCode} />
                            <span className="font-mono">{st.result.durationMs} ms</span>
                          </button>
                          {expanded[key] && (
                            <div className="mt-2 rounded-lg border border-border bg-muted/30 p-3 max-h-72 overflow-y-auto">
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
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        <p className="text-[11px] text-muted-foreground px-1">
          Steps run in order — each one builds on the ledger state the previous
          step wrote. The command line under every step is exactly what runs; you
          can replay any of it by hand in the Runner tab.
        </p>
      </div>
    </div>
  )
}
