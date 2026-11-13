# Real-World Usage Scenarios (`human-authorship`)

These five scenarios show how writers, developers, journalists, researchers, and legal/executive authors use `human-authorship` in practice. In every scenario, the agent enforces **Rule #0 (Zero Ghostwriting)**: it will challenge weak logic, build stripped-down structural skeletons, and run deterministic rhythm checks, **but it will never write a single paragraph of ready prose for you**.

---

## Scenario 1 (Flagship): AI Dependency Detox: Rebuilding Critical Thinking & Structure

### When You Need This
You notice a pattern: whenever you need to write a tough essay, technical post, newsletter, or opinion piece, you instinctively open an LLM and ask for "a first draft I can edit." Months later, your outlining feels rusty, your sentences converge into predictable 16-word blocks, and a blank page feels intimidating without autocomplete.

### How `human-authorship` Breaks the Habit
Instead of abandoning AI completely, you flip its role from **ghostwriter** to **sparring partner**.

1. **You dump raw, unpolished thoughts:**
   > **User:** "I want to write about why senior engineers shouldn't let AI write all their RFCs. Whenever AI drafts our design docs, everyone agrees too fast because the prose sounds smooth, then bugs show up in production. I'm tired today, can you write a punchy two-paragraph intro to get me started?"

2. **Agent blocks the shortcut and fires Socratic friction:**
   > **Foquinha (`human-authorship`):** Refused: zero ghostwriting. Smooth prose hides shallow decisions; let's sharpen your own argument first.
   >
   > **Answer 3 checks before drafting:**
   > 1. **Falsification:** Name one RFC drafted with AI that still caught a real architectural flaw. What made it work?
   > 2. **Concrete Scene (5s):** Recall one actual production bug from a "smooth" AI RFC. Which exact assumption or line item did reviewers skim past?
   > 3. **Cut Test:** If you had only 12 words in Caveman style to state your thesis, what survives?

3. **You answer from real memory -> Agent emits a Caveman Scaffold (`<= 10 words` per line):**
   > **User:** "Last quarter our billing retry RFC passed review in 10 minutes because ChatGPT wrote clean bullet points. Nobody noticed idempotency keys expired after 24h while webhook retries ran for 72h. My 12-word thesis: Smooth AI prose makes reviewers skim past fatal edge cases."
   >
   > **Foquinha (`human-authorship`):**
   > - `Opening scene:` [10-minute RFC sign-off, 3 LGTMs, zero edge-case questions]
   > - `Hidden defect:` [24h key TTL] vs [72h webhook retry window]
   > - `Core mechanism:` [polished LLM syntax] -> [false consensus / skipped skepticism]
   > - `Counterpoint:` [when AI formatting helps: boilerplate tables, NOT failure modes]
   > - `Concrete close:` [rule for next RFC: author writes failure scenarios manually first]

4. **You close the chat, write in your own cadence, then run the Voice Gate:**
   ```bash
   python scripts/audit_human_voice.py rfc-brain-rot-post.md
   ```
   If your draft still sounds like an LLM metronome (`burstiness_stdev < 6.0` or `short_sentences_le8 == 0`), the script tells you **where** cadence flattened so *you* inject a sharp 4-word line.

---

## Scenario 2: Investigative Journalism & Press Prize Compliance (PT-BR / Cláusula 4.3.1)

### When You Need This
You are reporting an investigative story for outlets or prizes with strict human-authorship clauses (for example, Cláusula 4.3.1 do Prêmio MOL) where synthetic LLM rhythms or generic transitions disqualify a submission.

### Workflow in Action
- **User dumps field notes:** *"Tenho extratos do portal da transparência mostrando corte de R$ 15 mil na oficina de cultura em dez/2025, entrevista com a coordenadora Ana e silêncio da secretaria após dois e-mails."*
- **Agent applies Journalism Protocol ([references/socratic-protocols.md](../references/socratic-protocols.md)):**
  1. *Qual tela ou PDF oficial você conferiu diretamente antes de cravar R$ 15 mil?*
  2. *Onde a coordenadora Ana toma uma ação concreta na história, em vez de aparecer só como vítima passiva?*
  3. *Qual prazo formal e canal você deu à secretaria para o contraditório?*
