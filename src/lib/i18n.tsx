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
    tr: "{commands} komut · çevrimdışı · tedarikçi yok",
    en: "{commands} commands · offline · zero-vendor",
  },

  // ── hero ────────────────────────────────────────────────────────────────
  "hero.badge": {
    tr: "v3.0.0 · 38 komut · 13 beceri · tamamen çevrimdışı",
    en: "v3.0.0 · 38 commands · 13 skills · fully offline",
  },
  "hero.titleA": { tr: "Tarayıcıda dene.", en: "Try it right here." },
  "hero.titleB": { tr: "Kurulum yok, hesap yok.", en: "No setup. No account." },
  "hero.sub": {
    tr: "Bu sayfa Local Advisor Suite'in 38 komutunu gerçekten çalıştırır — güvenli bir demo alanında. Bir hikâye seç, Çalıştır'a bas, gerçekte ne olduğunu izle.",
    en: "This page actually runs the suite's 38 commands — inside a safe demo workspace. Pick a story, press Run, and watch what really happens.",
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
    tr: "Kum havuzu modu: 38 komutun tamamı, hazır çalışan argümanlarla. Yeni misin? Önce Hikâyeler sekmesinde bir hikâyeyi baştan sona çalıştır.",
    en: "Sandbox mode: all 38 commands with pre-filled working arguments. New here? Run a full story in the Stories tab first.",
  },
  "runner.allCommands": { tr: "38 komutun tamamı", en: "all 38 commands" },
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
    tr: "Pakette {n} beceri var — her biri kendi klasöründe duran, references + templates + examples içeren bir SKILL.md.",
    en: "{n} skills bundled in the suite — each a self-contained SKILL.md with references, templates and examples.",
  },
  "skills.refresh": { tr: "Yenile", en: "Refresh" },
  "skills.files": { tr: "dosya", en: "files" },
  "skills.example": { tr: "örnek", en: "example" },
  "skills.examples": { tr: "örnek", en: "examples" },

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
