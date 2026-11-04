"use client"

import { useEffect, useState } from "react"
import {
  Database,
  FileOutput,
  FolderOpen,
  Loader2,
  RotateCcw,
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import type { LedgerFile, WorkspaceState } from "@/lib/console-types"
import { JsonViewer } from "./json-viewer"

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  return `${(bytes / 1024).toFixed(1)} KB`
}

function countItems(ledger: LedgerFile): string {
  const json = ledger.json as Record<string, unknown> | null
  if (!json || typeof json !== "object") return ""
  for (const key of ["sources", "claims", "gaps", "entries", "stories", "criteria", "tasks", "findings", "hypotheses"]) {
    const value = json[key]
    if (Array.isArray(value)) return `${value.length} ${key}`
  }
  return `${Object.keys(json).length} keys`
}

export function WorkspacePanel() {
  const [state, setState] = useState<WorkspaceState | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [resetting, setResetting] = useState(false)
  const [active, setActive] = useState<LedgerFile | null>(null)

  async function load() {
    setError(null)
    try {
      const res = await fetch("/api/workspace")
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`)
      setState(data)
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err))
    }
  }

  useEffect(() => {
    void load()
  }, [])

  async function reset() {
    setResetting(true)
    try {
      const res = await fetch("/api/workspace", { method: "POST" })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`)
      setState(data.state)
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err))
    } finally {
      setResetting(false)
    }
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-10 text-center text-sm text-rose-600 dark:text-rose-400">
          {error}
        </CardContent>
      </Card>
    )
  }

  if (!state) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-40 animate-pulse rounded-xl bg-muted" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2 justify-between">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-sm text-muted-foreground mr-1">Hosts in workspace:</span>
          {state.hosts.map((host) => (
            <Badge
              key={host}
              variant="outline"
              className="font-mono text-xs bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30"
            >
              {host}
            </Badge>
          ))}
        </div>
        <Button variant="outline" size="sm" onClick={() => void reset()} disabled={resetting} className="gap-2">
          {resetting ? (
            <Loader2 className="size-3.5 animate-spin" />
          ) : (
            <RotateCcw className="size-3.5" />
          )}
          {resetting ? "Reseeding (~10 s)…" : "Reset workspace"}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Database className="size-4 text-emerald-500" />
              State ledgers
            </CardTitle>
            <CardDescription className="font-mono text-[11px] truncate">
              {state.stateDir}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-1.5">
            {state.ledgers.map((ledger) => (
              <button
                key={ledger.name}
                onClick={() => setActive(ledger)}
                className="w-full flex items-center justify-between gap-2 rounded-md px-2.5 py-2 hover:bg-muted transition-colors text-left"
              >
                <span className="font-mono text-xs truncate">{ledger.name}</span>
                <span className="flex items-center gap-2 shrink-0">
                  {countItems(ledger) && (
                    <span className="text-[11px] text-muted-foreground">{countItems(ledger)}</span>
                  )}
                  <span className="text-[11px] text-muted-foreground">{formatSize(ledger.size)}</span>
                </span>
              </button>
            ))}
            {state.ledgers.length === 0 && (
              <p className="text-sm text-muted-foreground py-4 text-center">
                No ledgers yet — reset the workspace to seed demo data.
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <FileOutput className="size-4 text-emerald-500" />
              Generated artifacts
            </CardTitle>
            <CardDescription>
              ADRs, reports and handoff packs written by workbench commands.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-1.5">
            {state.outputs.map((file) => (
              <div
                key={file.path}
                className="flex items-center justify-between gap-2 rounded-md px-2.5 py-2 bg-muted/30"
              >
                <span className="font-mono text-xs truncate">{file.name}</span>
                <span className="text-[11px] text-muted-foreground shrink-0">
                  {formatSize(file.size)}
                </span>
              </div>
            ))}
            {state.outputs.length === 0 && (
              <p className="text-sm text-muted-foreground py-4 text-center">
                No artifacts yet — try <span className="font-mono text-xs">adr-new</span> or{" "}
                <span className="font-mono text-xs">research-pack</span>.
              </p>
            )}
            <div className="pt-2 text-[11px] text-muted-foreground flex items-center gap-1.5">
              <FolderOpen className="size-3.5" />
              Also in workspace: demo-project/, decision-matrix.json, AGENTS.md
            </div>
          </CardContent>
        </Card>
      </div>

      <Dialog open={!!active} onOpenChange={(open) => !open && setActive(null)}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="font-mono">{active?.name}</DialogTitle>
            <DialogDescription>State ledger JSON</DialogDescription>
          </DialogHeader>
          <div className="rounded-lg border border-border bg-muted/30 p-3 overflow-x-auto">
            <JsonViewer data={active?.json ?? `(unparseable, ${formatSize(active?.size ?? 0)})`} />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
