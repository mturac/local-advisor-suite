"use client"

import { useEffect, useState } from "react"
import { BookOpen, Check, FileText, Folder, Globe, Loader2, RefreshCw, ScrollText } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useLang } from "@/lib/i18n"
import type { SkillInfo } from "@/lib/console-types"
import { Markdown } from "./markdown"

export function SkillsBrowser() {
  const { t } = useLang()
  const [skills, setSkills] = useState<SkillInfo[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [active, setActive] = useState<SkillInfo | null>(null)

  async function load() {
    setError(null)
    try {
      const res = await fetch("/api/skills")
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`)
      setSkills(data.skills)
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err))
    }
  }

  useEffect(() => {
    void load()
  }, [])

  if (error) {
    return (
      <Card>
        <CardContent className="py-10 text-center text-sm text-rose-600 dark:text-rose-400">
          {error}
        </CardContent>
      </Card>
    )
  }

  if (!skills) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-40 rounded-xl" />
        ))}
      </div>
    )
  }

  return (
    <>
      <div className="flex items-center justify-between mb-4 gap-3 flex-wrap">
        <p className="text-sm text-muted-foreground max-w-2xl">
          {t("skills.desc", { n: skills.length })}
        </p>
        <Button variant="outline" size="sm" onClick={() => void load()} className="gap-2">
          <RefreshCw className="size-3.5" />
          {t("skills.refresh")}
        </Button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {skills.map((skill) => (
          <Card
            key={skill.slug}
            className="cursor-pointer transition-all hover:border-emerald-500/40 hover:shadow-md"
            onClick={() => setActive(skill)}
          >
            <CardContent className="p-5 space-y-3">
              <div className="flex items-start justify-between gap-2">
                <div className="size-9 rounded-lg bg-emerald-500/15 flex items-center justify-center shrink-0">
                  <BookOpen className="size-4.5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div className="flex flex-col items-end gap-1">
                  <Badge variant="secondary" className="font-mono text-[10px]">
                    <FileText className="size-3 mr-1" />
                    {skill.fileCount} {t("skills.files")}
                  </Badge>
                </div>
              </div>
              <div>
                <h3 className="font-mono text-sm font-semibold">{skill.name}</h3>
                <p className="text-xs text-muted-foreground line-clamp-3 mt-1">
                  {skill.description || "—"}
                </p>
              </div>
              {/* readiness: skills are instruction packs for the AI agent —
                  they are ready wherever the agent is; nothing is "offline" */}
              <div
                className="flex items-center gap-1.5 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-1"
                title={t("skills.readyHint")}
              >
                <span className="relative flex size-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                  <span className="relative inline-flex size-2 rounded-full bg-emerald-500" />
                </span>
                <span className="text-[11px] font-medium text-emerald-700 dark:text-emerald-300">
                  {t("skills.ready")}
                </span>
                <span className="text-[11px] text-emerald-700/80 dark:text-emerald-300/80">
                  · {skill.runtime === "llm-web" ? t("skills.webHint") : t("skills.readyHint")}
                </span>
                {skill.runtime === "llm-web" && (
                  <Globe className="size-3 ml-auto text-emerald-600 dark:text-emerald-400 shrink-0" />
                )}
              </div>
              <div className="flex flex-wrap items-center gap-1">
                {skill.subdirs.map((dir) => (
                  <span
                    key={dir}
                    className="inline-flex items-center gap-1 text-[10px] font-mono text-muted-foreground border border-border rounded-full px-2 py-0.5"
                  >
                    <Folder className="size-2.5" />
                    {dir}
                  </span>
                ))}
                {skill.examples?.length > 0 && (
                  <span className="inline-flex items-center gap-1 text-[10px] font-mono text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 bg-emerald-500/10 rounded-full px-2 py-0.5">
                    <ScrollText className="size-2.5" />
                    {skill.examples.length}{" "}
                    {skill.examples.length === 1 ? t("skills.example") : t("skills.examples")}
                  </span>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={!!active} onOpenChange={(open) => !open && setActive(null)}>
        <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="font-mono">{active?.name}</DialogTitle>
            <DialogDescription>
              suite/skills/{active?.slug}/SKILL.md
            </DialogDescription>
          </DialogHeader>
          {active && (
            <Tabs defaultValue="overview" className="mt-2">
              <TabsList className="h-9 w-full justify-start overflow-x-auto">
                <TabsTrigger value="overview" className="text-xs gap-1.5">
                  <BookOpen className="size-3.5" />
                  SKILL.md
                </TabsTrigger>
                {active.examples.map((ex) => (
                  <TabsTrigger
                    key={ex.name}
                    value={`example:${ex.name}`}
                    className="text-xs gap-1.5"
                  >
                    <ScrollText className="size-3.5" />
                    {ex.name}
                  </TabsTrigger>
                ))}
              </TabsList>
              <TabsContent value="overview" className="mt-3">
                <Markdown>
                  {active.content.replace(/^---\n[\s\S]*?\n---\n?/, "")}
                </Markdown>
              </TabsContent>
              {active.examples.map((ex) => (
                <TabsContent
                  key={ex.name}
                  value={`example:${ex.name}`}
                  className="mt-3"
                >
                  <Markdown>{ex.content}</Markdown>
                </TabsContent>
              ))}
            </Tabs>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}
