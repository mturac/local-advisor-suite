import { NextRequest, NextResponse } from "next/server"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

/**
 * Server-side proxy for the Firecrawl web-research API.
 *
 * The API key never reaches the browser: the client asks this route for an
 * action (search / scrape / map / extract / crawl) and gets a normalized
 * JSON result back. Every call here is a real, credit-consuming Firecrawl
 * call — this is the same engine the Deep Research story uses to search and
 * read the live web.
 */

const BASE = "https://api.firecrawl.dev/v2"
const MAX_MARKDOWN_DISPLAY = 6_000
const EXCERPT_AROUND_QUOTE = 180
const DEFAULT_EXCERPT = 500

type Json = Record<string, unknown>

function apiKey(): string | null {
  const key = process.env.FIRECRAWL_API_KEY
  return key && key.trim() ? key.trim() : null
}

async function fireFetch(
  path: string,
  init: RequestInit,
  timeoutMs: number
): Promise<{ ok: boolean; status: number; body: Json }> {
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), timeoutMs)
  try {
    const res = await fetch(`${BASE}${path}`, {
      ...init,
      signal: ctrl.signal,
      headers: {
        Authorization: `Bearer ${apiKey()}`,
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
      },
    })
    let body: Json
    try {
      body = (await res.json()) as Json
    } catch {
      body = { error: `Firecrawl returned non-JSON (HTTP ${res.status})` }
    }
    return { ok: res.ok, status: res.status, body }
  } finally {
    clearTimeout(timer)
  }
}

function errText(body: Json): string {
  const e = body.error
  if (typeof e === "string") return e
  if (e && typeof e === "object") {
    const msg = (e as Json).message
    if (typeof msg === "string") return msg
  }
  return JSON.stringify(body).slice(0, 300)
}

/** Collapse all whitespace runs to single spaces (workbench quote checks use this too). */
function norm(s: string): string {
  return s.replace(/\s+/g, " ").trim()
}

function asString(v: unknown, fallback = ""): string {
  return typeof v === "string" ? v : fallback
}

function isHttpsUrl(raw: unknown): raw is string {
  return typeof raw === "string" && /^https:\/\/[^\s]+$/i.test(raw.trim())
}

interface ScrapeResult {
  action: "scrape"
  url: string
  title: string
  markdown: string
  excerpt: string
  quote: string | null
  quoteFound: boolean | null
  markdownLength: number
  fetchedAt: string
}

function buildScrapeResult(
  url: string,
  title: string,
  markdown: string,
  quote: string | null
): ScrapeResult {
  const flat = norm(markdown)
  let excerpt = flat.slice(0, DEFAULT_EXCERPT)
  let quoteFound: boolean | null = null

  if (quote) {
    const q = norm(quote)
    const idx = flat.toLowerCase().indexOf(q.toLowerCase())
    quoteFound = idx >= 0
    if (quoteFound) {
      const start = Math.max(0, idx - EXCERPT_AROUND_QUOTE)
      const end = Math.min(flat.length, idx + q.length + EXCERPT_AROUND_QUOTE)
      excerpt = (start > 0 ? "… " : "") + flat.slice(start, end) + (end < flat.length ? " …" : "")
    }
  }

  return {
    action: "scrape",
    url,
    title: title || url,
    markdown: markdown.slice(0, MAX_MARKDOWN_DISPLAY),
    excerpt,
    quote: quote ?? null,
    quoteFound,
    markdownLength: markdown.length,
    fetchedAt: new Date().toISOString(),
  }
}

async function pollJob(
  kind: "extract" | "crawl",
  id: string,
  maxWaitMs: number
): Promise<Json | null> {
  const deadline = Date.now() + maxWaitMs
  let last: Json | null = null
  while (Date.now() < deadline) {
    const res = await fireFetch(`/${kind}/${id}`, { method: "GET" }, 15_000)
    last = res.body
    const status = asString(res.body.status)
    if (status === "completed" || status === "failed" || res.body.data) return res.body
    await new Promise((r) => setTimeout(r, 2_500))
  }
  return last
}

