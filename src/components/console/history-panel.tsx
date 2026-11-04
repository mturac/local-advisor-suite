"use client"

import { Fragment, useEffect, useState } from "react"
import { History, RefreshCw } from "lucide-react"
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { RunLogEntry } from "@/lib/console-types"
import { ExitBadge, StatusBadge } from "./status-badge"
import { JsonViewer } from "./json-viewer"

function timeAgo(iso: string) {
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000))
  if (seconds < 60) return `${seconds}s ago`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  return `${Math.floor(seconds / 3600)}h ago`
}

export function HistoryPanel({ refreshKey }: { refreshKey: number }) {
  const [logs, setLogs] = useState<RunLogEntry[] | null>(null)
  const [expanded, setExpanded] = useState<number | null>(null)

  async function load() {
    try {
      const res = await fetch("/api/history")
      const data = await res.json()
      if (res.ok) setLogs(data.logs)
    } catch {
      setLogs([])
    }
  }

  useEffect(() => {
    fetch("/api/history")
      .then(async (res) => {
        const data = await res.json()
        if (res.ok) setLogs(data.logs)
      })
      .catch(() => setLogs([]))
  }, [refreshKey])

  return (
    <Card>
      <CardHeader className="pb-4">
        <CardTitle className="text-base flex items-center gap-2">
          <History className="size-4 text-emerald-500" />
          Run history
          <Button
            variant="outline"
            size="sm"
            className="ml-auto gap-2"
            onClick={() => void load()}
          >
            <RefreshCw className="size-3.5" />
            Refresh
          </Button>
        </CardTitle>
        <CardDescription>
          Every command executed through the console, newest first (persisted in SQLite).
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!logs && <p className="text-sm text-muted-foreground py-6 text-center">Loading…</p>}
        {logs && logs.length === 0 && (
          <p className="text-sm text-muted-foreground py-6 text-center">
            No runs yet — go fire a command from the Runner tab.
          </p>
        )}
        {logs && logs.length > 0 && (
          <div className="rounded-lg border border-border overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">When</TableHead>
                  <TableHead className="w-48">Command</TableHead>
                  <TableHead className="w-20">Status</TableHead>
                  <TableHead className="w-16">Exit</TableHead>
                  <TableHead className="w-20">Duration</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((log) => (
                  <Fragment key={log.id}>
                    <TableRow
                      className="cursor-pointer"
                      onClick={() => setExpanded(expanded === log.id ? null : log.id)}
                    >
                      <TableCell className="text-xs text-muted-foreground">
                        {timeAgo(log.createdAt)}
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {log.command}
                        {log.argsJson !== "[]" && (
                          <span className="text-muted-foreground"> +{JSON.parse(log.argsJson).length}</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={log.status} />
                      </TableCell>
                      <TableCell>
                        <ExitBadge code={log.exitCode} />
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground font-mono">
                        {log.durationMs} ms
                      </TableCell>
                    </TableRow>
                    {expanded === log.id && (
                      <TableRow>
                        <TableCell colSpan={5} className="bg-muted/30 p-4">
                          <div className="max-h-80 overflow-y-auto rounded-lg border border-border bg-background p-3">
                            <JsonViewer data={safeParse(log.stdout) ?? (log.stdout || log.stderr || "(empty)")} />
                          </div>
                          <div className="mt-2 flex items-center gap-2">
                            <Badge variant="secondary" className="font-mono text-[10px]">
                              argv: {log.argsJson}
                            </Badge>
                            <span className="text-[10px] text-muted-foreground font-mono">
                              {new Date(log.createdAt).toLocaleString()}
                            </span>
                          </div>
                        </TableCell>
                      </TableRow>
                    )}
                  </Fragment>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function safeParse(text: string): unknown {
  const trimmed = text.trim()
  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    try {
      return JSON.parse(trimmed)
    } catch {
      return null
    }
  }
  return null
}
