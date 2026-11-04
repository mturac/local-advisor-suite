import { NextResponse } from "next/server"
import { getWorkspaceState, seedWorkspace } from "@/lib/suite"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const state = await getWorkspaceState()
    return NextResponse.json(state)
  } catch (err) {
    return NextResponse.json(
      { error: String(err instanceof Error ? err.message : err) },
      { status: 500 }
    )
  }
}

export async function POST() {
  try {
    const result = await seedWorkspace()
    const state = await getWorkspaceState()
    return NextResponse.json({ result, state })
  } catch (err) {
    return NextResponse.json(
      { error: String(err instanceof Error ? err.message : err) },
      { status: 500 }
    )
  }
}
