"use client"

import { useState } from "react"
import { ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

function primitiveClass(v: unknown) {
  if (typeof v === "string") return "text-emerald-500 dark:text-emerald-400 break-all"
  if (typeof v === "number") return "text-amber-600 dark:text-amber-400"
  if (typeof v === "boolean") return "text-rose-600 dark:text-rose-400"
  return "text-zinc-700 dark:text-zinc-300"
}

function formatPrimitive(v: unknown) {
  if (typeof v === "string") return `"${v}"`
  return String(v)
}

function JsonNode({
  label,
  value,
  depth,
  isLast,
}: {
  label?: string
  value: unknown
  depth: number
  isLast?: boolean
}) {
  const [open, setOpen] = useState(depth < 2)

  const isObject = value !== null && typeof value === "object"

  if (!isObject) {
    return (
      <div className="pl-4 leading-6">
        {label !== undefined && (
          <span className="text-zinc-500 dark:text-zinc-400">{label}: </span>
        )}
        <span className={primitiveClass(value)}>{formatPrimitive(value)}</span>
        {!isLast && <span className="text-zinc-400">,</span>}
      </div>
    )
  }

  const entries: [string, unknown][] = Array.isArray(value)
    ? value.map((v, i) => [String(i), v] as [string, unknown])
    : Object.entries(value as Record<string, unknown>)

  const bracketOpen = Array.isArray(value) ? "[" : "{"
  const bracketClose = Array.isArray(value) ? "]" : "}"

  if (entries.length === 0) {
    return (
      <div className="pl-4 leading-6">
        {label !== undefined && (
          <span className="text-zinc-500 dark:text-zinc-400">{label}: </span>
        )}
        <span className="text-zinc-400">
          {bracketOpen}
          {bracketClose}
        </span>
      </div>
    )
  }

  return (
    <div className="pl-4">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1 leading-6 text-left hover:bg-zinc-100 dark:hover:bg-zinc-800/60 rounded px-0.5 -ml-0.5"
      >
        <ChevronRight
          className={cn(
            "size-3.5 shrink-0 text-zinc-400 transition-transform",
            open && "rotate-90"
          )}
        />
        {label !== undefined && (
          <span className="text-zinc-500 dark:text-zinc-400">{label}: </span>
        )}
        <span className="text-zinc-400">{bracketOpen}</span>
        {!open && (
          <span className="text-zinc-400">
            {entries.length} {entries.length === 1 ? "item" : "items"}
            {bracketClose}
          </span>
        )}
      </button>
      {open && (
        <div className="border-l border-zinc-200 dark:border-zinc-800">
          {entries.map(([k, v], i) => (
            <JsonNode
              key={k}
              label={Array.isArray(value) ? undefined : k}
              value={v}
              depth={depth + 1}
              isLast={i === entries.length - 1}
            />
          ))}
          <div className="pl-4 leading-6 text-zinc-400">{bracketClose}</div>
        </div>
      )}
    </div>
  )
}

export function JsonViewer({
  data,
  className,
}: {
  data: unknown
  className?: string
}) {
  return (
    <div className={cn("font-mono text-xs", className)}>
      <JsonNode value={data} depth={0} />
    </div>
  )
}
