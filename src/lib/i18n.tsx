"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"

export type Lang = "tr" | "en"

const STORAGE_KEY = "las-lang"

/**
 * UI strings. `tr` is the default language; every key must have both values.
 * Interpolation: "{name}" placeholders are replaced by t(key, { name }).
 */
const STRINGS: Record<string, { tr: string; en: string }> = {
  // ── header ──────────────────────────────────────────────────────────────
  "header.subtitle": { tr: "Konsol", en: "Console" },
  "header.meta": {
    tr: "{commands} komut · yerelde çalışır · tedarikçi kilidi yok",
    en: "{commands} commands · runs locally · zero vendor lock-in",
  },

  // ── hero ────────────────────────────────────────────────────────────────
  "hero.badge": {
    tr: "v3.1.0 · 39 komut · 13 beceri · hepsi AI agent'ınla hazır",
    en: "v3.1.0 · 39 commands · 13 skills · all ready via your AI agent",
  },
  "hero.titleA": { tr: "Tarayıcıda dene.", en: "Try it right here." },
  "hero.titleB": { tr: "Kurulum yok, hesap yok.", en: "No setup. No account." },
  "hero.sub": {
    tr: "Bu sayfa Local Advisor Suite'in 39 komutunu gerçekten çalıştırır — güvenli bir demo alanında. Beceriler ise AI agent'ının beyniyle çalışır: agent kuruluysa hepsi hazır. Bir hikâye seç, Çalıştır'a bas, gerçekte ne olduğunu izle.",
    en: "This page actually runs the suite's 39 commands — inside a safe demo workspace. The skills run through your AI agent's reasoning: if the agent is installed, every skill is ready. Pick a story, press Run, and watch what really happens.",
  },
  "hero.cta": { tr: "Hemen bir hikâye dene", en: "Try a story now" },
  "hero.step1.title": { tr: "1 · Soldan bir hikâye seç", en: "1 · Pick a story on the left" },
  "hero.step1.desc": {
    tr: "Araştırma, teslimat, hata ayıklama ya da karar — hepsi başlangıç seviyesinde anlatıldı.",
    en: "Research, shipping, debugging or a decision — all told in beginner language.",
  },
  "hero.step2.title": { tr: "2 · Çalıştır'a bas", en: "2 · Press Run" },
  "hero.step2.desc": {
    tr: "Adım adım ya da \"Tümünü çalıştır\" ile. Her buton gerçek komutu çalıştırır, sahte animasyon değil.",
    en: "Step by step, or all at once. Every button fires the real command — not a fake animation.",
  },
  "hero.step3.title": { tr: "3 · Sonucu gör", en: "3 · See the result" },
  "hero.step3.desc": {
    tr: "Her adımın altında \"şu görünecek\" kutusu ve gerçek çıktı var. Üretilen dosyalar Dosyalar sekmesinde.",
    en: "Each step shows a \"you'll see\" hint plus the real output. Generated files land in the Files tab.",
  },

  // ── tabs ────────────────────────────────────────────────────────────────
  "tab.stories": { tr: "Hikâyeler", en: "Stories" },
  "tab.web": { tr: "Web Araştırma", en: "Web Research" },
  "tab.runner": { tr: "Komut Dene", en: "Try Commands" },
  "tab.skills": { tr: "Beceriler", en: "Skills" },
  "tab.doctor": { tr: "Sağlık", en: "Health" },
  "tab.workspace": { tr: "Dosyalar", en: "Files" },
  "tab.history": { tr: "Geçmiş", en: "History" },

  // ── walkthroughs ────────────────────────────────────────────────────────
  "wt.title": { tr: "Hikâyeler", en: "Stories" },
  "wt.pickHint": {
    tr: "Baştan sona gerçek senaryolar. Her biri gerçek komutlar çalıştırır ve sonunda elinde bir dosya olur.",
    en: "Complete stories, start to finish. Each runs real commands and ends with a real artifact.",
  },
  "wt.stepsShort": { tr: "adım", en: "steps" },
  "wt.flowMeta": { tr: "{n} adım · ~{m} dk", en: "{n} steps · ~{m} min" },
  "wt.endsWith": { tr: "Sonunda: {outcome}", en: "Ends with: {outcome}" },
  "wt.runAll": { tr: "Tümünü çalıştır", en: "Run all steps" },
  "wt.running": { tr: "Çalışıyor…", en: "Running…" },
  "wt.clear": { tr: "Temizle", en: "Clear" },
  "wt.resetFirst": { tr: "Önce çalışma alanını sıfırla", en: "Reset workspace first" },
  "wt.reseeding": { tr: "Sıfırlanıyor…", en: "Reseeding…" },
  "wt.realCli": {
    tr: "her tıklama gerçek komutu çalıştırır",
    en: "every click runs the real CLI",
  },
  "wt.youWillSee": { tr: "Şu görünecek", en: "You'll see" },
  "wt.whatHappens": { tr: "Ne oluyor?", en: "What happens?" },
  "wt.commandLabel": { tr: "Komut", en: "Command" },
  "wt.runStep": { tr: "Bu adımı çalıştır", en: "Run this step" },
  "wt.run": { tr: "Çalıştır", en: "Run" },
  "wt.deliverable": { tr: "çıktı dosyası", en: "deliverable" },
  "wt.rawOutput": { tr: "ham çıktı", en: "raw output" },
  "wt.stepOk": { tr: "Adım başarılı — beklenen sonuç geldi", en: "Step succeeded — as expected" },
  "wt.stepMismatch": {
    tr: "Sonuç beklendiği gibi değil",
    en: "Result differs from what was expected",
  },
  "wt.expected": { tr: "beklenen: {status}", en: "expected: {status}" },
  "wt.complete.title": { tr: "Hikâye tamamlandı 🎉", en: "Story complete 🎉" },
  "wt.complete.body": {
    tr: "{n} adımın hepsi gerçek komut olarak çalıştı ve hikâye şununla bitti: {outcome}. Üretilen dosyaları Dosyalar sekmesinde görebilirsin.",
    en: "All {n} steps ran against the real CLI and the story ended with: {outcome}. Check the Files tab for what it produced.",
  },
  "wt.stoppedAt": {
    tr: "{n}. adım (\"{title}\") beklenen sonucu vermedi — çalışma orada durdu.",
    en: "Step {n} (\"{title}\") did not produce the expected result — the run stopped there.",
  },
  "wt.note": {
    tr: "Adımlar sırayla çalışır; her biri bir öncekinin deftere yazdığı state üzerine inşa eder. Her adımın altındaki komut satırı, birebir çalıştırılan şeyin kendisidir — istersen Komut Dene sekmesinde elle de tekrar oynatabilirsin.",
    en: "Steps run in order; each one builds on the ledger state the previous step wrote. The command line under every step is exactly what runs — you can replay any of it by hand in the Try Commands tab.",
  },
  "wt.copied": { tr: "Kopyalandı!", en: "Copied!" },
  "wt.copy": { tr: "Kopyala", en: "Copy" },

  // ── runner ──────────────────────────────────────────────────────────────
  "runner.commands": { tr: "Komutlar", en: "Commands" },
  "runner.search": { tr: "Komut ara…", en: "Search commands…" },
  "runner.noMatch": { tr: "Şuna uyan komut yok: {q}", en: "No commands match \"{q}\"." },
  "runner.examplesTitle": { tr: "Tek tıkla örnekler", en: "One-click examples" },
  "runner.examplesDesc": {
    tr: "Kum havuzu modu: 39 komutun tamamı, hazır çalışan argümanlarla. Yeni misin? Önce Hikâyeler sekmesinde bir hikâyeyi baştan sona çalıştır.",
    en: "Sandbox mode: all 39 commands with pre-filled working arguments. New here? Run a full story in the Stories tab first.",
  },
  "runner.allCommands": { tr: "39 komutun tamamı", en: "all 39 commands" },
  "runner.amberNote": {
    tr: "Turuncu senaryolar yazmadan önce kendi defterini siler — demo veriyi her zaman Dosyalar sekmesindeki \"Çalışma alanını sıfırla\" ile geri getirebilirsin.",
    en: "Amber scenarios wipe their own ledger before writing — restore the demo data anytime with Reset workspace in the Files tab.",
  },
  "runner.noArgs": {
    tr: "Bu komut argüman almaz. Sadece çalıştırman yeterli.",
    en: "This command takes no arguments. Just run it.",
  },
  "runner.extraArgs": { tr: "Ek argümanlar (ileri düzey)", en: "Extra args (advanced)" },
  "runner.resetArgs": { tr: "Argümanları sıfırla", en: "Reset args" },
  "runner.output": { tr: "Çıktı", en: "Output" },
  "runner.noStdout": { tr: "(stdout boş)", en: "(no stdout)" },
  "runner.timedOut": {
    tr: "Komut zaman aşımına uğradı ve sonlandırıldı.",
    en: "Command timed out and was killed.",
  },
  "runner.pickCommand": {
    tr: "Soldan bir komut seç ya da yukarıdan bir örnek senaryo ateşle.",
    en: "Pick a command on the left, or fire an example scenario above.",
  },
  "runner.required": { tr: "zorunlu", en: "required" },
  "runner.addValue": { tr: "Değer ekle", en: "Add value" },

  // ── skills ──────────────────────────────────────────────────────────────
  "skills.desc": {
    tr: "Pakette {n} beceri var — her biri AI agent'ının okuyup uyguladığı bir talimat paketi: references + templates + examples içeren bir SKILL.md. Agent'ın (Claude Code, Cursor vb.) kurulu olduğu her yerde çalışmaya hazırdır — indirilecek, başlatılacak ayrı bir servis yoktur.",
    en: "{n} skills bundled in the suite — each a self-contained SKILL.md with references, templates and examples. They are instruction packs your AI agent reads and follows, so they are ready wherever your agent (Claude Code, Cursor, …) is installed — nothing to install or start.",
  },
  "skills.refresh": { tr: "Yenile", en: "Refresh" },
  "skills.files": { tr: "dosya", en: "files" },
  "skills.example": { tr: "örnek", en: "example" },
  "skills.examples": { tr: "örnek", en: "examples" },
  "skills.ready": { tr: "Hazır", en: "Ready" },
  "skills.readyHint": {
    tr: "AI agent'ınla çalışır — ek kurulum yok",
    en: "runs via your AI agent — no extra setup",
  },
  "skills.webHint": {
    tr: "agent'ın + canlı web (Firecrawl)",
    en: "your agent + live web (Firecrawl)",
  },

  // ── firecrawl ──────────────────────────────────────────────────────────
  "fc.title": { tr: "Web'i oku: Firecrawl motoru", en: "Read the web: the Firecrawl engine" },
  "fc.intro": {
    tr: "Firecrawl, AI agent'ının web'i okumasını sağlayan motordur: arar, sayfayı indirip temiz metne çevirir, site haritası çıkarır, veri toplar. Deep Research hikâyendeki tüm aramalar ve sayfa okumaları bu motorla yapılır. Burada motoru tek başına deneyebilirsin — neyin ne işe yaradığını gör.",
    en: "Firecrawl is the engine that lets your AI agent read the web: it searches, downloads pages into clean text, maps sites and extracts data. Every search and page read in the Deep Research story runs on this engine. Try the engine on its own here — see what each feature does.",
  },
  "fc.point1": {
    tr: "1 · Gerçek çağrılar: her buton canlı web'e gerçek bir istek atar, sahte sonuç dönmez.",
    en: "1 · Real calls: every button fires a live request to the real web — no fake results.",
  },
  "fc.point2": {
    tr: "2 · Anahtar tarayıcıya sızmaz: çağrılar sunucu tarafından yapılır, anahtar sadece .env'de durur.",
    en: "2 · The key never reaches your browser: calls go through the server; the key stays in .env.",
  },
  "fc.point3": {
    tr: "3 · Hikâyeyle aynı motor: Deep Research hikâyesindeki adımlar da buradaki search ve scrape'i kullanır.",
    en: "3 · Same engine as the story: the Deep Research story steps use this very search and scrape.",
  },
  "fc.search.tag": { tr: "arama", en: "search" },
  "fc.search.what": {
    tr: "Web'de arama yapar: başlık + adres + kısa özet döner. Araştırmaya “kim ne yazmış?” diye başlamanın yolu.",
    en: "Searches the live web and returns title + URL + snippet. The way research starts: “who wrote about this?”",
  },
  "fc.search.when": {
    tr: "Bir konuda ilk keşif yaparken — henüz hangi sayfaları okuyacağını bilmiyorken.",
    en: "When exploring a topic for the first time — before you know which pages to read.",
  },
  "fc.scrape.tag": { tr: "sayfa okuma", en: "scrape" },
  "fc.scrape.what": {
    tr: "Tek bir sayfayı indirir, menüleri/reklamları süpürür, temiz metne çevirir. Alıntı yapılacak cümle sayfada gerçekten var mı diye de kontrol eder.",
    en: "Downloads one page, strips menus/ads, turns it into clean text — and verifies the sentence you want to quote really is on the page.",
  },
  "fc.scrape.when": {
    tr: "Arama sonucundan bir sayfayı okumak ve alıntı yapmak istediğinde.",
    en: "When you want to read one page from the search results and quote it.",
  },
  "fc.crawl.tag": { tr: "site tarama", en: "crawl" },
  "fc.crawl.what": {
    tr: "Bir sitenin birden çok sayfasını sırayla gezer ve her birinden temiz metin çıkarır.",
    en: "Walks multiple pages of one site in sequence, extracting clean text from each.",
  },
  "fc.crawl.when": {
    tr: "Tek sayfa yetmediğinde — örn. dokümantasyonun tamamını toplarken.",
    en: "When one page is not enough — e.g. collecting a whole documentation site.",
  },
  "fc.map.tag": { tr: "site haritası", en: "map" },
  "fc.map.what": {
    tr: "Bir sitedeki bağlantıların listesini çıkarır — sayfaları okumadan önce “sitede neler var?” görünümü.",
    en: "Lists the links inside a site — a “what's on this site?” view before reading anything.",
  },
  "fc.map.when": {
    tr: "Hangi alt sayfaları okuyacağına karar verirken — içerik okumadan önce.",
    en: "When deciding which subpages to read — before reading their content.",
  },
  "fc.extract.tag": { tr: "veri çıkarma", en: "extract" },
  "fc.extract.what": {
    tr: "Sayfayı okur ve istediğin bilgiyi senin cümlenle sorarak çıkarır (örn. “ilk 3 haber başlığını listele”).",
    en: "Reads the page and pulls out exactly what you ask for in plain words (e.g. “list the top 3 headlines”).",
  },
  "fc.extract.when": {
    tr: "Sayfadan belirli bir bilgi lazım olduğunda — tamamı değil, sadece o kısım.",
    en: "When you need one specific fact from a page — not the whole page.",
  },
  "fc.slowBadge": { tr: "yavaş — çok sayfa gezer", en: "slow — visits many pages" },
  "fc.llmBadge": { tr: "LLM kullanır", en: "uses an LLM" },
  "fc.tryTitle": { tr: "Dene", en: "Try it" },
  "fc.whenLabel": { tr: "Ne zaman:", en: "When to use:" },
  "fc.tryHint": {
    tr: "gerçek çağrı — internete gider",
    en: "real call — hits the live internet",
  },
  "fc.fieldQuery": { tr: "Arama sorgusu", en: "Search query" },
  "fc.fieldLimit": { tr: "Sonuç sayısı", en: "Result limit" },
  "fc.fieldUrl": { tr: "Sayfa adresi (https://…)", en: "Page URL (https://…)" },
  "fc.fieldPrompt": { tr: "Ne çıkarılsın? (sadece extract)", en: "What should be extracted? (extract only)" },
  "fc.fieldPages": { tr: "Sayfa sayısı", en: "Page count" },
  "fc.runAction": { tr: "{action} çalıştır", en: "Run {action}" },
  "fc.running": { tr: "Çalışıyor…", en: "Running…" },
  "fc.done": { tr: "Tamamlandı", en: "Done" },
  "fc.failed": { tr: "Başarısız", en: "Failed" },
  "fc.searchResults": { tr: "{n} gerçek sonuç", en: "{n} real results" },
  "fc.mapResults": { tr: "{n} bağlantı bulundu", en: "{n} links found" },
  "fc.footnote": {
    tr: "Bu panel Firecrawl kredisini gerçekten harcar (ücretsiz kotasıyla sınırlı). Web araştırması gerektiren hikâye adımları ve Beceriler sekmesindeki web becerileri de aynı anahtarı kullanır.",
    en: "This panel really spends Firecrawl credits (bounded by the free tier). The story steps that need web research and the web skills in the Skills tab use the same key.",
  },

  // ── doctor ──────────────────────────────────────────────────────────────
  "doctor.title": { tr: "Kurulum sağlığı", en: "Installation health" },
  "doctor.desc": {
    tr: "Demo çalışma alanında workbench.py doctor komutunu çalıştırır (tohumlayıcı 6 aracı kurmuş olarak gelir).",
    en: "Runs workbench.py doctor inside the demo workspace (the seeder installs all 6 hosts).",
  },
  "doctor.rerun": { tr: "Yeniden çalıştır", en: "Re-run doctor" },
  "doctor.running": { tr: "Doctor çalışıyor…", en: "Running doctor…" },
  "doctor.overall": { tr: "Genel durum", en: "Overall" },
  "doctor.runtime": { tr: "Python sürümü", en: "Runtime" },
  "doctor.skillsInstalled": { tr: "Kurulu beceri", en: "Skills installed" },
  "doctor.hostsDetected": { tr: "Bulunan araç", en: "Hosts detected" },
  "doctor.check": { tr: "Kontrol", en: "Check" },
  "doctor.status": { tr: "Durum", en: "Status" },
  "doctor.detail": { tr: "Detay", en: "Detail" },
  "doctor.noJson": {
    tr: "Doctor JSON döndürmedi — ham çıktıyı Komut Dene sekmesinden inceleyebilirsin.",
    en: "Doctor did not return JSON — inspect the raw output from the Try Commands tab.",
  },
  "doctor.selfcheckTitle": { tr: "Tedarsikçi tarafsızlığı özkontrolü", en: "Vendor-neutrality selfcheck" },
  "doctor.selfcheckDesc": {
    tr: "Tüm paketi, yasak araştırma-tedarikçisi referansları için tarar — 95 testlik pakette gelen aynı kapı.",
    en: "Scans the whole suite for banned research-vendor references — the same gate that ships in the 95-test suite.",
  },
  "doctor.runSelfcheck": { tr: "Pakette özkontrol çalıştır", en: "Run selfcheck on suite" },

  // ── workspace ───────────────────────────────────────────────────────────
  "ws.hosts": { tr: "Çalışma alanındaki araçlar:", en: "Hosts in workspace:" },
  "ws.reset": { tr: "Çalışma alanını sıfırla", en: "Reset workspace" },
  "ws.reseeding": { tr: "Yeniden tohumlanıyor (~10 sn)…", en: "Reseeding (~10 s)…" },
  "ws.ledgers": { tr: "Durum defterleri", en: "State ledgers" },
  "ws.artifacts": { tr: "Üretilen dosyalar", en: "Generated artifacts" },
  "ws.artifactsDesc": {
    tr: "workbench komutlarının yazdığı ADR'ler, raporlar ve devir dosyaları.",
    en: "ADRs, reports and handoff packs written by workbench commands.",
  },
  "ws.noLedgers": {
    tr: "Henüz defter yok — demo veriyi geri yüklemek için çalışma alanını sıfırla.",
    en: "No ledgers yet — reset the workspace to seed demo data.",
  },
  "ws.noArtifacts": {
    tr: "Henüz dosya yok — {c1} veya {c2} komutlarını dene.",
    en: "No artifacts yet — try {c1} or {c2}.",
  },
  "ws.also": {
    tr: "Ayrıca çalışma alanında: demo-project/, decision-matrix.json, AGENTS.md",
    en: "Also in workspace: demo-project/, decision-matrix.json, AGENTS.md",
  },
  "ws.ledgerJson": { tr: "Durum defteri JSON'u", en: "State ledger JSON" },

  // ── history ─────────────────────────────────────────────────────────────
  "hist.title": { tr: "Çalıştırma geçmişi", en: "Run history" },
  "hist.desc": {
    tr: "Konsoldan çalıştırılan her komut, en yeni en üstte (SQLite'ta saklanır).",
    en: "Every command executed through the console, newest first (persisted in SQLite).",
  },
  "hist.when": { tr: "Zaman", en: "When" },
  "hist.command": { tr: "Komut", en: "Command" },
  "hist.status": { tr: "Durum", en: "Status" },
  "hist.exit": { tr: "Çıkış", en: "Exit" },
  "hist.duration": { tr: "Süre", en: "Duration" },
  "hist.noRuns": {
    tr: "Henüz çalıştırma yok — Komut Dene sekmesinden bir komut ateşle.",
    en: "No runs yet — go fire a command from the Try Commands tab.",
  },
  "hist.loading": { tr: "Yükleniyor…", en: "Loading…" },
  "hist.ago": { tr: "önce", en: "ago" },

  // ── footer ──────────────────────────────────────────────────────────────
  "footer.note": {
    tr: "Demo çalışma alanı: her komut .workspace/ altındaki tohumlanmış, atılabilir defterlerde çalışır.",
    en: "Demo workspace: every command runs against seeded, disposable ledgers under .workspace/.",
  },
  "footer.line": {
    tr: "6 araç · 13 beceri · 95 test · tıkladığın her şey gerçek",
    en: "6 hosts · 13 skills · 95 tests · everything you click is real",
  },
  "footer.readyNote": {
    tr: "13 becerinin tamamı AI agent'ınla hazır: LLM'e bağlı beceriler agent kuruluysa çalışır; sadece web'e çıkanlar (Deep Research, web-search, wide-search) Firecrawl anahtarı ister.",
    en: "All 13 skills are ready via your AI agent: LLM-based skills run wherever the agent is installed; only the web-facing ones (deep-research, web-search, wide-search) need the Firecrawl key.",
  },

  // ── misc ────────────────────────────────────────────────────────────────
  "common.ms": { tr: "ms", en: "ms" },
  "common.lang": { tr: "Dil", en: "Language" },
  "catalog.error": {
    tr: "Komut kataloğu yüklenemedi: {err}",
    en: "Failed to load command catalog: {err}",
  },
}

