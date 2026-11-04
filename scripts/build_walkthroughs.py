#!/usr/bin/env python3
"""Rebuild scripts/walkthroughs.json — v3 storytelling rewrite.

Design rules for this rewrite (learned the hard way):
  * Every step is written so someone who has never seen the suite can follow
    it: WHAT the step does and WHY it exists, in plain sentences.
  * Flows are grouped into chapters ("acts") so the story has a shape.
  * A storyIntro sets the scene — including the honest framing that in real
    life an LLM host (Claude Code / Codex / Cursor) plays these steps, and
    here in the demo YOU play that role.
  * The research flow runs REAL web research through Firecrawl (search +
    scrape), and the scraped results feed the ledger commands via
    {{stepId.field}} interpolation.
  * The decide flow ends with a dedicated "devil's advocate" chapter: the
    steelman counter-argument and pre-mortem sections the tool deliberately
    refuses to fill.

Verbatim quotes below were verified against the live pages via Firecrawl
scrape on 2026-11-04. The firecrawl route checks them again at run time.

Usage: python3 scripts/build_walkthroughs.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts" / "walkthroughs.json"

# ── verified verbatim quotes (checked live via Firecrawl) ──────────────────
WAL_QUOTE = (
    "WAL provides more concurrency as readers do not block writers and "
    "a writer does not block readers. Reading and writing can proceed "
    "concurrently."
)
DUCK_QUOTE = (
    "As long as there are no write conflicts, multiple concurrent writes will "
    "succeed. Appends will never conflict, even on the same table."
)
POSTHOG_QUOTE = (
    "It follows a MVCC design \u2013 where row versioning is used to avoid "
    "conflicting reads and writes \u2013 and can support a single writer with "
    "multiple concurrent readers."
)

WAL_URL = "https://www.sqlite.org/wal.html"
DUCK_URL = "https://duckdb.org/docs/stable/connect/concurrency"
POSTHOG_URL = "https://posthog.com/blog/duckdb-vs-sqlite"


def S(title, title_tr, explain, explain_tr, see, see_tr, **kw):
    """Step factory: bilingual title/explain/see plus kind-specific fields."""
    step = {"title": title, "title_tr": title_tr}
    if explain is not None:
        step["explain"] = explain
        step["explain_tr"] = explain_tr
    if see is not None:
        step["see"] = see
        step["see_tr"] = see_tr
    step.update(kw)
    return step


RESEARCH = {
    "id": "research",
    "icon": "flask",
    "title": "Deep research: answer a question with evidence",
    "title_tr": "Derin araştırma: bir soruyu kanıtlarla cevapla",
    "subtitle": (
        "A real question — 'DuckDB or SQLite?' — gets honestly researched: search "
        "the live web with Firecrawl, read the pages, tie every claim to a "
        "word-for-word quote, catch a contradiction, settle it, and finish with "
        "a cited report."
    ),
    "subtitle_tr": (
        "Gerçek bir soru: 'DuckDB mi, SQLite mi?' Web'de canlı ara (Firecrawl "
        "gerçekten çalışır), sayfaları oku, her iddiayı kelimesi kelimesine "
        "alıntıya bağla, çelişkiyi yakala, çöz ve kanıtlı raporla bitir."
    ),
    "outcome": "a cited evidence report (markdown file)",
    "outcome_tr": "kanıtlı araştırma raporu (markdown dosyası)",
    "time_min": 4,
    "story_intro": (
        "In this story, YOU play the AI assistant. In real life Claude Code or "
        "Cursor does this job: it searches the web (through Firecrawl), reads "
        "pages, and writes what it learned into a notebook — the research "
        "ledger. Why a notebook at all? So that at the end, every 'how do you "
        "know that?' has a specific answer: which page, which sentence. All "
        "19 steps are real: the searches hit the live internet, the commands "
        "write the real notebook. Press Run step by step and watch the result "
        "panel under each step."
    ),
    "story_intro_tr": (
        "Bu hikâyede YAPAY ZEKÂNIN ROLÜNDESİN. Gerçek hayatta bunu Claude Code "
        "veya Cursor yapar: web'de arar (Firecrawl ile), sayfaları okur, "
        "öğrendiklerini bir deftere yazar — araştırma defterine. Neden defter? "
        "Çünkü sonunda her 'bunu nereden biliyorsun?' sorusunun tek tek cevabı "
        "olsun: hangi sayfa, hangi cümle. 19 adımın hepsi gerçek: aramalar "
        "canlı internete gider, komutlar gerçek defteri yazar. Adım adım "
        "'Çalıştır'a bas ve her adımın altındaki sonuç panelini izle."
    ),
    "chapters": [
        {"title": "Write the question down", "title_tr": "Soruyu yaz"},
        {"title": "Search and read the web — Firecrawl", "title_tr": "Web'de ara ve oku — Firecrawl"},
        {"title": "Turn findings into claims", "title_tr": "Öğrendiklerini iddiaya çevir"},
        {"title": "Catch and settle the contradiction", "title_tr": "Çelişkiyi yakala ve çöz"},
        {"title": "Produce the report", "title_tr": "Raporu çıkar"},
    ],
    "steps": [
        # ── ch1: write the question ────────────────────────────────────────
        S(
            "Open the notebook, write the question",
            "Defteri aç, soruyu yaz",
            "Every research starts with one sentence: 'DuckDB or SQLite?' This "
            "command writes the question on the notebook's cover, adds 2 "
            "sub-questions and a 'max 8 searches' limit. Why a limit? So the "
            "research can't surf forever — at some point it must stop and write.",
            "Her araştırma tek cümleyle başlar: 'DuckDB mi, SQLite mi?' Bu komut "
            "soruyu defterin kapağına yazar, yanına 2 alt soru ve 'en fazla 8 "
            "arama' sınırı koyar. Sınır niye var? Araştırma sonsuza kadar sörf "
            "yapamasın diye — bir noktada durup yazmak zorunda.",
            "status: OK — topic + 2 sub-questions registered",
            "status: OK — konu + 2 alt soru kaydedildi",
            chapter=1,
            command="research-init",
            argv=[
                "--topic",
                "Which local database engine handles concurrent analytics better: DuckDB or SQLite?",
                "--sub-question",
                "How does SQLite handle concurrent readers and writers?",
                "--sub-question",
                "How does DuckDB handle writes inside one process vs. across processes?",
                "--entity",
                "DuckDB",
                "--entity",
                "SQLite",
                "--field",
                "concurrency model",
                "--max-queries",
                "8",
            ],
            pick="topic",
            pick_label="Topic",
            pick_label_tr="Konu",
        ),
        # ── ch2: search & read (Firecrawl) ────────────────────────────────
        S(
            "Search the web — a real search",
            "Web'de ara — gerçek arama",
            "Firecrawl's Search feature really runs here: it queries the live "
            "web and returns 5 real pages (title + URL + snippet). This is "
            "exactly how an AI starts research: 'who wrote about this?' The "
            "results come from today's internet — tomorrow they may differ "
            "slightly, and that is normal.",
            "Firecrawl'ın Search özelliği burada GERÇEKTEN çalışır: canlı "
            "web'de arama yapar ve 5 gerçek sayfa getirir (başlık + adres + "
            "özet). Yapay zekâ araştırmaya tam böyle başlar: 'bu konuda kim ne "
            "yazmış?' Sonuçlar bugünkü internetten gelir — yarın biraz farklı "
            "olabilir, bu gayet normal.",
            "5 real results: title + URL + snippet",
            "5 gerçek sonuç: başlık + adres + kısa özet",
            chapter=2,
            kind="firecrawl",
            id="search1",
            action="search",
            params={"query": "duckdb sqlite concurrent readers writers", "limit": 5},
            pick="results.0.title",
            pick_label="First result",
            pick_label_tr="İlk sonuç",
        ),
        S(
            "Log the search: charge the budget",
            "Aramayı deftere yaz: bütçeden düş",
            "The notebook records the search you just made; 1 of your 8-search "
            "budget is now spent. It looks tiny, but this is the whole point of "
            "auditable research: what you searched, and when, is on the record.",
            "Defter, az önce yaptığın aramayı 'yaptım' diye kaydeder; 8 aramalık "
            "bütçenin 1'i gitti. Küçük görünüyor ama işin tüm özü bu: ne zaman "
            "ne aradın, hepsi kayıtta. Denetlenebilir araştırma dediğimiz şey.",
            "queries_executed: 1 of 8",
            "queries_executed: 1 / 8",
            chapter=2,
            command="research-log-query",
            argv=[
                "--query",
                "duckdb sqlite concurrent readers writers",
                "--tool-used",
                "firecrawl-search",
            ],
            pick="queries_executed",
            pick_label="Searches spent",
            pick_label_tr="Harcanan arama",
        ),
        S(
            "Read SQLite's official page",
            "SQLite'in resmi sayfasını oku",
            "Firecrawl's Scrape feature really downloads this page, strips the "
            "menus and turns it into clean text. It also checks the sentence we "
            "marked: 'is the sentence I want to quote actually on this page?' "
            "Green check if yes; if not, the step deliberately fails — made-up "
            "quotes are not allowed in this notebook.",
            "Firecrawl'ın Scrape özelliği bu sayfayı GERÇEKTEN indirir, "
            "menüleri süpürür ve temiz metne çevirir. Bir de işaretlediğimiz "
            "cümleyi kontrol eder: 'alıntı yapacağım cümle bu sayfada gerçekten "
            "var mı?' Varsa yeşil onay; yoksa adım bilerek düşer — bu deftere "
            "uydurma alıntı giremez.",
            "page title + clean text + 'quote found on page ✓'",
            "sayfa başlığı + temiz metin + 'alıntı sayfada bulundu ✓'",
            chapter=2,
            kind="firecrawl",
            id="scrapeWal",
            action="scrape",
            params={"url": WAL_URL, "quote": WAL_QUOTE},
            pick="quoteFound",
            pick_label="Quote on page?",
            pick_label_tr="Alıntı sayfada mı?",
        ),
        S(
            "File the page into the notebook as card S1",
            "Sayfayı deftere 'S1' kartı olarak kaydet",
            "The page you just read is now card S1 in the notebook. Look "
            "closely: the URL, title and excerpt were not typed by hand — they "
            "flowed automatically from the previous step's result (the "
            "{{scrapeWal.…}} parts of the command). From now on, 'how do you "
            "know?' is answered by pointing at S1.",
            "Az önce okuduğun sayfa artık defterde S1 kartı. Dikkatli bak: "
            "adres, başlık ve alıntı bölge elle yazılmadı — bir önceki adımın "
            "sonucundan otomatik aktı (komuttaki {{scrapeWal.…}} yazan "
            "yerler). Artık 'bunu nereden biliyorsun?' dendiğinde S1 "
            "gösterilecek.",
            "status: OK — source S1 registered (tier PRIMARY)",
            "status: OK — S1 kaynağı kaydedildi (PRIMARY)",
            chapter=2,
            command="research-add-source",
            argv=[
                "--source-id",
                "S1",
                "--url",
                "{{scrapeWal.url}}",
                "--title",
                "{{scrapeWal.title}}",
                "--publisher",
                "SQLite",
                "--tier",
                "PRIMARY",
                "--excerpt",
                "{{scrapeWal.excerpt}}",
            ],
            pick="source_id",
            pick_label="Source id",
            pick_label_tr="Kaynak no",
        ),
        S(
            "Read DuckDB's official page",
            "DuckDB'nin resmi sayfasını oku",
            "Same job for the second engine. DuckDB's own documentation is a "
            "PRIMARY source: the party that knows the engine best. The marked "
            "sentence says non-conflicting writes within one process succeed — "
            "we will use exactly that sentence in claim C2 shortly.",
            "İkinci motor için aynı iş. DuckDB'nin kendi dokümantasyonu "
            "BİRİNCİL (PRIMARY) kaynaktır: motoru en iyi bilen taraf. "
            "İşaretlenen cümle 'tek süreç içinde çakışmayan yazmalar başarılı "
            "olur' diyor — bu cümleyi birazdan C2 iddiasında birebir "
            "kullanacağız.",
            "clean text + quote found ✓",
            "temiz metin + alıntı bulundu ✓",
            chapter=2,
            kind="firecrawl",
            id="scrapeDuck",
            action="scrape",
            params={"url": DUCK_URL, "quote": DUCK_QUOTE},
            pick="quoteFound",
            pick_label="Quote on page?",
            pick_label_tr="Alıntı sayfada mı?",
        ),
        S(
            "Second source card: S2",
            "İkinci kaynak kartı: S2",
            "Like S1, but for DuckDB. The notebook now holds two primary "
            "sources. Remember: this card was also filled from the page that "
            "was really downloaded seconds ago — nothing here is hand-waved.",
            "S1 gibi, DuckDB için. Defterde artık iki birincil kaynak var. "
            "Unutma: bu kart da az önce GERÇEKTEN indirilen sayfadan dolduruldu "
            "— burada elle hazırlanmış hiçbir şey yok.",
            "status: OK — source S2 registered (tier PRIMARY)",
            "status: OK — S2 kaynağı kaydedildi (PRIMARY)",
            chapter=2,
            command="research-add-source",
            argv=[
                "--source-id",
                "S2",
                "--url",
                "{{scrapeDuck.url}}",
                "--title",
                "{{scrapeDuck.title}}",
                "--publisher",
                "DuckDB",
                "--tier",
                "PRIMARY",
                "--excerpt",
                "{{scrapeDuck.excerpt}}",
            ],
            pick="source_id",
            pick_label="Source id",
            pick_label_tr="Kaynak no",
        ),
        S(
            "Read a blog post too (a secondary source)",
            "Bir blog yazısını da oku (ikincil kaynak)",
            "Real research doesn't only read official docs — blogs get read "
            "too. But they are labeled SECONDARY: the author learned the topic "
            "from someone else. Notice something: this post says DuckDB is 'a "
            "single writer'… while the official doc just said 'multiple "
            "concurrent writes succeed'. Do you smell it yet?",
            "Gerçek araştırma sadece resmi doküman okumaz — bloglar da okunur. "
            "Ama etiketleri İKİNCİL (SECONDARY): yazar konuyu başkasından "
            "öğrenmiştir. Bir şeye dikkat: bu yazı DuckDB için 'tek yazıcı' "
            "diyor… resmi doküman ise az önce 'çoklu eşzamanlı yazma başarılı "
            "olur' demişti. Kokuyu aldın mı?",
            "clean text + quote found ✓",
            "temiz metin + alıntı bulundu ✓",
            chapter=2,
            kind="firecrawl",
            id="scrapeBlog",
            action="scrape",
            params={"url": POSTHOG_URL, "quote": POSTHOG_QUOTE},
            pick="quoteFound",
            pick_label="Quote on page?",
            pick_label_tr="Alıntı sayfada mı?",
        ),
        S(
            "Third source card: S3 (secondary)",
            "Üçüncü kaynak kartı: S3 (ikincil)",
            "The blog enters the notebook too, stamped SECONDARY on its card. "
            "In the scoring step, secondary sources will earn fewer points — "
            "note that already; it matters at the end.",
            "Blog da deftere giriyor, ama kartında İKİNCİL damgası var. Puanlama "
            "adımında ikincil kaynaklar daha az puan alacak — bunu şimdiden "
            "not et; sonda işe yarayacak.",
            "status: OK — source S3 registered (tier SECONDARY)",
            "status: OK — S3 kaynağı kaydedildi (SECONDARY)",
            chapter=2,
            command="research-add-source",
            argv=[
                "--source-id",
                "S3",
                "--url",
                "{{scrapeBlog.url}}",
                "--title",
                "{{scrapeBlog.title}}",
                "--publisher",
                "PostHog",
                "--tier",
                "SECONDARY",
                "--excerpt",
                "{{scrapeBlog.excerpt}}",
            ],
            pick="source_id",
            pick_label="Source id",
            pick_label_tr="Kaynak no",
        ),
        # ── ch3: claims ────────────────────────────────────────────────────
        S(
            "Claim C1: 'in SQLite, readers don't block the writer'",
            "İddia C1: 'SQLite'te okuyucu yazıcıyı bloklamaz'",
            "Turn what you learned into a one-sentence claim and paste in the "
            "QUOTE. The tool searches the quote word-for-word inside card S1's "
            "excerpt; if it finds it, the claim gets a VERIFIED stamp. A claim "
            "= sentence + quote + source card. Without all three, it doesn't "
            "count as knowledge.",
            "Öğrendiğin şeyi tek cümlelik iddiaya çevir ve ALINTIYI yapıştır. "
            "Araç, alıntıyı S1 kartının özetinde kelimesi kelimesine arar; "
            "bulursa iddiaya VERIFIED (doğrulandı) damgası basar. İddia = "
            "cümle + alıntı + kaynak kartı. Üçü bir arada değilse bilgi sayılmaz.",
            "quote_verified_in_excerpt: true — C1 VERIFIED",
            "quote_verified_in_excerpt: true — C1 doğrulandı",
            chapter=3,
            command="research-add-claim",
            argv=[
                "--claim-id",
                "C1",
                "--statement",
                "SQLite in WAL mode: readers do not block the writer and the writer does not block readers",
                "--source-id",
                "S1",
                "--quote",
                WAL_QUOTE,
                "--entity",
                "SQLite",
                "--field",
                "concurrency model",
                "--value",
                "readers and one writer run concurrently (WAL)",
                "--confidence",
                "HIGH",
                "--sub-question",
                "Q1",
            ],
            pick="quote_verified_in_excerpt",
            pick_label="Quote verified?",
            pick_label_tr="Alıntı doğrulandı mı?",
        ),
        S(
            "Claim C2: 'DuckDB allows concurrent writes in one process'",
            "İddia C2: 'DuckDB'de tek süreçte eşzamanlı yazma olur'",
            "Same mechanism, for DuckDB. The quote comes from S2. Now hear the "
            "alarm bells: this claim says 'multiple concurrent writes'… but the "
            "blog said 'a single writer'. The contradiction hasn't fired yet — "
            "it fires in the next step.",
            "Aynı düzenek, DuckDB için. Alıntı S2'den. Şimdi çan seslerini duy: "
            "bu iddia 'çoklu eşzamanlı yazma' diyor… ama blog 'tek yazıcı' "
            "demişti. Çelişki henüz patlamadı — bir sonraki adımda patlayacak.",
            "C2 VERIFIED — value: 'multiple concurrent writes inside one process'",
            "C2 doğrulandı — değer: 'tek süreçte çoklu eşzamanlı yazma'",
            chapter=3,
            command="research-add-claim",
            argv=[
                "--claim-id",
                "C2",
                "--statement",
                "DuckDB allows multiple concurrent writes inside a single process, as long as they do not conflict",
                "--source-id",
                "S2",
                "--quote",
                DUCK_QUOTE,
                "--entity",
                "DuckDB",
                "--field",
                "concurrency model",
                "--value",
                "multiple concurrent writes inside one process",
                "--confidence",
                "HIGH",
                "--sub-question",
                "Q2",
            ],
            pick="claim_id",
            pick_label="Claim id",
            pick_label_tr="İddia no",
        ),
        S(
            "Claim C3: 'DuckDB is single-writer' (says the blog)",
            "İddia C3: 'DuckDB tek yazıcıdır' (blog böyle diyor)",
            "Record the blog's sentence as-is — and you already see it: C2 said "
            "'multiple writes' while C3 says 'a single writer', both about "
            "DuckDB's 'concurrency model' field. The notebook will catch this "
            "clash by itself in the next step. Your only job was to write both "
            "sources down honestly; judging is the notebook's job.",
            "Blogun cümlesini aynen kaydet — ve sen zaten görüyorsun: C2 'çoklu "
            "yazma' derken C3 'tek yazıcı' diyor, ikisi de DuckDB'nin "
            "'concurrency model' alanı hakkında. Defter bu çatışmayı bir "
            "sonraki adımda KENDİSİ yakalayacak. Senin tek görevin iki kaynağı "
            "da dürüstçe yazmaktı; yargılamak defterin işi.",
            "C3 recorded — the clash signal is now in the notebook",
            "C3 kaydedildi — çelişki sinyali artık defterde",
            chapter=3,
            command="research-add-claim",
            argv=[
                "--claim-id",
                "C3",
                "--statement",
                "DuckDB supports a single writer with multiple concurrent readers",
                "--source-id",
                "S3",
                "--quote",
                POSTHOG_QUOTE,
                "--entity",
                "DuckDB",
                "--field",
                "concurrency model",
                "--value",
                "single writer only",
                "--confidence",
                "MEDIUM",
                "--sub-question",
                "Q2",
            ],
            pick="claim_id",
            pick_label="Claim id",
            pick_label_tr="İddia no",
        ),
        # ── ch4: contradiction ─────────────────────────────────────────────
        S(
            "Stop: the notebook caught the contradiction itself",
            "Dur: defter çelişkiyi kendi yakaladı",
            "Just call the status command — no extra code anywhere. Seeing two "
            "different values for the same entity (DuckDB) and the same field "
            "(concurrency model), the notebook drops them into the "
            "'contradictions' list. This is the antidote to 'is the AI making "
            "things up?': the clash is not hidden — it sits at the top of the "
            "table, shouting.",
            "Sadece 'durum' komutunu çağır — ortada ekstra kod yok. Aynı varlık "
            "(DuckDB) ve aynı alan (concurrency model) için iki farklı değer "
            "görünce defter onları 'çelişkiler' listesine düşürür. 'AI "
            "uyduruyor mu?' korkusunun panzehiri tam bu: çatışma saklanmaz — "
            "tablonun en üstünde oturur, bağırır.",
            "contradictions: 1 — C2 'multiple writes' vs C3 'single writer'",
            "çelişkiler: 1 — C2 'çoklu yazma' karşı C3 'tek yazıcı'",
            chapter=4,
            command="research-status",
            argv=[],
            pick="contradictions.0.claim_ids.0",
            pick_label="Contradicting claim",
            pick_label_tr="Çelişen iddia",
        ),
        S(
            "Settle it: winner C2, reason on record",
            "Çelişkiyi çöz: kazanan C2, nedeni yazılı",
            "Settling a contradiction requires a written reason — not a vibe. "
            "The rule here is plain: for a question about DuckDB itself, "
            "DuckDB's official documentation (S2) outranks a blog (S3). The "
            "blog had conflated 'a single writer' with 'a single writer "
            "PROCESS'. The decision is now in the notebook, together with its "
            "justification.",
            "Çelişki çözerken sebep de yazılır — 'hissettim' değil. Buradaki "
            "kural yalın: konu DuckDB'nin kendisiyse, DuckDB'nin resmi "
            "dokümanı (S2) blogdan (S3) güçlüdür. Blog 'tek yazıcı' ile 'tek "
            "yazıcı SÜREÇ' kavramlarını birbirine karıştırmış. Karar artık "
            "gerekçesiyle birlikte defterde.",
            "status: OK — resolution recorded (winner: C2)",
            "status: OK — çözüm kaydedildi (kazanan: C2)",
            chapter=4,
            command="research-resolve",
            argv=[
                "--entity",
                "DuckDB",
                "--field",
                "concurrency model",
                "--winner-claim",
                "C2",
                "--reason",
                "Primary DuckDB documentation (S2) is authoritative; the PostHog article (S3) simplifies: DuckDB allows multiple writer threads within one process, but only one writer process.",
            ],
        ),
        S(
            "Write what you couldn't find: saying 'unknown'",
            "Bulamadığını da yaz: 'bilinmiyor' demek",
            "The hardest part of honest research: writing 'not found' for "
            "what's missing. 'No public benchmark compares crash recovery "
            "times between DuckDB and SQLite' — this gap goes on the record "
            "too. The final report will say: known up to here, unknown beyond. "
            "Inventing is not an option.",
            "Dürüst araştırmanın en zor kısmı: bulunamayan şeyi 'bulamadım' "
            "diye yazmak. 'Kaza sonrası toparlanma sürelerini karşılaştıran "
            "kamu kaynağı yok' — bu bilgi eksikliği de kayda geçer. Raporun "
            "sonunda 'buraya kadar bildik, buradan sonrası bilinmiyor' "
            "denecek. Uydurmak seçenek değil.",
            "status: OK — gap recorded",
            "status: OK — bilinmeyen kaydedildi",
            chapter=4,
            command="research-add-gap",
            argv=[
                "--description",
                "No public benchmark compares crash recovery times between DuckDB and SQLite",
                "--entity",
                "DuckDB",
                "--field",
                "crash recovery",
            ],
        ),
        # ── ch5: report ────────────────────────────────────────────────────
        S(
            "Grade the sources (0–5)",
            "Kaynaklara karne ver (0–5)",
            "Every source card gets scored: primary or secondary, fresh or "
            "stale, quoted or not. The official docs (S1, S2) come out high; "
            "the blog (S3) comes out lower. The AI writing the final report "
            "can now ask, per sentence: 'how trustworthy is the source behind "
            "this?'",
            "Her kaynak kartı puanlanır: birincil mi ikincil mi, güncel mi "
            "değil mi, alıntısı var mı. Resmi dokümanlar (S1, S2) yüksek, blog "
            "(S3) düşük çıkar. Raporu yazan yapay zekâ artık cümle cümle "
            "sorabilir: 'bu cümlenin arkasındaki kaynak ne kadar güvenilir?'",
            "S1 and S2 score high, S3 lower (tier: SECONDARY)",
            "S1 ve S2 yüksek puan alır, S3 düşük (tür: SECONDARY)",
            chapter=5,
            command="research-score",
            argv=[],
            pick="low_quality",
            pick_label="Low-quality list",
            pick_label_tr="Zayıf kaynak listesi",
        ),
        S(
            "Build the comparison table",
            "Karşılaştırma tablosunu kur",
            "The claims get laid out in an entity × field table: rows DuckDB "
            "and SQLite, column 'concurrency model'. Every cell is either "
            "filled by a verified claim or honestly says n.a. (not answered). "
            "One glance shows the difference between the two engines — and "
            "what is still unknown.",
            "İddialar bir varlık × alan tablosuna dizilir: satırlarda DuckDB ve "
            "SQLite, sütunda 'concurrency model'. Her hücre ya doğrulanmış bir "
            "iddiayla dolar ya da dürüstçe 'n.a.' (cevaplanmadı) der. Tek "
            "bakışta iki motorun farkı — ve hâlâ bilinmeyen — görülür.",
            "verified cells: 2 · one cell was contested, now resolved",
            "doğrulanmış hücre: 2 · biri çelişkiliydi, çözüldü",
            chapter=5,
            command="wide-table",
            argv=[
                "--entity",
                "DuckDB",
                "--entity",
                "SQLite",
                "--field",
                "concurrency model",
            ],
        ),
        S(
            "Write the report to a file",
            "Raporu dosyaya yaz",
            "The whole notebook pours into a single markdown file: every claim "
            "with its quote and its S1/S2/S3 source cards, the resolution, the "
            "gaps. The file appears in the Files tab. What you are holding: a "
            "research report in which every sentence can be traced back to a "
            "source.",
            "Bütün defter tek bir markdown dosyasına dökülür: her iddia, "
            "alıntısıyla ve S1/S2/S3 kaynak kartlarıyla, çözüm kararı, "
            "bilinmeyenler. Dosya Dosyalar sekmesinde belirir. Elinde tuttuğun "
            "şey: her cümlesi bir kaynağa geri izlenebilen araştırma raporu.",
            "artifacts/duckdb-vs-sqlite-evidence.md written",
            "artifacts/duckdb-vs-sqlite-evidence.md yazıldı",
            chapter=5,
            command="research-pack",
            argv=["--output", "artifacts/duckdb-vs-sqlite-evidence.md"],
            deliverable=True,
        ),
        S(
            "Final audit: is the report clean?",
            "Son denetim: rapor temiz mi?",
            "The closing audit checks the notebook: does every claim have a "
            "source, are the quotes non-empty, did any contradiction survive "
            "unresolved? A PASS means the report is closed. This step writes "
            "nothing — it only sets rules and checks them. Trust, but verify.",
            "Kapanış denetimi defteri kontrol eder: her iddianın kaynağı var "
            "mı, alıntılar dolu mu, çözülmeden kalan çelişki var mı? PASS "
            "alırsa rapor 'kapandı' demektir. Bu adım hiçbir şey yazmaz — "
            "sadece kural koyar ve kontrol eder. Güven, ama doğrula.",
            "status: PASS — blocking_count: 0",
            "status: PASS — blocking_count: 0",
            chapter=5,
            command="audit-report",
            argv=[],
            expect_status="PASS",
        ),
    ],
}


DECIDE = {
    "id": "decide",
    "icon": "scale",
    "title": "The decision council: score it, record it, then hear the devil's advocate",
    "title_tr": "Karar meclisi: puanla, yaz, sonra şeytanın avukatını dinle",
    "subtitle": (
        "Torn between two options — a shared workspace or isolated sandboxes? "
        "Turn the decision into a weighted scorecard, write the numbered ADR, "
        "and at the very end sit through the devil's advocate round: the "
        "strongest argument against your own choice."
    ),
    "subtitle_tr": (
        "İki seçenek arasında kaldın: ortak çalışma alanı mı, izole kum havuzu "
        "mu? Kararı tartılı bir puan tablosuna dök, numaralı ADR'ye yaz ve en "
        "sonunda şeytanın avukatı turuna katlan: seçiminin EN GÜÇLÜ karşı "
        "argümanı."
    ),
    "outcome": "a numbered ADR decision record",
    "outcome_tr": "numaralı ADR karar dosyası",
    "time_min": 2,
    "story_intro": (
        "Our brains cheat at decisions: they pick the first appealing idea, "
        "then invent the reason afterwards. This story hands the cheat over to "
        "the police. First the question is written down precisely (including "
        "what we will NOT do). Then every option is scored on weighted "
        "criteria, and the arithmetic — not the mood — produces the "
        "recommendation. Finally comes the part most people skip: the devil's "
        "advocate round, where the tool deliberately refuses to finish your "
        "decision record until the strongest counter-argument and the "
        "failure-scenarios have been written. 3 real commands + 1 reading step."
    ),
    "story_intro_tr": (
        "Beynimiz kararlarda hile yapar: önce gözüne kestirdiğini seçer, gerekçeyi "
        "sonradan uydurur. Bu hikâye o hileyi zabıta teslim eder. Önce soru "
        "kesin olarak yazılır (ve NELER YAPMAYACAĞIMIZ da). Sonra her seçenek "
        "tartılı kriterlerle puanlanır; öneriyi aritmetik çıkarır, keyif değil. "
        "En sonda herkesin atladığı kısım gelir: şeytanın avukatı turu — araç, "
        "en güçlü karşı argüman ve başarısızlık senaryoları yazılmadan karar "
        "dosyanızı bitirmeyi bilerek reddeder. 3 gerçek komut + 1 okuma adımı."
    ),
    "chapters": [
        {"title": "Frame the decision", "title_tr": "Kararı çerçevele"},
        {"title": "The scorecard", "title_tr": "Puan tablosu"},
        {"title": "Write the record", "title_tr": "Kararı yaz"},
        {"title": "Devil's advocate", "title_tr": "Şeytanın avukatı"},
    ],
    "steps": [
        S(
            "Write the question honestly",
            "Soruyu dürüstçe yaz",
            "First rule of the decision council: no scoring before the question "
            "is written precisely. The question: 'should console commands run "
            "on a shared workspace or isolated sandboxes?' Context and "
            "constraints go in — plus a NOT-DOING list ('no multi-user auth'). "
            "The scope fences go up first, so the decision can't bloat.",
            "Karar meclisinin ilk kuralı: soru kesin yazılmadan puanlama yok. "
            "Soru: 'konsol komutları ortak çalışma alanına mı, izole kum "
            "havuzuna mı çalışsın?' Bağlam ve zorunluluklar yazılır — bir de "
            "YAPMAYACAKLAR listesi ('çok kullanıcılı yetkilendirme yok'). Sınır "
            "direkleri en başta dikilir ki karar şişlemesin.",
            "mode: architecture — intake saved",
            "mode: architecture — giriş kaydedildi",
            chapter=1,
            command="advise-intake",
            argv=[
                "--question",
                "Should the test console run commands against a shared demo workspace or isolated sandboxes per run?",
                "--context",
                "The web console executes real workbench commands and must keep ledger state inspectable",
                "--constraint",
                "Keep the Workspace tab able to show live ledgers",
                "--non-goal",
                "Multi-user isolation and auth",
                "--mode",
                "architecture",
            ],
            pick="intake.mode",
            pick_label="Mode",
            pick_label_tr="Mod",
        ),
        S(
            "Compute the scorecard — the math recommends",
            "Puan tablosunu hesapla — öneriyi matematik verir",
            "The ready-made matrix says: inspectability counts 3×, effort 2×, "
            "reversibility 1×. Each option scores 0–10 per criterion; multiply, "
            "sum, rank. One criterion carries a floor ('inspectability at "
            "least 5') — options falling below it are DISQUALIFIED outright. "
            "The recommendation comes out of the table, not the mood. Don't "
            "like it? Change the matrix — the recommendation changes with it.",
            "Hazır gelen matris der ki: incelenebilirlik 3 kat, emek 2 kat, "
            "geri dönüş kolaylığı 1 kat önemli. Her seçenek her kriterden 0–10 "
            "alır; çarp, topla, sırala. Bir kriterin tabanı da var "
            "('incelenebilirlik en az 5') — altında kalan seçenek doğrudan "
            "ELENİR. Öneri tablodan çıkar, keyiften değil. Beğenmedin mi? "
            "Matrisi değiştir — öneri de seninle değişir.",
            "recommended_option: shared workspace",
            "recommended_option: shared workspace (ortak alan)",
            chapter=2,
            command="decision-score",
            argv=[
                "--spec-file",
                "decision-matrix.json",
                "--output",
                "decision-result.json",
            ],
            pick="recommended_option",
            pick_label="Recommended",
            pick_label_tr="Önerilen",
        ),
        S(
            "Write the decision into a numbered file: the ADR",
            "Kararı numaralı dosyaya yaz: ADR",
            "The decision is now a numbered file under docs/adr/: dated, "
            "owned, with the score table filled in from the result. An ADR's "
            "job is to leave a message for the future: 'what did we knowingly "
            "choose, and why?' But look — the file still has EMPTY sections, "
            "and the tool fills them on purpose not. Which ones? Next chapter.",
            "Karar artık docs/adr/ altında numaralı bir dosya: tarihli, "
            "sahipli, sonuç dosyasından doldurulmuş puan tablosu dolu. ADR'nin "
            "işi geleceğe mesaj bırakmaktır: 'neyi bilerek seçtik ve neden?' "
            "Ama bak — dosyada hâlâ BOŞ bölümler var ve araç onları bilerek "
            "doldurmuyor. Hangi bölümler? Bir sonraki bölüm.",
            "docs/adr/00NN-…md written — numbered and dated",
            "docs/adr/00NN-…md yazıldı — numaralı ve tarihli",
            chapter=3,
            id="adr1",
            command="adr-new",
            argv=[
                "--title",
                "Run the test console against a shared demo workspace",
                "--decision-result",
                "decision-result.json",
                "--dir",
                "docs/adr",
                "--owner",
                "console-team",
            ],
            pick="adr",
            pick_label="File",
            pick_label_tr="Dosya",
            deliverable=True,
        ),
        S(
            "Devil's advocate: 'what if I'm wrong?'",
            "Şeytanın avukatı: 'ya yanlışsam?'",
            None,
            None,
            None,
            None,
            chapter=4,
            kind="explain",
            body=(
                "The ADR file has two sections the tool refuses to fill — by "
                "design, not by omission:\n\n"
                "1) **Steelman Counter-Argument** — the STRONGEST argument "
                "against your choice. Not a strawman; steel. Write it as if "
                "your smartest opponent drafted it.\n\n"
                "2) **Pre-mortem** — assume it is 12 months later and the "
                "decision FAILED. Write the 2 most likely causes, each with "
                "its early warning signal and its mitigation.\n\n"
                "The tool leaves these empty on purpose: they are *thinking* "
                "work, not *bookkeeping* work. Your AI can fill them in — but "
                "honestly, or adr-check will keep failing."
            ),
            body_tr=(
                "ADR dosyasında aracın doldurmayı REDDETTİĞİ iki bölüm var — "
                "bu bir kusur değil, bilinçli bir tercih:\n\n"
                "1) **Steelman Counter-Argument (Karşı Argüman)** — seçtiğin "
                "karara yönelik EN GÜÇLÜ itiraz. Hasır kaşık değil; çelik. "
                "En zeki düşmanın yazmış gibi yaz.\n\n"
                "2) **Pre-mortem (Önceden Otopsi)** — 12 ay geçmiş ve karar "
                "BAŞARISIZ olmuş diye varsay. En olası 2 nedeni, her birinin "
                "erken uyarı sinyalini ve panzehirini yaz.\n\n"
                "Araç bu bölümleri bilerek boş bırakır: bunlar *düşünme* işi, "
                "*kayıt* işi değil. Yapay zekân doldurabilir — ama dürüstçe, "
                "yoksa adr-check geçmeye devam etmez."
            ),
            example=(
                "**A filled example** — Steelman: 'A shared workspace can "
                "corrupt ledgers when two tabs run at once; isolation would "
                "zero that risk.' · Pre-mortem: 'A year later it failed "
                "because concurrent demo runs corrupted the ledger state. "
                "Early signal: two runs starting in the same second. "
                "Mitigation: queue runs behind a lock.'"
            ),
            example_tr=(
                "**Doldurulmuş örnek** — Steelman: 'Ortak alanda aynı anda iki "
                "sekme çalışınca defterler bozulabilir; izolasyon bu riski "
                "sıfırlardı.' · Pre-mortem: 'Bir yıl sonra başarısız oldu, "
                "çünkü eşzamanlı demo koşuları defter durumunu bozdu. Erken "
                "sinyal: aynı saniyede başlayan iki koşu. Panzehir: koşuları "
                "kilit arkasında sıraya al.'"
            ),
        ),
        S(
            "Audit it: it must say FAIL, on purpose",
            "Denetle: bilerek 'başarısız' demeli",
            "adr-check audits the file and right now says FAIL — and that is "
            "the CORRECT behavior! The 'unfilled placeholders' list tells you "
            "exactly what is still owed: the devil's advocate sections remain "
            "empty. In real life you (or your AI) fill them in and re-run this "
            "command until it says PASS. The tool leans on you: no 'I titled "
            "it and moved on'.",
            "adr-check dosyayı denetler ve şu anda FAIL der — ve bu DOĞRU "
            "davranıştır! 'Doldurulmamış yer tutucular' listesi senden hâlâ "
            "beklenen şeyi tek tek söyler: şeytanın avukatı bölümleri boş. "
            "Gerçek hayatta sen (veya yapay zekân) doldurur ve PASS diyene "
            "kadar bu komutu tekrar çalıştırırsın. Araç sana yaslanır: "
            "'başlığını attım, geçtim' yok.",
            "status: FAIL — unfilled placeholders: STEELMAN_COUNTERARGUMENT, …",
            "status: FAIL — doldurulmamış: STEELMAN_COUNTERARGUMENT, …",
            chapter=4,
            command="adr-check",
            argv=["--file", "{{adr1.adr}}"],
            expect_status="FAIL",
            expect_exit=2,
            pick="problems.0",
            pick_label="First problem",
            pick_label_tr="İlk sorun",
        ),
    ],
}


def ship_and_debug_flows():
    """Keep the validated command sequences of ship/debug; rewrite the story."""
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    old_by_id = {f["id"]: f for f in old.get("flows", [])}

    ship_argv = [s["argv"] for s in old_by_id["ship"]["steps"]]
    debug_argv = [s["argv"] for s in old_by_id["debug"]["steps"]]
    ship_cmd = [s["command"] for s in old_by_id["ship"]["steps"]]
    debug_cmd = [s["command"] for s in old_by_id["debug"]["steps"]]

    ship = {
        "id": "ship",
        "icon": "rocket",
        "title": "Ship a change safely",
        "title_tr": "Bir değişikliği güvenle teslim et",
        "subtitle": (
            "'I did it' isn't enough — you must be able to say 'I PROVED it "
            "delivers what was asked.' The story: a CSV export button on the "
            "billing screen. Write the acceptance tests first, verify the "
            "delivery with runnable evidence, review your own code (and find "
            "a real bug), then hand the session over."
        ),
        "subtitle_tr": (
            "'Yaptım' demek yetmez — 'istediğim şeyi teslim ettiğimi KANITLADIM' "
            "demek gerekir. Hikâye: fatura ekranına bir CSV indirme düğmesi. "
            "Önce kabul testlerini yaz, teslimatı çalıştırılabilir kanıtla "
            "doğrula, kendi kodunu incelet (ve gerçek bir hata bul), sonra "
            "oturumu devret."
        ),
        "outcome": "verified delivery + review verdict + handoff pack",
        "outcome_tr": "doğrulanmış teslim + inceleme kararı + devir dosyası",
        "time_min": 3,
        "story_intro": (
            "Engineering teams don't trust 'done' — they trust evidence. This "
            "story walks a tiny feature through the whole quality gauntlet: "
            "spec (what does 'done' mean, exactly?), verification (run it and "
            "show me), review (a second pair of eyes finds a MAJOR bug), "
            "handoff (tomorrow someone else continues from the file). You play "
            "the engineer; the notebook keeps everyone honest."
        ),
        "story_intro_tr": (
            "Mühendis ekipler 'bitti'ye güvenmez — kanıta güvenir. Bu hikâye "
            "ufak bir özelliği kalite tünelinin içinden baştan sona geçirir: "
            "tarif ('bitti' tam olarak ne demek?), doğrulama (çalıştır ve "
            "göster), inceleme (ikinci bir göz bir MAJOR hata bulur), devir "
            "(yarın başka biri dosyadan devam eder). Mühendisin rolündesin; "
            "herkesi dürüst tutan şey defter."
        ),
        "chapters": [
            {"title": "Spell out the work", "title_tr": "İşi tarif et"},
            {"title": "Prove it", "title_tr": "Kanıtla"},
            {"title": "Put it through review", "title_tr": "İncelemeden geçir"},
            {"title": "Hand it over", "title_tr": "Devret"},
        ],
        "steps": [
            S(
                "Spell out the work: goal, story, non-goals",
                "İşi tarif et: hedef, hikâye, yapmayacaklar",
                "Before any code, the work gets described: one goal sentence, "
                "user stories (US1…), and — most important — the explicit "
                "NOT-doing list. 'Finance can export the invoices as CSV': "
                "sharp and measurable. NOT doing: PDF export, e-mailing. Work "
                "that starts without fences never ends.",
                "Koddan önce iş tarif edilir: tek hedef cümle, kullanıcı "
                "hikâyeleri (US1…) ve en önemlisi YAPMAYACAKLAR listesi. "
                "'Finans faturaları CSV olarak indirebilsin': keskin ve "
                "ölçülebilir. Yapılmayacak: PDF çıktısı, e-posta atma. Sınırsız "
                "başlanan iş asla bitmez.",
                "status: OK — spec ledger opened with story US1",
                "status: OK — tarif defteri US1 hikâyesiyle açıldı",
                chapter=1,
                command=ship_cmd[0],
                argv=ship_argv[0],
            ),
            S(
                "Write the acceptance test: Given / When / Then",
                "Kabul şartını yaz: Verildiğinde / Olduğunda / O zaman",
                "'When is US1 done?' gets a three-line answer: GIVEN the "
                "billing screen is showing one month of invoices, WHEN the "
                "user clicks Export CSV, THEN the file downloads and has 12 "
                "columns. These lines are the bricks every later task must "
                "verify — no task, no 'done'.",
                "'US1 ne zaman tamam sayılır?' sorusunun üç satırlık cevabı: "
                "VERİLDİĞİNDE fatura ekranı bir aylık faturaları gösteriyor, "
                "OLDUĞUNDA kullanıcı CSV'ye Dışa Aktar'a basıyor, O ZAMAN "
                "dosya iner ve 12 kolon vardır. Bu satırlar, ileride her "
                "görevin doğrulamak zorunda olduğu tuğlalar — görev yoksa "
                "'bitti' de yok.",
                "AC1 recorded — linked to story US1",
                "AC1 kaydedildi — US1 hikâyesine bağlandı",
                chapter=1,
                command=ship_cmd[1],
                argv=ship_argv[1],
            ),
            S(
                "Write the task and tie it to the criterion it verifies",
                "Görevi yaz ve doğrulayacağı şarta bağla",
                "Every task must claim 'I verify at least one acceptance "
                "criterion' (--verifies AC1). The task: wire the export button "
                "to the CSV endpoint and add a regression test. Why forced? A "
                "task that verifies nothing is decoration — it gets deleted.",
                "Her görev 'en az bir kabul şartını doğruluyorum' demek "
                "zorundadır (--verifies AC1). Görev: dışa aktarma düğmesini "
                "CSV uç noktasına bağla ve bir regresyon testi ekle. Neden "
                "zorunlu? Hiçbir şartı doğrulamayan görev süstür — silinir.",
                "task T1 — verifies: AC1",
                "görev T1 — doğrular: AC1",
                chapter=1,
                command=ship_cmd[2],
                argv=ship_argv[2],
            ),
            S(
                "Start the delivery report from a template",
                "Teslim raporunu şablondan başlat",
                "The delivery's 'evidence file' starts from a template: what "
                "was delivered, how it was observed, which commands prove it. "
                "No pre-written content — structure. The empty spots show up "
                "as {{PLACEHOLDER}}s, on purpose: a human (or the AI) must "
                "fill them in.",
                "Teslimatın 'kanıt dosyası' şablondan başlar: ne teslim "
                "edildi, nasıl gözlemlendi, hangi komutlar kanıtlıyor. Önceden "
                "yazılmış içerik yok — yapı var. Boş yerler bilerek "
                "{{YER_TUTUCU}} olarak görünür: insan (veya yapay zekâ) "
                "dolduracak.",
                "artifacts/billing-export-report.md created",
                "artifacts/billing-export-report.md oluştu",
                chapter=2,
                command=ship_cmd[3],
                argv=ship_argv[3],
            ),
            S(
                "Audit the spec: does every criterion have a task?",
                "Tarifi denetle: her şartın görevi var mı?",
                "The spec audits itself: any uncovered criteria? dependency "
                "cycles? missing fields? If none, PASS. This is not a spelling "
                "check — it's a process check: the spec can't cheat its own "
                "rules.",
                "Tarif kendi kendini denetler: kapsanmamış şart var mı, "
                "bağımlılık döngüsü var mı, eksik alan var mı? Yoksa PASS. Bu "
                "yazım denetimi değil — süreç denetimidir: tarif kendi "
                "kurallarını atlatamaz.",
                "status: PASS — criteria coverage complete",
                "status: PASS — şart kapsamı tamam",
                chapter=2,
                command=ship_cmd[4],
                argv=ship_argv[4],
            ),
            S(
                "Verify the delivery observably",
                "Teslimatı gözle görülür şekilde doğrula",
                "'It works' is not evidence; a RUNNABLE check is. "
                "verify-delivery executes a command (--check 'L2:test …') and "
                "searches the output for the expected sentence. The output "
                "contains 'passed' → the evidence is in. Otherwise the "
                "delivery stays 'unverified' — and everyone can see that.",
                "'Çalışıyor' kanıt değildir; ÇALIŞTIRILABİLİR kontrol kanıttır. "
                "verify-delivery bir komut çalıştırır (--check 'L2:test …') ve "
                "çıktının içinde beklenen cümleyi arar. Çıktıda 'passed' var "
                "→ kanıt sağlandı. Yoksa teslim 'doğrulanmadı' olarak kalır — "
                "ve bunu herkes görebilir.",
                "status: PASS — check output contained the expected sentence",
                "status: PASS — kontrol çıktısı beklenen cümleyi içerdi",
                chapter=2,
                command=ship_cmd[5],
                argv=ship_argv[5],
            ),
            S(
                "Open a review on your own code",
                "Kendi kodunu incelemeye aç",
                "Even trusting your own code, you open a review: target file, "
                "focus 'correctness'. Review is the art of finding the bug "
                "before the user does. (--force is only there because the "
                "demo ledger has run before; you wouldn't need it fresh.)",
                "Koduna güvensek bile inceleme açarız: hedef dosya, odak "
                "'correctness' (doğruluk). İnceleme, hatayı kullanıcı "
                "bulmadan bulma sanatıdır. (--force yalnızca demo defteri daha "
                "önce koştuğu için var; temiz durumda gerekmez.)",
                "review ledger opened — target: src/billing/export.ts",
                "inceleme defteri açıldı — hedef: src/billing/export.ts",
                chapter=3,
                command=ship_cmd[6],
                argv=ship_argv[6],
            ),
            S(
                "Record the finding, with severity",
                "Bulgunu ciddiyetiyle kaydet",
                "The review found a flaw: the CSV fields are joined without "
                "escaping (line 42, MAJOR). Findings are recorded with file + "
                "line + severity + category — 'there's a bug somewhere' is not "
                "an accepted finding. MAJOR means: it can corrupt data.",
                "İncelemede bir kusur bulundu: CSV alanları kaçış karakteri "
                "olmadan birleştirilmiş (satır 42, MAJOR). Bulgunlar dosya + "
                "satır + ciddiyet + kategori ile kaydedilir — 'bir yerde hata "
                "var' cümlesi bulgun sayılmaz. MAJOR demek: veriyi bozabilir.",
                "finding recorded — MAJOR, correctness",
                "bulgun kaydedildi — MAJOR, doğruluk",
                chapter=3,
                command=ship_cmd[7],
                argv=ship_argv[7],
            ),
            S(
                "Verdict: APPROVE or BLOCK?",
                "Karar: APPROVE mi BLOCK mu?",
                "Findings are counted and the verdict follows mechanically "
                "from the severities: a MAJOR means the review BLOCKS. No "
                "'come on, don't exaggerate'. Fix the bug, open a new review.",
                "Bulgunlar sayılır ve karar ciddiyetlerden mekanik olarak "
                "çıkar: bir MAJOR varsa inceleme BLOCK verir. 'Aman canım, "
                "abartma' yok. Hatayı düzelt, yeni inceleme aç.",
                "verdict: BLOCK — 1 MAJOR finding",
                "karar: BLOCK — 1 MAJOR bulgu",
                chapter=3,
                command=ship_cmd[8],
                argv=ship_argv[8],
            ),
            S(
                "Prepare the handoff pack",
                "Devir dosyasını hazırla",
                "The session ends, but the work might not. handoff-pack "
                "compiles every ledger (spec, review, verification) into one "
                "handoff file: what remains open, which commands ran, which "
                "files are where. Whoever starts tomorrow never asks 'where is "
                "the context?' — it's in the file.",
                "Oturum bitiyor ama iş bitmiş olmayabilir. handoff-pack bütün "
                "defterleri (tarif, inceleme, doğrulama) tek bir devir "
                "dosyasında toplar: ne açık kaldı, hangi komutlar koştu, "
                "hangi dosya nerede. Yarın başlayan kişi 'context nerede?' "
                "diye sormaz — dosyada.",
                "HANDOFF file written — session-status: DONE",
                "HANDOFF dosyası yazıldı — oturum durumu: DONE",
                chapter=4,
                command=ship_cmd[9],
                argv=ship_argv[9],
                deliverable=True,
            ),
        ],
    }

    debug = {
        "id": "debug",
        "icon": "bug",
        "title": "Chase a bug to its root cause",
        "title_tr": "Bir hatayı kök nedenine kadar kovala",
        "subtitle": (
            "The program prints an empty list instead of an error. Detective "
            "rules apply: every guess goes on record, every guess yields a "
            "testable prediction, a failed prediction gets the guess stamped "
            "FALSIFIED. The root cause turns out to be one line of code."
        ),
        "subtitle_tr": (
            "Program hata basacağına boş liste basıyor. Dedektif kuralları "
            "geçerli: her tahmin kayda geçer, her tahmin sınanabilir bir "
            "öngörü üretir, tutmayan öngörü tahmini ÇÜRÜK damgalatır. Kök "
            "nedenin tek bir satır kod olduğu ortaya çıkar."
        ),
        "outcome": "a root-cause report",
        "outcome_tr": "kök neden raporu",
        "time_min": 2,
        "story_intro": (
            "Given 'abc' as the limit, the demo app prints [] instead of "
            "complaining. Why? We work like detectives: a guess ('maybe the "
            "argument never reaches the program') is only allowed on record, "
            "and only with a prediction ('then abc and 3 must behave "
            "identically'). The prediction fails → the guess is falsified. "
            "Two strikes and that path closes. What survives is the root "
            "cause — with its evidence chain."
        ),
        "story_intro_tr": (
            "Limit olarak 'abc' verilince demo uygulama şikâyet etmek yerine "
            "boş liste basıyor. Neden? Dedektif gibi çalışıyoruz: bir tahmin "
            "('galiba argüman programa hiç ulaşmıyor') yalnızca kayda "
            "geçerek yaşar ve ancak öngörüyle ('o zaman abc ile 3 aynı "
            "davranmalı') tutunur. Öngörü tutmaz → tahmin çürütülür. İki "
            "çürütme o yolu kapatır. Sağ kalan tek şey kök nedendir — kanıt "
            "zinciriyle birlikte."
        ),
        "chapters": [
            {"title": "Write the symptom", "title_tr": "Belirtiyi yaz"},
            {"title": "Guess and falsify", "title_tr": "Tahmin et ve çürüt"},
            {"title": "Root-cause report", "title_tr": "Kök neden raporu"},
        ],
        "steps": [
            S(
                "Write the symptom and the first suspect",
                "Belirtiyi ve ilk şüpheliyi yaz",
                "Debugging is done with recorded hypotheses, not with 'maybe's. "
                "Symptom: with a non-numeric limit the app prints an empty "
                "list instead of an error. First suspect (H1): 'the command "
                "line argument never reaches the program'. It's on record "
                "now — it will be tested, not forgotten.",
                "Hata ayıklama 'galiba'larla değil, kayıtlı hipotezlerle "
                "yapılır. Belirti: sayısal olmayan limit verilince uygulama "
                "hata yerine boş liste basıyor. İlk şüpheli (H1): 'komut "
                "satırı argümanı programa hiç ulaşmıyor'. Kayda geçti — artık "
                "unutulamaz, sınanacak.",
                "H1 recorded — status: OPEN",
                "H1 kaydedildi — durum: OPEN",
                chapter=1,
                command=debug_cmd[0],
                argv=debug_argv[0],
            ),
            S(
                "Read the file the suspect points to",
                "Şüphelinin gösterdiği dosyayı oku",
                "The inspection target is the code itself: "
                "demo-project/src/app.py. scope-read reads files strictly "
                "inside the project root — it cannot wander. What we're "
                "looking at: the parse_int function and its error handling.",
                "İnceleme hedefi kodun kendisi: demo-project/src/app.py. "
                "scope-read dosyaları yalnızca proje kökünün içinden okur — "
                "dışarı çıkamaz. Bakacağımız şey: parse_int fonksiyonu ve "
                "hata yakalama kısmı.",
                "app.py contents — line by line",
                "app.py içeriği — satır satır",
                chapter=2,
                command=debug_cmd[1],
                argv=debug_argv[1],
            ),
            S(
                "Sharpen H1: write a prediction",
                "H1'i keskinleştir: öngörü yaz",
                "The claim 'the argument never arrives' must become testable: "
                "'THEN abc and 3 must behave identically.' Without a written "
                "prediction a hypothesis is a toy; with one, its fate is "
                "sealed — it will be confirmed or falsified.",
                "'Argüman ulaşmıyor' iddiası sınanabilir hale gelmeli: 'O "
                "ZAMAN abc ile 3 birbirinden farklı davranamaz.' Yazılı "
                "öngörüsü olmayan hipotez oyuncaktır; olanın kaderi bellidir "
                "— doğrulanacak ya da çürütülecek.",
                "H1 updated — prediction added",
                "H1 güncellendi — öngörü eklendi",
                chapter=2,
                command=debug_cmd[2],
                argv=debug_argv[2],
            ),
            S(
                "Test and falsify: H1 falls",
                "Sına ve çürüt: H1 düştü",
                "The test: abc → prints [], 3 → prints the squares. The "
                "behaviors DIFFER — so the argument does arrive; H1 is "
                "falsified. Even the falsification is recorded with its "
                "evidence: 'running with abc prints [] while 3 prints squares "
                "— the argument reaches the program.' One more path closed; "
                "closed paths lead closer to the root cause.",
                "Sınama: abc → [] basıyor, 3 → kareleri basıyor. Davranışlar "
                "FARKLI — yani argüman ulaşıyor; H1 çürüdü. Çürüme bile kanıtla "
                "kayda geçer: 'abc ile [] basıyor, 3 ile kareler — argüman "
                "programa ulaşıyor.' Bir yol daha kapandı; kapanan yollar kök "
                "nedene yaklaştırır.",
                "H1: FALSIFIED — recorded with evidence",
                "H1: ÇÜRÜTÜLDÜ — kanıtla kaydedildi",
                chapter=2,
                command=debug_cmd[3],
                argv=debug_argv[3],
            ),
            S(
                "Second suspect: the line that swallows the error",
                "İkinci şüpheli: hatayı yutan satır",
                "New hypothesis H2: 'parse_int catches the ValueError and "
                "returns 0 — and range(0) is an empty list.' Prediction: 'the "
                "error from int(abc) silently turns into 0 inside app.py.' We "
                "have already read the file; the try/except sits right there.",
                "Yeni hipotez H2: 'parse_int ValueError'u yakalayıp 0 "
                "döndürüyor — range(0) da boş liste demek.' Öngörü: "
                "'int(abc)'nin hatası app.py içinde sessizce 0'a dönüşüyor.' "
                "Dosyayı zaten okuduk; try/except tam orada duruyor.",
                "H2 recorded — with its prediction",
                "H2 kaydedildi — öngörüsüyle birlikte",
                chapter=2,
                command=debug_cmd[4],
                argv=debug_argv[4],
            ),
            S(
                "H2 confirmed: root cause found",
                "H2 doğrulandı: kök neden bulundu",
                "The evidence: int('abc') raises ValueError; app.py catches "
                "it and silently returns 0; range(0) → empty list. The chain "
                "closes: input → swallowed error → 0 → empty output. H2 is "
                "CONFIRMED. The root cause is no longer a feeling — it's a "
                "sentence with evidence.",
                "Kanıt: int('abc') ValueError fırlatır; app.py yakalar ve "
                "sessizce 0 döndürür; range(0) → boş liste. Zincir kapanır: "
                "girdi → yutulan hata → 0 → boş çıktı. H2 DOĞRULANDI. Kök "
                "neden artık bir his değil — kanıtlı bir cümle.",
                "H2: CONFIRMED — evidence chain complete",
                "H2: DOĞRULANDI — kanıt zinciri tamam",
                chapter=2,
                command=debug_cmd[5],
                argv=debug_argv[5],
            ),
            S(
                "Write the root-cause report",
                "Kök neden raporunu yaz",
                "The report carries three things: the root cause (with its "
                "evidence), the fix that was applied ('parse_int now re-raises "
                "the ValueError instead of returning 0'), and the open risk "
                "('not exercised with negative or very long inputs'). "
                "Debugging ends; honesty doesn't — the unknowns go in too.",
                "Raporda üç şey taşınır: kök neden (kanıtıyla), uygulanan "
                "düzeltme ('parse_int artık ValueError'u 0 döndürmek yerine "
                "yeniden fırlatıyor') ve açık risk ('negatif veya çok uzun "
                "girdiler denenmedi'). Hata ayıklama biter; dürüstlük bitmez — "
                "bilinmeyenler de yazılır.",
                "root-cause report rendered",
                "kök neden raporu oluşturuldu",
                chapter=3,
                command=debug_cmd[6],
                argv=debug_argv[6],
                deliverable=True,
            ),
        ],
    }
    return [ship, debug]


def main() -> None:
    flows = [RESEARCH, DECIDE, *ship_and_debug_flows()]
    data = {"flows": flows}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # sanity checks
    n_steps = sum(len(f["steps"]) for f in flows)
    for f in flows:
        chs = f.get("chapters", [])
        for s in f["steps"]:
            c = s.get("chapter")
            if chs and (c is None or not (1 <= c <= len(chs))):
                raise SystemExit(f"{f['id']}/{s['title']}: bad chapter {c}")
            if s.get("kind") == "firecrawl" and not s.get("action"):
                raise SystemExit(f"{f['id']}/{s['title']}: firecrawl step missing action")
            if s.get("kind", "workbench") == "workbench" and not s.get("command"):
                raise SystemExit(f"{f['id']}/{s['title']}: workbench step missing command")
    print(f"wrote {OUT} — {len(flows)} flows, {n_steps} steps")


if __name__ == "__main__":
    main()
