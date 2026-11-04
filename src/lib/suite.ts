import { spawn } from "child_process"
import path from "path"
import fs from "fs/promises"

export interface ArgSpec {
  flags: string[]
  dest: string
  kind: "single" | "switch" | "multi" | "positional"
  required: boolean
  default: unknown
  help: string
  type: string | null
  choices: string[] | null
  metavar: string | null
}

export interface CommandSpec {
  name: string
  help: string
  usage: string
  category: string
  args: ArgSpec[]
}

export interface Catalog {
  version: string
  commands: CommandSpec[]
}

export interface RunResult {
  exitCode: number
  stdout: string
  stderr: string
  durationMs: number
  json: unknown
  truncated: boolean
  timedOut: boolean
}

export interface SkillInfo {
  slug: string
  name: string
  description: string
  fileCount: number
  subdirs: string[]
  examples: { name: string; content: string }[]
  content: string
}

const ROOT = process.cwd()
export const SUITE_DIR = process.env.SUITE_DIR || path.join(ROOT, "suite")
export const WORKBENCH = path.join(SUITE_DIR, "workbench.py")
export const WORKSPACE = path.join(ROOT, ".workspace")
export const STATE_DIR = path.join(WORKSPACE, ".local-workbench")

const MAX_OUTPUT = 200_000

function python(): string {
  return process.env.PYTHON || "python3"
}

export function runProcess(
  args: string[],
  opts: { cwd?: string; timeoutMs?: number } = {}
): Promise<RunResult> {
  const { cwd = ROOT, timeoutMs = 30_000 } = opts
  return new Promise((resolve) => {
    const started = Date.now()
    const child = spawn(python(), args, {
      cwd,
      env: { ...process.env, PYTHONIOENCODING: "utf-8", PYTHONUNBUFFERED: "1" },
    })
    let stdout = ""
    let stderr = ""
    let truncated = false
    let timedOut = false

    const timer = setTimeout(() => {
      timedOut = true
      child.kill("SIGKILL")
    }, timeoutMs)

    child.stdout.on("data", (chunk: Buffer) => {
      if (stdout.length >= MAX_OUTPUT) {
        truncated = true
        return
      }
      stdout += chunk.toString("utf-8")
    })
    child.stderr.on("data", (chunk: Buffer) => {
      if (stderr.length >= 20_000) {
        truncated = true
        return
      }
      stderr += chunk.toString("utf-8")
    })
    child.on("error", (err) => {
      clearTimeout(timer)
      resolve({
        exitCode: -1,
        stdout,
        stderr: stderr + String(err),
        durationMs: Date.now() - started,
        json: null,
        truncated,
        timedOut,
      })
    })
    child.on("close", (code) => {
      clearTimeout(timer)
      if (stdout.length > MAX_OUTPUT) {
        stdout = stdout.slice(0, MAX_OUTPUT)
        truncated = true
      }
      let json: unknown = null
      const trimmed = stdout.trim()
      if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
        try {
          json = JSON.parse(trimmed)
        } catch {
          json = null
        }
      }
      resolve({
        exitCode: code ?? -1,
        stdout,
        stderr,
        durationMs: Date.now() - started,
        json,
        truncated,
        timedOut,
      })
    })
  })
}

let catalogCache: Promise<Catalog> | null = null

export function getCatalog(): Promise<Catalog> {
  if (!catalogCache) {
    catalogCache = runProcess(
      [path.join(ROOT, "scripts", "introspect_catalog.py"), SUITE_DIR],
      { timeoutMs: 30_000 }
    ).then((res) => {
      if (res.exitCode !== 0 || !res.json) {
        catalogCache = null
        throw new Error(`catalog introspection failed: ${res.stderr.slice(0, 400)}`)
      }
      return res.json as Catalog
    })
  }
  return catalogCache
}

export function runWorkbench(command: string, argv: string[]): Promise<RunResult> {
  const clean: string[] = []
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--state-dir") {
      i++ // skip its value too
      continue
    }
    clean.push(argv[i])
  }
  return runProcess(
    [WORKBENCH, "--state-dir", STATE_DIR, command, ...clean],
    { cwd: WORKSPACE, timeoutMs: 45_000 }
  )
}