interface LangContextValue {
  lang: Lang
  setLang: (lang: Lang) => void
  t: (key: string, vars?: Record<string, string | number>) => string
}

const LangContext = createContext<LangContextValue | null>(null)

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("tr")

  /* eslint-disable react-hooks/set-state-in-effect --
     Restoring the persisted language preference must happen after hydration:
     localStorage and navigator are not available during SSR, and reading them
     during the first client render would cause a hydration mismatch. This is
     the same post-mount pattern next-themes uses for the theme. */
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored === "tr" || stored === "en") {
        setLangState(stored)
        return
      }
      const nav = navigator.language?.toLowerCase() ?? ""
      if (nav.startsWith("en")) setLangState("en")
    } catch {
      /* localStorage unavailable — keep Turkish */
    }
  }, [])
  /* eslint-enable react-hooks/set-state-in-effect */

  useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])

  function setLang(next: Lang) {
    setLangState(next)
    try {
      localStorage.setItem(STORAGE_KEY, next)
    } catch {
      /* ignore */
    }
  }

  function t(key: string, vars?: Record<string, string | number>): string {
    let text = STRINGS[key]?.[lang] ?? STRINGS[key]?.en ?? key
    if (vars) {
      for (const [name, value] of Object.entries(vars)) {
        text = text.split(`{${name}}`).join(String(value))
      }
    }
    return text
  }

  return <LangContext.Provider value={{ lang, setLang, t }}>{children}</LangContext.Provider>
}

export function useLang(): LangContextValue {
  const ctx = useContext(LangContext)
  if (!ctx) throw new Error("useLang must be used inside <LangProvider>")
  return ctx
}

/**
 * Pick a localized data field: the Turkish value when the UI language is
 * Turkish and a Turkish value exists, otherwise the English fallback.
 */
export function pickLocalized(
  lang: Lang,
  en: string | undefined,
  tr: string | undefined
): string {
  if (lang === "tr" && tr) return tr
  return en ?? ""
}
