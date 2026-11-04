"use client"

import { useCallback, useEffect, useState } from "react"
import { Activity, HeartPulse, Loader2, ShieldCheck, Stethoscope } from "lucide-react"
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
import type { RunResponse } from "@/lib/console-types"
import { useLang } from "@/lib/i18n"
import { StatusBadge } from "./status-badge"
import { JsonViewer } from "./json-viewer"

interface DoctorJson {
  status: string
  runtime_version: string
  project_root: string
  hosts_detected: string[]
  skills_installed: number
  checks: { id: string; status: string; detail: string }[]
}

export function DoctorPanel({ onRan }: { onRan?: () => void }) {
  const { t } = useLang()
  const [result, setResult] = useState<RunResponse | null>(null)
  const [selfcheck, setSelfcheck] = useState<RunResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadingSc, setLoadingSc] = useState(false)

  const runCommand = useCallback(
    async (command: string, argv: string[]) => {
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command, argv }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`)
      return data as RunResponse
    },
    []
  )

  useEffect(() => {
    runCommand("doctor", [])
      .then(setResult)
      .catch(() => setResult(null))
      .finally(() => setLoading(false))
  }, [runCommand])

  const doctor = result?.json as DoctorJson | undefined

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-4">
          <CardTitle className="text-base flex items-center gap-2">
            <Stethoscope className="size-4 text-emerald-500" />
            {t("doctor.title")}
            {doctor && <StatusBadge status={doctor.status} className="ml-1" />}
            <Button
              variant="outline"
              size="sm"
              className="ml-auto gap-2"
              disabled={loading}
              onClick={() => {
                setLoading(true)
                runCommand("doctor", [])
                  .then(setResult)
                  .catch(() => setResult(null))
                  .finally(() => setLoading(false))
                onRan?.()
              }}
            >
              {loading ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : (
                <Activity className="size-3.5" />
              )}
              {t("doctor.rerun")}
            </Button>
          </CardTitle>
          <CardDescription>{t("doctor.desc")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading && !doctor && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground py-6 justify-center">
              <Loader2 className="size-4 animate-spin" />
              {t("doctor.running")}
            </div>
          )}
          {doctor && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Stat
                  icon={<HeartPulse className="size-4" />}
                  label={t("doctor.overall")}
                  value={doctor.status}
                />
                <Stat
                  icon={<ShieldCheck className="size-4" />}
                  label={t("doctor.runtime")}
                  value={doctor.runtime_version}
                />
                <Stat
                  icon={<Activity className="size-4" />}
                  label={t("doctor.skillsInstalled")}
                  value={String(doctor.skills_installed)}
                />
                <Stat
                  icon={<Activity className="size-4" />}
                  label={t("doctor.hostsDetected")}
                  value={String(doctor.hosts_detected.length)}
                />
              </div>
              <div className="flex flex-wrap gap-1.5">
                {doctor.hosts_detected.map((host) => (
                  <Badge
                    key={host}
                    variant="outline"
                    className="font-mono text-xs bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30"
                  >
                    {host}
                  </Badge>
                ))}
              </div>
              <div className="rounded-lg border border-border overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-48">{t("doctor.check")}</TableHead>
                      <TableHead className="w-24">{t("doctor.status")}</TableHead>
                      <TableHead>{t("doctor.detail")}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {doctor.checks.map((check) => (
                      <TableRow key={check.id}>
                        <TableCell className="font-mono text-xs">{check.id}</TableCell>
                        <TableCell>
                          <StatusBadge status={check.status} />
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground">
                          {check.detail}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              <p className="text-[11px] text-muted-foreground font-mono truncate">
                project_root: {doctor.project_root}
              </p>
            </>
          )}
          {!loading && !doctor && (
            <p className="text-sm text-muted-foreground py-4">{t("doctor.noJson")}</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-4">
          <CardTitle className="text-base flex items-center gap-2">
            <ShieldCheck className="size-4 text-emerald-500" />
            {t("doctor.selfcheckTitle")}
            {selfcheck && (
              <StatusBadge
                status={
                  selfcheck.json &&
                  typeof selfcheck.json === "object" &&
                  "status" in (selfcheck.json as Record<string, unknown>)
                    ? String((selfcheck.json as Record<string, unknown>).status)
                    : null
                }
                className="ml-1"
              />
            )}
            <Button
              variant="outline"
              size="sm"
              className="ml-auto gap-2"
              disabled={loadingSc}
              onClick={() => {
                setLoadingSc(true)
                runCommand("selfcheck", ["--path", "../suite"])
                  .then(setSelfcheck)
                  .catch(() => setSelfcheck(null))
                  .finally(() => setLoadingSc(false))
                onRan?.()
              }}
            >
              {loadingSc ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : (
                <ShieldCheck className="size-3.5" />
              )}
              {t("doctor.runSelfcheck")}
            </Button>
          </CardTitle>
          <CardDescription>{t("doctor.selfcheckDesc")}</CardDescription>
        </CardHeader>
        {selfcheck && (
          <CardContent>
            <div className="rounded-lg border border-border bg-muted/30 p-3 overflow-x-auto max-h-96 overflow-y-auto">
              <JsonViewer data={selfcheck.json ?? selfcheck.stdout} />
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  )
}

function Stat({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="rounded-lg border border-border bg-muted/30 p-3 space-y-1">
      <div className="flex items-center gap-1.5 text-muted-foreground text-xs">
        {icon}
        {label}
      </div>
      <div className="font-mono text-lg font-semibold truncate">{value}</div>
    </div>
  )
}
