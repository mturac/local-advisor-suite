"use client"

import { useLang, type Lang } from "@/lib/i18n"
import { cn } from "@/lib/utils"

const OPTIONS: { value: Lang; label: string }[] = [
  { value: "tr", label: "TR" },
  { value: "en", label: "EN" },
]

export function LangToggle() {
  const { lang, setLang } = useLang()

  return (
    <div
      role="group"
      aria-label="Dil / Language"
      className="inline-flex items-center rounded-md border border-border bg-muted/40 p-0.5 h-9"
    >
      {OPTIONS.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => setLang(opt.value)}
          aria-pressed={lang === opt.value}
          className={cn(
            "h-8 px-2.5 rounded-sm text-xs font-semibold tracking-wide transition-colors",
            lang === opt.value
              ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}
