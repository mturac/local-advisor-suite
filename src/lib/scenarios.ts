// AUTO-GENERATED from scripts/scenarios.json by scripts/gen_scenarios_ts.py.
// Every argv below is validated by scripts/test_scenarios.py against a
// freshly seeded demo workspace. Edit the JSON, then regenerate.

export interface Scenario {
  label: string
  command: string
  argv: string[]
  note: string
  /** Turkish note; falls back to `note` when absent. */
  noteTr?: string
  /** Resets (wipes) its ledger before writing — shown amber in the UI. */
  resets?: boolean
  /** Exits non-zero on the seeded workspace by design (mechanical gate). */
  expectFail?: boolean
}

export interface ScenarioGroup {
  title: string
  titleTr?: string
  scenarios: Scenario[]
}

export const SCENARIO_GROUPS: ScenarioGroup[] = [
  {
    title: "Skill routing",
    titleTr: "Beceri yönlendirme",
    scenarios: [
      { label: "load-skills (TR)", command: "load-skills", argv: ["--prompt", "DuckDB mi SQLite mi, eşzamanlı yazma konusunda hangisi daha iyi, karşılaştır"], note: "Route any prompt (TR/EN) to its skills; returns the brief (read order, first command, stop rule). Try --skill NAME or --list too", noteTr: "Herhangi bir prompt'u (TR/EN) becerilere yönlendirir; brief döner (okuma sırası, ilk komut, durma kuralı). --skill AD ve --list de dene" },
      { label: "load-skills --core", command: "load-skills", argv: ["--core", "--prompt", "what is the latest python version and its release date"], note: "Core depth: a run-from-this-card brief — skill, 3-step core loop, first command, stop rule; zero file reading", noteTr: "Çekirdek derinlik: karttan-çalıştır brifingi — beceri, 3 adımlı çekirdek döngü, ilk komut, durma kuralı; sıfır dosya okuma" },
    ],
  },
  {
    title: "Question contract",
    titleTr: "Soru sözleşmesi",
    scenarios: [
      { label: "qc-pin", command: "qc-pin", argv: ["--question", "Should we modernize the demo console's workspace model?", "--decision", "choose between sandbox isolation and shared state this week", "--consumer", "the console maintainer"], note: "Pin the question, the decision it informs and the consumer — the vague-term scan fires on 'modernize'", noteTr: "Soruyu, besleyeceği kararı ve okuyucuyu sabitle — 'modernize' belirsiz kelime taramasını tetikler" },
      { label: "qc-check (the gate)", command: "qc-check", argv: [], note: "READY or NEEDS_INPUT: never answer a question whose decision and consumer are unpinned", noteTr: "READY veya NEEDS_INPUT: kararı ve okuyucusu sabitlenmemiş soruyu asla cevaplama" },
      { label: "qc-assume", command: "qc-assume", argv: ["--assumption", "modernize means the run model, not the visual interface"], note: "Record the interpretation where the question stayed ambiguous — it lands in the answer's caveat", noteTr: "Sorunun belirsiz kaldığı yerdeki yorumu kaydet — cevabın uyarı notuna girer" },
    ],
  },
  {
    title: "Suite health",
    titleTr: "Paket sağlığı",
    scenarios: [
      { label: "doctor", command: "doctor", argv: [], note: "Cross-host install health for all six hosts", noteTr: "Altı aracın kurulum sağlığını tek tabloda gösterir" },
      { label: "selfcheck", command: "selfcheck", argv: ["--path", "../suite"], note: "Structural self-test of the suite itself", noteTr: "Paketin kendi kendini yapısal testi" },
    ],
  },
  {
    title: "Research",
    titleTr: "Araştırma",
    scenarios: [
      { label: "research-status", command: "research-status", argv: [], note: "Ledger snapshot: sources, claims, query budget", noteTr: "Defterin anlık görüntüsü: kaynaklar, iddialar, arama bütçesi" },
      { label: "research-gaps", command: "research-gaps", argv: [], note: "Open knowledge gaps and why they exist", noteTr: "Açık bilgi boşlukları ve neden var oldukları" },
      { label: "research-score", command: "research-score", argv: [], note: "Source quality scoring (tier, freshness, domain)", noteTr: "Kaynak kalite puanı (tür, güncellik, alan adı)" },
      { label: "research-pack", command: "research-pack", argv: [], note: "Render evidence_pack.md for synthesis", noteTr: "Kanıt raporunu evidence_pack.md olarak yazar" },
      { label: "research-log-query", command: "research-log-query", argv: ["--query", "claude code skills directory layout docs", "--tool-used", "console-scenario"], note: "Log a unique query against the budget", noteTr: "Bir aramayı bütçeye kaydeder" },
      { label: "research-add-source", command: "research-add-source", argv: ["--url", "https://code.visualstudio.com/docs/copilot/chat/agent-skills", "--title", "VS Code agent skills documentation", "--publisher", "Microsoft", "--tier", "PRIMARY", "--excerpt", "Agent Skills are folders with a SKILL.md file."], note: "Register a PRIMARY source with excerpt", noteTr: "Alıntılı birincil (PRIMARY) kaynak kaydeder" },
      { label: "research-add-claim", command: "research-add-claim", argv: ["--statement", "VS Code loads agent skills from a skills folder in the workspace", "--source-id", "S1", "--quote", "A skill is a folder with a SKILL.md file; name and description are required.", "--entity", "VS Code", "--field", "skills directory", "--value", "workspace skills folder", "--confidence", "MEDIUM", "--allow-unverified-quote"], note: "Add a PROVISIONAL claim backed by source S1", noteTr: "S1 kaynağına dayalı geçici (PROVISIONAL) iddia ekler" },
      { label: "research-add-gap", command: "research-add-gap", argv: ["--description", "No public benchmark compares skill discovery latency across hosts", "--entity", "All hosts", "--field", "performance", "--query-tried", "agent skills discovery latency benchmark", "--reason", "NO_PUBLIC_SOURCE"], note: "Record a gap with reason NO_PUBLIC_SOURCE", noteTr: "Nedeni 'kaynak yok' olan bir bilgi boşluğu kaydeder" },
      { label: "research-resolve", command: "research-resolve", argv: ["--entity", "Cursor", "--field", "command surface", "--winner-claim", "C3", "--reason", "Primary Cursor docs describe .cursor/rules and generated commands."], note: "Resolve an entity/field to claim C3", noteTr: "Bir varlık/alan çelişkisini C3 lehine çözer" },
      { label: "fetch-url", command: "fetch-url", argv: ["--url", "https://agentskills.io/specification", "--allow-network"], note: "Fetch and cache an https source (explicit opt-in)", noteTr: "Bir https kaynağını çeker ve önbelleğe alır (açık izinle)" },
      { label: "research-init", command: "research-init", argv: ["--topic", "Cross-host portability of agent skill suites", "--sub-question", "How should one SKILL.md serve every host?", "--entity", "Claude Code", "--entity", "Codex", "--field", "skills directory", "--max-queries", "8"], note: "Start a fresh research ledger (wipes sources, claims, gaps)", noteTr: "Yeni boş araştırma defteri açar (kaynak/iddia/boşlukları siler)", resets: true },
    ],
  },
  {
    title: "Spec",
    titleTr: "Spec",
    scenarios: [
      { label: "spec-check", command: "spec-check", argv: [], note: "Spec health: criteria coverage and task links", noteTr: "Spec sağlığı: kriter kapsamı ve görev bağlantıları" },
      { label: "spec-criterion", command: "spec-criterion", argv: ["--story-id", "US1", "--given", "a seeded demo workspace", "--when", "wide-table runs with no arguments", "--then", "an entity by field matrix renders without errors"], note: "Add a Given/When/Then criterion to story US1", noteTr: "US1 hikâyesine Given/When/Then kriteri ekler" },
      { label: "spec-task", command: "spec-task", argv: ["--task", "Add a scenario test for wide-table rendering", "--verifies", "AC1"], note: "Add a task that verifies criterion AC1", noteTr: "AC1 kriterini doğrulayan bir görev ekler" },
      { label: "spec-new", command: "spec-new", argv: ["--goal", "Restart the spec from scratch via the console example scenarios", "--story", "As a developer I want example scenarios so I can explore commands fast", "--non-goal", "Covering every argument combination", "--force"], note: "Restart the spec ledger (wipes stories, criteria, tasks)", noteTr: "Spec defterini sıfırdan açar (hikâye/kriter/görevleri siler)", resets: true },
    ],
  },
  {
    title: "Review & evidence",
    titleTr: "İnceleme ve kanıt",
    scenarios: [
      { label: "review-report", command: "review-report", argv: [], note: "Mechanical verdict: FAIL while any BLOCKING finding is open (seed has MAJOR/MINOR → PASS_WITH_FINDINGS)", noteTr: "Mekanik karar: açık BLOCKING varsa FAIL (hazır veride MAJOR/MINOR var → PASS_WITH_FINDINGS)" },
      { label: "audit-report", command: "audit-report", argv: [], note: "Evidence-ledger integrity audit (claims vs quotes vs sources)", noteTr: "Kanıt defteri bütünlük denetimi (iddia–alıntı–kaynak eşleşmesi)" },
      { label: "verify-delivery", command: "verify-delivery", argv: ["--artifact", "artifacts/demo-report.md"], note: "Delivery gate: artifact present (L1) and spec tasks verified", noteTr: "Teslim kapısı: çıktı dosyası var (L1) ve spec görevleri doğrulanmış" },
      { label: "review-finding", command: "review-finding", argv: ["--file", "demo-project/src/app.py", "--line", "50", "--severity", "MINOR", "--category", "correctness", "--description", "Module uses sys.argv in __main__ without importing sys", "--suggestion", "Add import sys at the top of the module"], note: "Append a MINOR finding on the demo project", noteTr: "Demo projesine MINOR bir bulgu ekler" },
      { label: "review-init", command: "review-init", argv: ["--title", "Second pass review", "--target", "demo-project/src", "--focus", "maintainability", "--force"], note: "Restart the review ledger (wipes findings)", noteTr: "İnceleme defterini sıfırdan açar (bulguları siler)", resets: true },
    ],
  },
  {
    title: "Knowledge",
    titleTr: "Bilgi tabanı",
    scenarios: [
      { label: "kb-search", command: "kb-search", argv: ["--query", "skills"], note: "Deterministic offline keyword search", noteTr: "Çevrimdışı, deterministik anahtar kelime araması" },
      { label: "kb-add", command: "kb-add", argv: ["--question", "Which six hosts does install.py support?", "--answer", "claude, codex, zcode, cursor, opencode and a generic AGENTS.md mode.", "--tag", "install", "--assumed"], note: "Capture a Q&A entry as an explicit assumption", noteTr: "Bir soru-cevabı 'varsayım' olarak kaydeder" },
      { label: "kb-export", command: "kb-export", argv: [], note: "Export the KB to KNOWLEDGE_BASE.md", noteTr: "Bilgi tabanını KNOWLEDGE_BASE.md olarak dışa aktarır" },
    ],
  },
  {
    title: "Data analysis",
    titleTr: "Veri analizi",
    scenarios: [
      { label: "data-register", command: "data-register", argv: ["--path", "demo-project/README.md", "--question", "How many lines and words does the demo README have?"], note: "Pin the dataset first: path, size and SHA-256 go on the record", noteTr: "Önce veri setini sabitle: yol, boyut ve SHA-256 kayda geçer" },
      { label: "data-finding", command: "data-finding", argv: ["--statement", "The README mentions 7 names in backticks", "--method", "grep -o '`[^`]*`' demo-project/README.md | wc -l", "--result", "7 names"], note: "Log a number together with the exact command that produced it", noteTr: "Sayıyı üreten tam komutla birlikte kayda geçir" },
      { label: "data-gap", command: "data-gap", argv: ["--description", "A per-author word split is not computable from the README", "--reason", "NO_DATA: the file has no author column"], note: "Declare what the file cannot answer instead of guessing", noteTr: "Dosyanın cevaplayamadığını tahmin etmek yerine beyan et" },
      { label: "data-report", command: "data-report", argv: ["--answer", "The demo README has 8 lines and 52 words; a per-section split is not computable."], note: "Render ANALYSIS.md; numbers in the answer are linted against the findings", noteTr: "ANALYSIS.md üretir; cevaptaki sayılar bulgularla karşılanmak zorunda" },
    ],
  },
  {
    title: "Devil's advocate",
    titleTr: "Şeytanın avukatı",
    scenarios: [
      { label: "devil-plan (archetype)", command: "devil-plan", argv: ["--archetype", "migrate"], note: "The attack plan for this kind of plan: a migration dies on rollback-path first, not on features", noteTr: "Bu plan türü için saldırı planı: bir migrasyon önce geri-dönüş yolunda ölür, özelliklerde değil" },
      { label: "devil-premortem", command: "devil-premortem", argv: ["--failure-story", "Twelve months on, the isolated sandbox console was abandoned: every click paid a cold start, and the seeded ledgers nobody could see made the demo useless", "--cause", "cold-start seconds were never measured before the decision", "--cause", "the seeded ledger history had no viewer in sandbox mode"], note: "The failure story, written before the challenges — assuming failure surfaces the doubts politeness withholds", noteTr: "İtirazlardan önce yazılan başarısızlık hikâyesi — başarısızlığı varsaymak, nezaketin sakladığı şüpheleri yüzeye çıkarır" },
      { label: "devil-outside (optimism bias)", command: "devil-outside", argv: ["--reference-class", "console workspace isolation attempts by small teams", "--base-rate", "35"], note: "The outside view: a bad base rate with no argued adjustment auto-opens a SERIOUS optimism-bias challenge", noteTr: "Dış görünüm: savunulmamış kötü temel oran, mekanik olarak SERIOUS iyimserlik-yanlılığı itirazı açar" },
      { label: "devil-consequence", command: "devil-consequence", argv: ["--l1", "each scenario run starts from an empty sandbox, so no ledger survives between clicks", "--l2", "users never see a filled ledger and conclude the suite produces nothing inspectable", "--l3", "the demo stops teaching, and the console loses its reason to exist"], note: "Second-order effects, three levels deep: the failures that surprise people are rarely first-order", noteTr: "İkinci derece etkiler, üç seviye derin: insanı şaşırtan başarısızlıklar nadiren birinci derecedir" },
      { label: "devil-challenge", command: "devil-challenge", argv: ["--assumption", "the shared workspace can be restored if isolation disappoints", "--attack", "Once scenario definitions depend on per-run state, wiring them back to a shared ledger is a manual rework of every scenario", "--category", "reversibility", "--severity", "SERIOUS", "--defeater", "a documented flag that switches the runner between shared and isolated modes"], note: "Attack a load-bearing assumption; every attack names what would defeat it", noteTr: "Yük taşıyan bir varsayıma saldır; her saldırı kendi yenilgisini neyin sağlayacağını söyler" },
      { label: "devil-rebuttal", command: "devil-rebuttal", argv: ["--id", "C1", "--rebuttal", "The seeded workspace deliberately pre-fills every ledger, so even a fresh isolated run starts from a realistic, inspectable state", "--basis", "evidence: seed_workspace.py pre-registers all ledgers before any run"], note: "Answer an open challenge with a basis; a sound rebuttal leaves the verdict", noteTr: "Açık bir itirazı temeliyle cevapla; sağlam cevap karardan çıkar" },
      { label: "devil-verdict", command: "devil-verdict", argv: ["--kill-criterion", "any scenario still reads state from a previous run after isolation"], note: "Mechanical gate: BLOCK while a FATAL stands; renders CHALLENGE.md with guards and kill criteria", noteTr: "Mekanik kapı: ayakta bir FATAL varken BLOCK; CHALLENGE.md guard ve kill kriterleriyle üretilir" },
      { label: "devil-open (TR)", command: "devil-open", argv: ["--force", "--claim", "Konsolun paylaşımlı çalışma alanını her çalıştırmada izole kum havuzuna çevirelim", "--steelman", "İzole çalıştırmalar birbirinin defter durumunu bozamaz; her senaryo temiz başlangıçtan tekrar üretilebilir"], note: "Open a session on a new claim — the honest steelman comes first (resets the ledger)", noteTr: "Yeni bir iddiayla oturum aç — önce dürüst çelik-adam gelir (defteri sıfırlar)", resets: true },
    ],
  },
  {
    title: "Get More Perspective",
    titleTr: "Farklı Bakış Açıları",
    scenarios: [
      { label: "load-skills → panel (TR)", command: "load-skills", argv: ["--prompt", "uzmanlar ne düşünür: fiyatlandırmayı değiştirmeli miyiz, danışma paneli kur"], note: "Route a perspectives ask to the panel skill; returns the brief with the read order and first command", noteTr: "Perspektif talebini panel becerisine yönlendirir; okuma sırası ve ilk komutla brief döner" },
      { label: "panel-voice (skeptic, evidence-mandated)", command: "panel-voice", argv: ["--role", "skeptic", "--stance", "oppose", "--force", "--risk", "The canary measures announcement shock only; renewal-cycle churn stays invisible until month two", "--trigger", "Renewal-day downgrades exceed 5 percent in the first billing cycle after the raise", "--evidence", "EV1", "--confidence", "60", "--reasoning", "Revising the risk after the operator's challenge: the canary cannot see renewal churn, so the watch must move to the first billing cycle after the raise lands"], note: "A seat revises its opinion with --force; role-mandated fields (risk + trigger + evidence) are enforced", noteTr: "Bir koltuk görüşünü --force ile revize eder; role zorunlu alanlar (risk + tetik + kanıt) denetlenir" },
      { label: "panel-evidence (table a quote)", command: "panel-evidence", argv: ["--via", "fetch-url", "--source-url", "https://status.example.com/incidents/2026-pricing", "--quote", "Incident report: pricing page showed mixed prices for 40 minutes during the last change", "--label", "EV3"], note: "Table a verbatim quote with its source; the skeptic and finance seats must cite labels like this before speaking", noteTr: "Kaynağıyla birebir alıntıyı masaya koyar; skeptic ve finance koltukları konuşmadan önce böyle etiketler atıf almalı" },
      { label: "panel-cross (open challenge)", command: "panel-cross", argv: ["--from-role", "finance", "--to-role", "customer-advocate", "--challenge", "Grandfathering for 12 months delays the revenue effect by four renewal cycles; does your condition survive contact with the budget"], note: "One seat challenges another; leave --response off and the challenge stays OPEN in the report", noteTr: "Bir koltuk diğerini sorgular; --response verilmezse itiraz raporda OPEN olarak kalır" },
      { label: "panel-synth", command: "panel-synth", argv: [], note: "Mechanical verdict — UNANIMOUS / CONDITIONS / MAJORITY_WITH_DISSENT / SPLIT; manufactured agreement is refused and a finance dissent is never buried. Renders PANEL.md", noteTr: "Mekanik karar — oybirliği / koşullu / çoğunluk-itirazlı / bölünmüş; yapay uzlaşı reddedilir, finance itirazı asla gömülmez. PANEL.md üretir", resets: true },
      { label: "panel-open (reconvene)", command: "panel-open", argv: ["--force", "--question", "Should the console ship usage-based pricing instead of seats", "--context", "Panel round two: same competitor set, plus metering telemetry from the last quarter"], note: "Reconvene the board with --force (wipes opinions, evidence and cross-examinations); --roles reshapes the seats", noteTr: "Panelden --force ile yeniden toplanır (görüş, kanıt ve sorgular silinir); --roles koltukları yeniden kurar", resets: true },
    ],
  },
  {
    title: "Decision journal",
    titleTr: "Karar defteri",
    scenarios: [
      { label: "journal-log", command: "journal-log", argv: ["--decision", "Keep the shared workspace and add per-run snapshots instead of sandboxes", "--prediction", "snapshot restore keeps every click under 300ms in the next month of use", "--confidence", "70", "--review-by", "2026-12-12", "--mind-changer", "any click measured above one second in daily use"], note: "Log the decision with its falsifiable prediction, confidence and review date", noteTr: "Kararı, çürütülebilir tahmini, güven düzeyi ve inceleme tarihiyle kaydet" },
      { label: "journal-resolve", command: "journal-resolve", argv: ["--id", "J1", "--outcome", "HIT", "--lesson", "the snapshot path avoided the cold-start tax entirely; measure latency before choosing isolation"], note: "Grade it against reality — HIT, MISS or PARTIAL, with the lesson you would act on", noteTr: "Gerçeğe göre notlandır — HIT, MISS veya PARTIAL, üzerinde eyleme geçilecek dersle" },
      { label: "journal-report (calibration)", command: "journal-report", argv: [], note: "Hit rate vs claimed confidence per band; overconfidence past 15 points is a flag, not a feeling", noteTr: "Bant bazında isabet oranı vs iddia edilen güven; 15 puanı aşan iyimserlik bayraktır, his değil" },
    ],
  },
  {
    title: "Advice & decisions",
    titleTr: "Tavsiye ve kararlar",
    scenarios: [
      { label: "advise-intake", command: "advise-intake", argv: ["--question", "Should v3.1 add a security-audit skill for offline prompt-injection scanning?", "--context", "Planning the next release of the suite", "--constraint", "Keep every check offline and deterministic", "--non-goal", "Network scanning or external services", "--mode", "planning"], note: "Structured intake before advising (overwrites previous intake)", noteTr: "Tavsiye öncesi yapılandırılmış giriş (öncekini ezer)" },
      { label: "decision-score", command: "decision-score", argv: ["--spec-file", "decision-matrix.json"], note: "Weighted scoring of the seeded decision matrix", noteTr: "Hazır karar matrisinin tartılı puanlaması" },
      { label: "wide-table", command: "wide-table", argv: [], note: "Entity x field evidence matrix from the ledger", noteTr: "Defterden varlık × alan kanıt matrisi" },
      { label: "adr-new", command: "adr-new", argv: ["--title", "Adopt grouped example scenarios in the console", "--dir", "docs/adr", "--owner", "console-team"], note: "Write a new numbered ADR to docs/adr/", noteTr: "docs/adr/ altına yeni numaralı ADR yazar" },
      { label: "adr-check", command: "adr-check", argv: ["--file", "docs/adr/0001-use-a-single-shared-demo-workspace-for-the-test-console.md"], note: "Hygiene check: catches unfilled placeholders in the seeded ADR", noteTr: "Sağlık kontrolü: hazır ADR'deki boş kalan yerleri yakalar (bilerek hata verir)", expectFail: true },
    ],
  },
  {
    title: "Debug",
    titleTr: "Hata ayıklama",
    scenarios: [
      { label: "debug-report", command: "debug-report", argv: [], note: "Hypothesis ledger and circuit-breaker state", noteTr: "Hipotez defteri ve sigorta (circuit-breaker) durumu" },
      { label: "debug-hypothesis", command: "debug-hypothesis", argv: ["--symptom", "kb-search returns no hits for a freshly added entry", "--statement", "The search index is cached and not refreshed after kb-add", "--prediction", "The new entry is found on the next kb-search run", "--test-command", "python3 workbench.py kb-search --query freshly", "--status", "PENDING", "--target-file", "demo-project/src/app.py"], note: "Add a falsifiable hypothesis with a prediction", noteTr: "Öngörülü, çürütülebilir bir hipotez ekler" },
    ],
  },
  {
    title: "Artifacts",
    titleTr: "Çıktılar",
    scenarios: [
      { label: "artifact-list", command: "artifact-list", argv: [], note: "List artifact-studio templates", noteTr: "Hazır çıktı şablonlarını listeler" },
      { label: "artifact-new", command: "artifact-new", argv: ["--type", "technical-report", "--title", "Scenario coverage report", "--output", "artifacts/scenario-coverage.md", "--force"], note: "Scaffold a technical report artifact", noteTr: "Teknik rapor çıktısı oluşturur" },
    ],
  },
  {
    title: "Handoff",
    titleTr: "Devir",
    scenarios: [
      { label: "handoff-check", command: "handoff-check", argv: [], note: "Validate the seeded handoff pack (freshness, sections)", noteTr: "Hazır devir dosyasını doğrular (tazelik, bölümler)" },
      { label: "handoff-pack", command: "handoff-pack", argv: ["--title", "Scenario walkthrough session", "--session-status", "PARTIAL", "--summary", "Explored the example scenarios across every command group", "--completed", "Ran research, spec, review and knowledge scenarios", "--next-step", "Try the amber reset scenarios, then re-seed the workspace"], note: "Write a PARTIAL session handoff pack", noteTr: "PARTIAL durumunda bir devir dosyası yazar" },
    ],
  },
  {
    title: "Scope",
    titleTr: "Kapsam",
    scenarios: [
      { label: "scope-read", command: "scope-read", argv: ["--project-root", "demo-project", "--file", "src/app.py"], note: "Numbered, checksummed read of a demo file", noteTr: "Demo dosyasını numaralı ve sağlamalı okur" },
      { label: "scope-scan", command: "scope-scan", argv: ["--project-root", "demo-project", "--pattern", "TODO|FIXME|BUG", "--ignore-case"], note: "Scan the demo project for TODO/FIXME/BUG markers", noteTr: "Demo projede TODO/FIXME/BUG işaretlerini tarar" },
    ],
  },
]

export const SCENARIO_COUNT = 64
