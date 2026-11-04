import { NextResponse } from "next/server"
import { getCatalog } from "@/lib/suite"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const catalog = await getCatalog()
    return NextResponse.json(catalog)
  } catch (err) {
    return NextResponse.json(
      { error: String(err instanceof Error ? err.message : err) },
      { status: 500 }
    )
  }
}