export async function listSkills(): Promise<SkillInfo[]> {
  const skillsRoot = path.join(SUITE_DIR, "skills")
  const entries = await fs.readdir(skillsRoot, { withFileTypes: true })
  const skills: SkillInfo[] = []
  for (const entry of entries) {
    if (!entry.isDirectory()) continue
    const skillDir = path.join(skillsRoot, entry.name)
    const mdPath = path.join(skillDir, "SKILL.md")
    try {
      const content = await fs.readFile(mdPath, "utf-8")
      const fmText = content.match(/^---\n([\s\S]*?)\n---/)?.[1] ?? ""
      const name = fmText.match(/^name:\s*(.+)$/m)?.[1]?.trim() || entry.name
      const description =
        fmText
          .match(/^description:\s*([\s\S]*?)(?=\n\w+:|\n*$)/m)?.[1]
          ?.replace(/\s+/g, " ")
          .trim() || ""
      const subdirs: string[] = []
      const examples: { name: string; content: string }[] = []
      let fileCount = 0
      const walk = async (dir: string, depth: number) => {
        const items = await fs.readdir(dir, { withFileTypes: true })
        for (const item of items) {
          const full = path.join(dir, item.name)
          if (item.isDirectory()) {
            if (depth === 0) subdirs.push(item.name)
            if (depth === 0 && item.name === "examples") {
              try {
                const exFiles = await fs.readdir(full, { withFileTypes: true })
                for (const ex of exFiles
                  .filter((f) => f.isFile() && f.name.endsWith(".md"))
                  .sort((a, b) => a.name.localeCompare(b.name))) {
                  examples.push({
                    name: ex.name.replace(/\.md$/, ""),
                    content: await fs.readFile(path.join(full, ex.name), "utf-8"),
                  })
                }
              } catch {
                // unreadable examples dir — skip
              }
            }
            await walk(full, depth + 1)
          } else {
            fileCount++
          }
        }
      }
      await walk(skillDir, 0)
      skills.push({ slug: entry.name, name, description, fileCount, subdirs, examples, content })
    } catch {
      // SKILL.md missing — skip
    }
  }
  return skills.sort((a, b) => a.slug.localeCompare(b.slug))
}

export interface LedgerFile {
  name: string
  size: number
  json: unknown
  parseError: boolean
}

export interface WorkspaceState {
  stateDir: string
  ledgers: LedgerFile[]
  outputs: { name: string; path: string; size: number }[]
  hosts: string[]
}

export async function getWorkspaceState(): Promise<WorkspaceState> {
  const ledgers: LedgerFile[] = []
  const outputs: WorkspaceState["outputs"] = []
  let hosts: string[] = []

  try {
    const files = await fs.readdir(STATE_DIR, { withFileTypes: true })
    for (const f of files) {
      if (!f.isFile()) continue
      const full = path.join(STATE_DIR, f.name)
      const stat = await fs.stat(full)
      const raw = await fs.readFile(full, "utf-8")
      let json: unknown = null
      let parseError = false
      if (f.name.endsWith(".json")) {
        try {
          json = JSON.parse(raw)
        } catch {
          parseError = true
        }
      }
      ledgers.push({ name: f.name, size: stat.size, json, parseError })
    }
  } catch {
    // state dir missing
  }

  const collectOutputs = async (rel: string) => {
    try {
      const dir = path.join(WORKSPACE, rel)
      const items = await fs.readdir(dir, { withFileTypes: true })
      for (const item of items) {
        if (!item.isFile()) continue
        const full = path.join(dir, item.name)
        const stat = await fs.stat(full)
        outputs.push({ name: `${rel}/${item.name}`, path: full, size: stat.size })
      }
    } catch {
      // optional dir
    }
  }
  await collectOutputs("artifacts")
  await collectOutputs("docs/adr")

  try {
    const entries = await fs.readdir(WORKSPACE, { withFileTypes: true })
    hosts = entries
      .filter((e) => e.isDirectory() && e.name.startsWith(".") && e.name !== ".local-workbench")
      .map((e) => e.name.replace(/^\./, ""))
    if (entries.some((e) => e.isFile() && e.name === "AGENTS.md")) hosts.push("agents-md")
  } catch {
    // workspace missing
  }

  return { stateDir: STATE_DIR, ledgers, outputs, hosts }
}

export function seedWorkspace(): Promise<RunResult> {
  return runProcess([path.join(ROOT, "scripts", "seed_workspace.py"), ROOT], {
    cwd: ROOT,
    timeoutMs: 300_000,
  })
}