export async function POST(req: NextRequest) {
  const key = apiKey()
  if (!key) {
    return NextResponse.json(
      { error: "FIRECRAWL_NOT_CONFIGURED", detail: "FIRECRAWL_API_KEY is not set on the server." },
      { status: 500 }
    )
  }

  let body: Json
  try {
    body = (await req.json()) as Json
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 })
  }

  const action = asString(body.action)

  try {
    if (action === "search") {
      const query = asString(body.query).trim()
      const limit = Math.min(Math.max(Number(body.limit) || 5, 1), 10)
      if (!query) {
        return NextResponse.json({ error: "Missing search query" }, { status: 400 })
      }
      const res = await fireFetch(
        "/search",
        { method: "POST", body: JSON.stringify({ query, limit }) },
        25_000
      )
      if (!res.ok) {
        return NextResponse.json({ error: errText(res.body) }, { status: 502 })
      }
      const web =
        ((res.body.data as Json | undefined)?.web as Array<Record<string, unknown>> | undefined) ??
        []
      return NextResponse.json({
        action: "search",
        query,
        results: web.map((r) => ({
          title: asString(r.title),
          url: asString(r.url),
          description: asString(r.description),
        })),
        creditsUsed: res.body.creditsUsed ?? null,
      })
    }

    if (action === "scrape") {
      if (!isHttpsUrl(body.url)) {
        return NextResponse.json({ error: "url must be a valid https:// URL" }, { status: 400 })
      }
      const url = body.url.trim()
      const quote = typeof body.quote === "string" && body.quote.trim() ? body.quote.trim() : null
      const res = await fireFetch(
        "/scrape",
        { method: "POST", body: JSON.stringify({ url, formats: ["markdown"] }) },
        45_000
      )
      if (!res.ok) {
        return NextResponse.json({ error: errText(res.body) }, { status: 502 })
      }
      const data = (res.body.data ?? {}) as Json
      const markdown = asString(data.markdown)
      const title = asString((data.metadata as Json | undefined)?.title)
      if (!markdown) {
        return NextResponse.json(
          { error: "Firecrawl returned no markdown for this page" },
          { status: 502 }
        )
      }
      const result = buildScrapeResult(url, title, markdown, quote)
      if (quote && !result.quoteFound) {
        return NextResponse.json(
          {
            error: "QUOTE_NOT_ON_PAGE",
            detail: `The marked sentence was not found on ${url}. The page may have changed — the story refuses to quote a page that does not contain the sentence.`,
            ...result,
          },
          { status: 422 }
        )
      }
      return NextResponse.json(result)
    }

    if (action === "map") {
      if (!isHttpsUrl(body.url)) {
        return NextResponse.json({ error: "url must be a valid https:// URL" }, { status: 400 })
      }
      const limit = Math.min(Math.max(Number(body.limit) || 20, 1), 50)
      const res = await fireFetch(
        "/map",
        { method: "POST", body: JSON.stringify({ url: body.url.trim(), limit }) },
        30_000
      )
      if (!res.ok) {
        return NextResponse.json({ error: errText(res.body) }, { status: 502 })
      }
      const links = ((res.body.data ?? {}) as Json).links
      return NextResponse.json({
        action: "map",
        url: body.url.trim(),
        links: Array.isArray(links) ? links.slice(0, limit) : [],
      })
    }

    if (action === "extract") {
      if (!isHttpsUrl(body.url)) {
        return NextResponse.json({ error: "url must be a valid https:// URL" }, { status: 400 })
      }
      const prompt = asString(body.prompt).trim()
      if (!prompt) {
        return NextResponse.json({ error: "Missing extraction prompt" }, { status: 400 })
      }
      const start = await fireFetch(
        "/extract",
        {
          method: "POST",
          body: JSON.stringify({ urls: [body.url.trim()], prompt }),
        },
        25_000
      )
      if (!start.ok) {
        return NextResponse.json({ error: errText(start.body) }, { status: 502 })
      }
      const id = asString(start.body.id)
      if (!id) {
        return NextResponse.json({ error: "Firecrawl did not return a job id" }, { status: 502 })
      }
      const done = await pollJob("extract", id, 40_000)
      const status = asString(done?.status)
      if (!done || status === "failed") {
        return NextResponse.json(
          { error: "Extraction job failed or timed out", last: done },
          { status: 502 }
        )
      }
      const extraction = ((done.data ?? {}) as Json).extraction ?? done.data ?? null
      return NextResponse.json({
        action: "extract",
        url: body.url.trim(),
        prompt,
        status,
        extraction,
      })
    }

    if (action === "crawl") {
      if (!isHttpsUrl(body.url)) {
        return NextResponse.json({ error: "url must be a valid https:// URL" }, { status: 400 })
      }
      const limit = Math.min(Math.max(Number(body.limit) || 5, 1), 10)
      const start = await fireFetch(
        "/crawl",
        {
          method: "POST",
          body: JSON.stringify({
            url: body.url.trim(),
            limit,
            scrapeOptions: { formats: ["markdown"] },
          }),
        },
        25_000
      )
      if (!start.ok) {
        return NextResponse.json({ error: errText(start.body) }, { status: 502 })
      }
      const id = asString(start.body.id)
      if (!id) {
        return NextResponse.json({ error: "Firecrawl did not return a job id" }, { status: 502 })
      }
      const done = await pollJob("crawl", id, 55_000)
      const status = asString(done?.status)
      const data = done?.data
      const pages = Array.isArray(data)
        ? (data as Array<Record<string, unknown>>).map((p) => ({
            url: asString(p.url ?? (p.metadata as Json | undefined)?.url),
            title: asString((p.metadata as Json | undefined)?.title),
          }))
        : []
      return NextResponse.json({
        action: "crawl",
        url: body.url.trim(),
        status: status || "unknown",
        pages,
        note:
          status === "completed"
            ? null
            : "Crawl was still running when the wait budget ended — showing partial results.",
      })
    }

    return NextResponse.json(
      {
        error: `Unknown action: ${action || "(none)"}. Use search | scrape | map | extract | crawl.`,
      },
      { status: 400 }
    )
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err)
    const aborted = msg.includes("abort")
    return NextResponse.json(
      {
        error: aborted ? "Firecrawl request timed out" : `Firecrawl request failed: ${msg}`,
      },
      { status: 504 }
    )
  }
}
