import { NextResponse } from "next/server"
import { listSkills } from "@/lib/suite"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const skills = await listSkills()
    return NextResponse.json({ skills })
  } catch (err) {
    return NextResponse.json(
      { error: String(err instanceof Error ? err.message : err) },
      { status: 500 }
    )
  }
}