- **Agent returns a 4-block Caveman Scaffold:**
  - `Cena abertura:` [sala fechada, cadeiras empilhadas, 18h, aviso na porta]
  - `Conflito central:` [empenho zerado em dez/25] vs [promessa oficial de manutenção]
  - `Contraponto obrigatorio:` [2 e-mails sem resposta (datas) + nota posterior se houver]
  - `Fecho empirico:` [alunos remanejados sem data de retorno; zero moralismo]
- **Post-draft audit:** Reporter writes the piece from memory and runs `audit_human_voice.py`, catching two accidental `"além disso"` connectors and three em-dashes before filing.

---

## Scenario 3: Academic Papers & Thesis Defense

### When You Need This
You have 40 open PDFs, three theoretical frameworks, and a paralyzing blinking cursor. You do not want an AI hallucinating citations or writing generic literature-review padding.

### Workflow in Action
- **Agent applies Academic Protocol ([references/socratic-protocols.md](../references/socratic-protocols.md)):**
  1. *In 12 Caveman words, what is your contribution that none of the cited authors formulated the same way?*
  2. *Which author in your bibliography directly contradicts your core premise, and what is the strongest version (steelman) of their argument?*
  3. *You stacked three abstract concepts in a row. Which real dataset, case, or empirical observation tests whether they hold up?*
- **Result:** You leave the session with a falsifiable outline and write the prose in your own academic register, passing the deterministic voice gate without robotic transitions like `"moreover"` or `"in conclusion"`.

---

## Scenario 4: Legal Briefs & Executive Memos (8-Second Mobile Test)

### When You Need This
You drafted a memo or judicial briefing that feels padded with hollow qualifiers (*"strategic impact"*, *"grave risk"*, *"essential measure"*). Decision-makers reading on a phone will bounce in 8 seconds.

### Workflow in Action
- **Agent applies Executive Protocol ([references/socratic-protocols.md](../references/socratic-protocols.md)):**
  1. *If the reader spends only 8 seconds on a phone screen, which number, deadline, or legal risk forces action today?*
  2. *List every qualifying adjective ("grave", "strategic", "urgent") and replace it with a measurable anchor (`R$`, statute article, percentage, or cutoff date).*
- **Result:** Bloated paragraphs collapse into direct, verifiable assertions written by counsel or the executive.

---

## Scenario 5: Standalone Pre-Publish CLI Gate (No Agent Required)

### When You Need This
You write completely offline in Obsidian, Vim, or VS Code and just want an honest, zero-API, zero-cloud metric gate before hitting publish.

### Run in Terminal
```bash
# Human-readable report
python scripts/audit_human_voice.py path/to/draft.md

# Machine-readable JSON (for editor tasks, git pre-commit, or CI)
python scripts/audit_human_voice.py path/to/draft.md --json
```

### Reading the JSON Output
| Field | Target | Meaning |
| :--- | :--- | :--- |
| `verdict` | `PASS_HUMAN_RHYTHM` | Passes only if `authorship_gate_score >= 80` and `warnings` is empty |
| `authorship_gate_score` | `80..100` | Starts at `100`, deducts deterministically for slop, dashes, watermarks, flat cadence |
| `burstiness_stdev` | `>= 6.0` (when `>= 5` sentences) | Word-count standard deviation across sentences; low values signal uniform AI rhythm |
| `short_sentences_le8` | `>= 1` (when `>= 5` sentences) | Ensures abrupt human pacing instead of endless medium-length clauses |
| `em_en_dash_count` | `0` | Flags `U+2014` (`—`) and `U+2013` (`–`) |
| `zero_width_count` | `0` | Detects hidden mid-text `U+200B..U+200D` and `U+FEFF` watermarks (ignoring leading UTF-8 BOM) |
| `slop_hits` | `[]` | Lists exact PT-BR (16 patterns) and EN (10 patterns) synthetic clichés found |
