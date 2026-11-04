import { NextRequest, NextResponse } from "next/server"
import { getCatalog, runWorkbench } from "@/lib/suite"
import { db } from "@/lib/db"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

export async function POST(req: NextRequest) {
  let body: { command?: unknown; argv?: unknown }
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 })
  }

  const command = typeof body.command === "string" ? body.command : ""
  const argv = Array.isArray(body.argv)
    ? body.argv.filter((a): a is string => typeof a === "string").slice(0, 64)
    : []

  if (!command) {
    return NextResponse.json({ error: "Missing command" }, { status: 400 })
  }

  try {
    const catalog = await getCatalog()
    const spec = catalog.commands.find((c) => c.name === command)
    if (!spec) {
      return NextResponse.json(
        { error: `Unknown command: ${command}` },
        { status: 400 }
      )
    }

    const result = await runWorkbench(command, argv)
    const status =
      result.json && typeof result.json === "object" && "status" in (result.json as Record<string, unknown>)
        ? String((result.json as Record<string, unknown>).status)
        : null

    try {
      await db.runLog.create({
        data: {
          command,
          argsJson: JSON.stringify(argv),
          exitCode: result.exitCode,
          status,
          durationMs: result.durationMs,
          stdout: result.stdout.slice(0, 20_000),
          stderr: result.stderr.slice(0, 5_000),
        },
      })
    } catch {
      // history logging is best-effort
    }

    return NextResponse.json({ command, argv, ...result })
  } catch (err) {
    return NextResponse.json(
      { error: String(err instanceof Error ? err.message : err) },
      { status: 500 }
    )
  }
}
