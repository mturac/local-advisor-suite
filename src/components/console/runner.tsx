"use client"

import { useMemo, useState } from "react"
import {
  Loader2,
  Play,
  Plus,
  RotateCcw,
  Search,
  Sparkles,
  Terminal,
  TriangleAlert,
  X,
  Zap,
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
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { cn } from "@/lib/utils"
import { pickLocalized, useLang } from "@/lib/i18n"
import type { ArgSpec, Catalog, CommandSpec, RunResponse } from "@/lib/console-types"
import { SCENARIO_COUNT, SCENARIO_GROUPS, type Scenario } from "@/lib/scenarios"
import { ExitBadge, StatusBadge } from "./status-badge"
import { JsonViewer } from "./json-viewer"

type FormValues = Record<string, string | boolean | string[]>

function defaultValues(spec: CommandSpec): FormValues {
  const values: FormValues = {}
  for (const arg of spec.args) {
    if (arg.kind === "switch") values[arg.dest] = false
    else if (arg.kind === "multi") values[arg.dest] = []
    else values[arg.dest] = ""
  }
  return values
}

function buildArgv(spec: CommandSpec, values: FormValues, extra: string): string[] {
  const argv: string[] = []
  for (const arg of spec.args) {
    const value = values[arg.dest]
    if (arg.kind === "switch") {
      if (value === true) argv.push(arg.flags[0])
    } else if (arg.kind === "multi") {
      for (const v of (value as string[]) || []) {
        if (v.trim() !== "") argv.push(arg.flags[0], v.trim())
      }
    } else if (typeof value === "string" && value.trim() !== "") {
      if (arg.kind === "positional") argv.push(value.trim())
      else argv.push(arg.flags[0], value.trim())
    }
  }
  if (extra.trim() !== "") {
    argv.push(...splitArgs(extra))
  }
  return argv
}

function splitArgs(input: string): string[] {
  const out: string[] = []
  let current = ""
  let quote: string | null = null
  for (const ch of input) {
    if (quote) {
      if (ch === quote) quote = null
      else current += ch
    } else if (ch === '"' || ch === "'") {
      quote = ch
    } else if (/\s/.test(ch)) {
      if (current) out.push(current)
      current = ""
    } else {
      current += ch
    }
  }
  if (current) out.push(current)
  return out
}

export function Runner({
  catalog,
  onRan,
}: {
  catalog: Catalog | null
  onRan?: () => void
}) {
  const { lang, t } = useLang()
  const [query, setQuery] = useState("")
  const [selected, setSelected] = useState<string | null>(null)
  const [values, setValues] = useState<FormValues>({})
  const [extra, setExtra] = useState("")
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<RunResponse | null>(null)

  const spec = useMemo(
    () => catalog?.commands.find((c) => c.name === selected) ?? null,
    [catalog, selected]
  )

  const grouped = useMemo(() => {
    const groups = new Map<string, CommandSpec[]>()
    const q = query.trim().toLowerCase()
    for (const cmd of catalog?.commands ?? []) {
      if (q && !cmd.name.includes(q) && !cmd.help.toLowerCase().includes(q)) continue
      const list = groups.get(cmd.category) ?? []
      list.push(cmd)
      groups.set(cmd.category, list)
    }
    return [...groups.entries()].sort((a, b) => a[0].localeCompare(b[0]))
  }, [catalog, query])

  function select(name: string, presetValues?: FormValues) {
    const next = catalog?.commands.find((c) => c.name === name) ?? null
    setSelected(name)
    setValues(presetValues ?? (next ? defaultValues(next) : {}))
    setExtra("")
    setResult(null)
  }

  async function run(commandName?: string, argv?: string[]) {
    const cmd = commandName ?? selected
    if (!cmd) return
    setRunning(true)
    setResult(null)
    try {
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd, argv: argv ?? buildArgv(spec!, values, extra) }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`)
      setResult(data as RunResponse)
      onRan?.()
    } catch (err) {
      setResult({
        command: cmd,
        argv: [],
        exitCode: -1,
        stdout: "",
        stderr: String(err instanceof Error ? err.message : err),
        durationMs: 0,
        json: null,
        truncated: false,
        timedOut: false,
      })
    } finally {
      setRunning(false)
    }
  }

  /** Populate the form from a scenario the way argparse would parse its argv,
   *  so switches (--force) and repeated flags (--entity x --entity y) land in
   *  the right fields, then run it. */
  function applyScenario(scenario: Scenario) {
    const next = catalog?.commands.find((c) => c.name === scenario.command)
    if (!next) return
    const presetValues = defaultValues(next)
    let i = 0
    while (i < scenario.argv.length) {
      const flag = scenario.argv[i]
      const arg = next.args.find((a) => a.flags.includes(flag))
      if (arg?.kind === "switch") {
        presetValues[arg.dest] = true
        i += 1
      } else {
        const value = scenario.argv[i + 1] ?? ""
        if (arg) {
          if (arg.kind === "multi") {
            const list = (presetValues[arg.dest] as string[]) || []
            presetValues[arg.dest] = [...list, value]
          } else {
            presetValues[arg.dest] = value
          }
        }
        i += 2
      }
    }
    select(scenario.command, presetValues)
    void run(scenario.command, scenario.argv)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-4 items-start">
      {/* Command catalog */}
      <Card className="lg:sticky lg:top-[72px]">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Terminal className="size-4 text-emerald-500" />
            {t("runner.commands")}
            {catalog && (
              <Badge variant="secondary" className="font-mono text-xs ml-auto">
                {catalog.commands.length}
              </Badge>
            )}
          </CardTitle>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t("runner.search")}
              className="pl-8 h-9"
            />
          </div>
        </CardHeader>
        <CardContent className="pb-3">
          <ScrollArea className="h-[480px] pr-2">
            <div className="space-y-4">
              {grouped.map(([category, commands]) => (
                <div key={category}>
                  <div
                    lang="en"
                    className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-1.5 px-1"
                  >
                    {category}
                  </div>
                  <div className="space-y-0.5">
                    {commands.map((cmd) => (
                      <button
                        key={cmd.name}
                        onClick={() => select(cmd.name)}
                        className={cn(
                          "w-full text-left rounded-md px-2.5 py-1.5 transition-colors",
                          selected === cmd.name
                            ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300"
                            : "hover:bg-muted text-foreground"
                        )}
                      >
                        <div className="font-mono text-xs">{cmd.name}</div>
                        {cmd.help && (
                          <div className="text-[11px] text-muted-foreground line-clamp-1">
                            {cmd.help}
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
              {grouped.length === 0 && (
                <p className="text-sm text-muted-foreground px-1 py-8 text-center">
                  {t("runner.noMatch", { q: query })}
                </p>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Command form + output */}
      <div className="space-y-4 min-w-0">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2 flex-wrap">
              <Zap className="size-4 text-emerald-500" />
              {t("runner.examplesTitle")}
              <Badge
                variant="outline"
                className="font-mono text-[10px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30"
              >
                {SCENARIO_COUNT}
              </Badge>
            </CardTitle>
            <CardDescription className="text-xs leading-relaxed">
              {t("runner.examplesDesc")}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="max-h-[360px] pr-2">
              <div className="space-y-2.5">
                {SCENARIO_GROUPS.map((group) => (
                  <div
                    key={group.title}
                    className="grid grid-cols-1 sm:grid-cols-[118px_1fr] gap-x-3 gap-y-1"
                  >
                    <div
                      lang={lang}
                      className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground pt-1.5 truncate"
                    >
                      {pickLocalized(lang, group.title, group.titleTr)}
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {group.scenarios.map((s) => (
                        <button
                          key={s.command}
                          onClick={() => applyScenario(s)}
                          disabled={running}
                          title={`${pickLocalized(lang, s.note, s.noteTr)}\nworkbench ${s.command}${s.argv.length ? ` ${s.argv.join(" ")}` : ""}${s.resets ? `\n⚠ resets this ledger` : ""}`}
                          className={cn(
                            "inline-flex items-center gap-1 font-mono text-xs rounded-full border px-2.5 py-1 transition-colors disabled:opacity-50",
                            s.resets
                              ? "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300 hover:border-amber-500/70"
                              : "border-border bg-muted/50 hover:border-emerald-500/50 hover:text-emerald-600 dark:hover:text-emerald-400"
                          )}
                        >
                          {s.resets && <TriangleAlert className="size-3 shrink-0" />}
                          {s.label}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
            <p className="mt-3 text-[11px] text-muted-foreground flex items-start gap-1.5 leading-relaxed">
              <Sparkles className="size-3 shrink-0 text-emerald-500 mt-0.5" />
              {t("runner.amberNote")}
            </p>
          </CardContent>
        </Card>

        {spec ? (
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="font-mono text-base flex items-center gap-2">
                {spec.name}
              </CardTitle>
              <CardDescription>{spec.help}</CardDescription>
              <pre className="font-mono text-[11px] text-muted-foreground whitespace-pre-wrap break-all bg-muted/50 rounded-md p-2 border border-border">
                {spec.usage.replace(/^usage: /, "")}
              </pre>
            </CardHeader>
            <CardContent className="space-y-4">
              {spec.args.length === 0 && (
                <p className="text-sm text-muted-foreground">{t("runner.noArgs")}</p>
              )}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {spec.args.map((arg) => (
                  <ArgField
                    key={arg.dest}
                    arg={arg}
                    value={values[arg.dest]}
                    onChange={(v) =>
                      setValues((prev) => ({ ...prev, [arg.dest]: v }))
                    }
                  />
                ))}
              </div>
              <div className="space-y-2">
                <Label htmlFor="extra-args" className="text-xs text-muted-foreground">
                  {t("runner.extraArgs")}
                </Label>
                <Input
                  id="extra-args"
                  value={extra}
                  onChange={(e) => setExtra(e.target.value)}
                  placeholder='e.g. --strict --max-age-days 30'
                  className="font-mono text-xs h-9"
                />
              </div>
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <Button onClick={() => run()} disabled={running} className="gap-2">
                  {running ? (
                    <Loader2 className="size-4 animate-spin" />
                  ) : (
                    <Play className="size-4" />
                  )}
                  {t("wt.run")} {spec.name}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => select(spec.name)}
                  disabled={running}
                  className="gap-2"
                >
                  <RotateCcw className="size-4" />
                  {t("runner.resetArgs")}
                </Button>
                <code className="ml-auto font-mono text-[11px] text-muted-foreground truncate max-w-full">
                  workbench {buildArgv(spec, values, extra).join(" ") || spec.name}
                </code>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="py-16 text-center text-muted-foreground">
              <Terminal className="size-10 mx-auto mb-3 opacity-40" />
              <p className="text-sm">{t("runner.pickCommand")}</p>
            </CardContent>
          </Card>
        )}

        {result && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2 flex-wrap">
                {t("runner.output")}
                <StatusBadge
                  status={
                    result.json &&
                    typeof result.json === "object" &&
                    "status" in (result.json as Record<string, unknown>)
                      ? String((result.json as Record<string, unknown>).status)
                      : null
                  }
                />
                <ExitBadge code={result.exitCode} />
                <Badge variant="secondary" className="font-mono text-xs">
                  {result.durationMs} {t("common.ms")}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {result.json ? (
                <div className="rounded-lg border border-border bg-muted/30 p-3 overflow-x-auto max-h-[480px] overflow-y-auto scroll-polite">
                  <JsonViewer data={result.json} />
                </div>
              ) : (
                <pre className="font-mono text-xs whitespace-pre-wrap break-all rounded-lg border border-border bg-muted/30 p-3 max-h-[480px] overflow-y-auto scroll-polite">
                  {result.stdout || t("runner.noStdout")}
                </pre>
              )}
              {result.stderr.trim() !== "" && (
                <details className="rounded-lg border border-rose-500/30 bg-rose-500/5 p-3">
                  <summary className="text-xs font-medium text-rose-600 dark:text-rose-400 cursor-pointer">
                    stderr
                  </summary>
                  <pre className="font-mono text-xs whitespace-pre-wrap break-all mt-2 text-muted-foreground">
                    {result.stderr}
                  </pre>
                </details>
              )}
              {result.timedOut && (
                <p className="text-xs text-rose-600 dark:text-rose-400">{t("runner.timedOut")}</p>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

function ArgField({
  arg,
  value,
  onChange,
}: {
  arg: ArgSpec
  value: string | boolean | string[] | undefined
  onChange: (v: string | boolean | string[]) => void
}) {
  const { t } = useLang()
  const flag = arg.flags[0] ?? arg.dest
  const label = (
    <Label className="font-mono text-xs flex items-center gap-1.5">
      {flag}
      {arg.required && (
        <span className="text-rose-500" title={t("runner.required")}>
          *
        </span>
      )}
      {arg.choices && (
        <span className="text-[10px] text-muted-foreground font-sans">
          ({arg.choices.join(" | ")})
        </span>
      )}
    </Label>
  )

  if (arg.kind === "switch") {
    return (
      <div className="flex items-center justify-between gap-3 rounded-lg border border-border p-3">
        <div className="min-w-0">
          {label}
          <p className="text-[11px] text-muted-foreground truncate">{arg.help}</p>
        </div>
        <Switch
          checked={value === true}
          onCheckedChange={onChange}
          aria-label={flag}
        />
      </div>
    )
  }

  if (arg.kind === "multi") {
    const items = (value as string[]) || []
    return (
      <div className="space-y-1.5">
        {label}
        {items.map((item, i) => (
          <div key={i} className="flex gap-1.5">
            <Input
              value={item}
              onChange={(e) => {
                const next = [...items]
                next[i] = e.target.value
                onChange(next)
              }}
              className="font-mono text-xs h-9"
              aria-label={`${flag} ${i + 1}`}
            />
            <Button
              variant="ghost"
              size="icon"
              className="size-9 shrink-0 text-muted-foreground"
              onClick={() => onChange(items.filter((_, j) => j !== i))}
              aria-label={`Remove ${flag} ${i + 1}`}
            >
              <X className="size-4" />
            </Button>
          </div>
        ))}
        <Button
          variant="outline"
          size="sm"
          className="h-8 text-xs gap-1"
          onClick={() => onChange([...items, ""])}
        >
          <Plus className="size-3.5" />
          {t("runner.addValue")}
        </Button>
        {arg.help && <p className="text-[11px] text-muted-foreground">{arg.help}</p>}
      </div>
    )
  }

  return (
    <div className="space-y-1.5">
      {label}
      {arg.choices ? (
        <Select
          value={(value as string) || undefined}
          onValueChange={onChange}
        >
          <SelectTrigger className="font-mono text-xs h-9 w-full">
            <SelectValue placeholder="—" />
          </SelectTrigger>
          <SelectContent>
            {arg.choices.map((choice) => (
              <SelectItem key={choice} value={choice} className="font-mono text-xs">
                {choice}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      ) : (
        <Input
          value={(value as string) ?? ""}
          onChange={(e) => onChange(e.target.value)}
          placeholder={
            arg.default !== null && arg.default !== undefined && arg.default !== ""
              ? String(arg.default)
              : arg.metavar || flag
          }
          className="font-mono text-xs h-9"
          aria-label={flag}
        />
      )}
      {arg.help && <p className="text-[11px] text-muted-foreground">{arg.help}</p>}
    </div>
  )
}
