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

export interface RunResponse extends RunResult {
  command: string
  argv: string[]
}

export interface SkillExample {
  name: string
  content: string
}

export interface SkillInfo {
  slug: string
  name: string
  description: string
  fileCount: number
  subdirs: string[]
  examples: SkillExample[]
  content: string
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

export interface RunLogEntry {
  id: number
  command: string
  argsJson: string
  exitCode: number
  status: string | null
  durationMs: number
  stdout: string
  stderr: string
  createdAt: string
}
