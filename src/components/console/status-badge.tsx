import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export function statusColor(status: string): string {
  const s = status.toUpperCase()
  if (["OK", "PASS", "DONE", "APPROVED"].includes(s)) return "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30"
  if (["WARN", "PARTIAL", "PENDING", "PROVISIONAL"].includes(s)) return "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30"
  if (["FAIL", "ERROR", "BLOCKED", "BLOCKING"].includes(s)) return "bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/30"
  return "bg-zinc-500/10 text-zinc-600 dark:text-zinc-400 border-zinc-500/25"
}

export function StatusBadge({
  status,
  className,
}: {
  status: string | null | undefined
  className?: string
}) {
  if (!status) return null
  return (
    <Badge variant="outline" className={cn("font-mono text-xs", statusColor(status), className)}>
      {status}
    </Badge>
  )
}

export function ExitBadge({ code }: { code: number }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "font-mono text-xs",
        code === 0
          ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30"
          : "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30"
      )}
    >
      exit {code}
    </Badge>
  )
}
