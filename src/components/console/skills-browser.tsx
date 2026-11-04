"use client"

import { useEffect, useState } from "react"
import { BookOpen, FileText, Folder, Loader2, RefreshCw } from "lucide-react"
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
import type { SkillInfo } from "@/lib/console-types"
import { Markdown } from "./markdown"

export function SkillsBrowser() {
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
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          {skills.length} skills bundled in the suite — each is a self-contained
          <span className="font-mono text-xs"> SKILL.md </span>
          with references, templates and examples.
        </p>
        <Button variant="outline" size="sm" onClick={() => void load()} className="gap-2">
          <RefreshCw className="size-3.5" />
          Refresh
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
                <Badge variant="secondary" className="font-mono text-[10px]">
                  <FileText className="size-3 mr-1" />
                  {skill.fileCount} files
                </Badge>
              </div>
              <div>
                <h3 className="font-mono text-sm font-semibold">{skill.name}</h3>
                <p className="text-xs text-muted-foreground line-clamp-3 mt-1">
                  {skill.description || "—"}
                </p>
              </div>
              {skill.subdirs.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {skill.subdirs.map((dir) => (
                    <span
                      key={dir}
                      className="inline-flex items-center gap-1 text-[10px] font-mono text-muted-foreground border border-border rounded-full px-2 py-0.5"
                    >
                      <Folder className="size-2.5" />
                      {dir}
                    </span>
                  ))}
                </div>
              )}
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
            <Markdown className="pt-2">
              {active.content.replace(/^---\n[\s\S]*?\n---\n?/, "")}
            </Markdown>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}
