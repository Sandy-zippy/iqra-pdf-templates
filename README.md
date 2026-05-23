# IQRA QMS — PDF Templates

**23 HTML+CSS templates** used by **n8n workflow `iqra-pdf-generation`** (Agent B) to render
official inspection PDFs for the EPE Jinnaram PEB project (J-126).

| Template | Form | Trigger | Output naming |
|---|---|---|---|
| `drawing-issue-001.html` | FRM-U2-001 Drawing Issue Register | Drawing Package Accepted | `NSPL-EPE-DWG-{seq:04d}.pdf` |
| `document-master-002.html` | FRM-U2-002 Document / Procedure Master List | Register update Accepted | `NSPL-EPE-DOC-{seq:04d}.pdf` |
| `calibration-003.html` | FRM-U2-003 Calibration Master Record | Calibration record Accepted | `NSPL-EPE-CAL-{seq:04d}.pdf` |
| `readiness-004.html` | FRM-U2-004 Readiness Closure Checklist | Readiness Package Accepted | `NSPL-EPE-RDY-{seq:04d}.pdf` |
| `imir-005.html` | FRM-U2-005 Incoming Material Inspection | IMIR Accepted / Accepted with condition | `NSPL-EPE-IMIR-{seq:04d}.pdf` |
| `traveller-006.html` | FRM-U2-006 Traveller / Material Traceability | Traveller Accepted | `NSPL-EPE-TRV-{seq:04d}.pdf` |
| `cutting-007a.html` | FRM-U2-007A Cutting Inspection | Cutting Accepted | `NSPL-EPE-CUT-{seq:04d}.pdf` |
| `drilling-parts-007b.html` | FRM-U2-007B Drilling (Assembly Parts) | Drilling Accepted | `NSPL-EPE-DRL-P-{seq:04d}.pdf` |
| `drilling-builtup-007c.html` | FRM-U2-007C Drilling (Built-up Members) | Drilling Accepted | `NSPL-EPE-DRL-M-{seq:04d}.pdf` |
| `fitup-saw-008a.html` | FRM-U2-008A Built-up Fit-up (SAW) | Fit-up Accepted | `NSPL-EPE-FIT-S-{seq:04d}.pdf` |
| `fitup-fcaw-008b.html` | FRM-U2-008B Attachment Fit-up (FCAW) | Fit-up Accepted | `NSPL-EPE-FIT-F-{seq:04d}.pdf` |
| `welding-saw-012a.html` | FRM-U2-012A SAW Welding Inspection | Welding Accepted | `NSPL-EPE-WLD-S-{seq:04d}.pdf` |
| `welding-fcaw-012b.html` | FRM-U2-012B FCAW Welding Inspection | Welding Accepted | `NSPL-EPE-WLD-F-{seq:04d}.pdf` |
| `pt-dpt-013.html` | FRM-U2-013 PT / DPT Inspection | DPT Accepted / Rejected | `NSPL-EPE-DPT-{seq:04d}.pdf` |
| `repair-014.html` | FRM-U2-014 Repair Closure | Repair Closure Accepted | `NSPL-EPE-RPR-{seq:04d}.pdf` |
| `final-release-015.html` | FRM-U2-015 Final Dimensional Release | Final Release Accepted | `NSPL-EPE-FNL-{seq:04d}.pdf` |
| `blasting-016a.html` | FRM-U2-016A Blasting / Surface Prep | Blasting Accepted | `NSPL-EPE-BLT-{seq:04d}.pdf` |
| `primer-016b.html` | FRM-U2-016B Primer Application | Primer Accepted | `NSPL-EPE-PRM-{seq:04d}.pdf` |
| `final-coat-016c.html` | FRM-U2-016C Final Coat Application | Final Coat Accepted | `NSPL-EPE-FCT-{seq:04d}.pdf` |
| `marking-packing-017a.html` | FRM-U2-017A Marking & Packing | Package Accepted | `NSPL-EPE-PKG-{seq:04d}.pdf` |
| `dispatch-017b.html` | FRM-U2-017B Dispatch Clearance | Dispatch Trip Accepted | `NSPL-EPE-DSP-{seq:04d}.pdf` |
| `dossier-index-018.html` | FRM-U2-018 Dossier Index (FRM-UI-022 style) | Dossier Compilation Accepted | `NSPL-EPE-DOS-{seq:04d}.pdf` |
| `nspl-weekly.html` | NSPL Weekly Status Report for EPE Review | Manual trigger (Tuesday weekly cron) | `NSPL-EPE-WSR-{seq:04d}.pdf` |

**Initial 5 templates** (IMIR, Traveller, Cutting, Dispatch, NSPL Weekly) were built by Agent C.
**Remaining 18 templates** (001, 002, 003, 004, 007B, 007C, 008A, 008B, 012A, 012B, 013, 014, 015, 016A, 016B, 016C, 017A, 018) added by Agent H following the same styling spec.

All output PDFs are pushed to Drive folder `1NbGic6olppElgWJudWXmqtM8ajP8WaQZ` via
the `iqra-drive-upload` workflow and the resulting URL is written back to the
record's `pdf_url` field (Layer 5).

---

## Styling spec

- **Page**: A4 portrait, 15mm margins (22mm bottom for footer)
- **Body**: Inter 10.5pt / 10pt (NSPL Weekly), color `#444`
- **Headings**: pure black, lower-cased uppercased H2 with a 1.5px `#D4A017` (Iqra gold) underline
- **Tables**: 0.6pt grey borders, `#F5F5F5` header background, tabular-numerics in number columns
- **Brand**: `IQRA` wordmark in Cormorant Garamond 24pt + `Quality Assured.` tagline in 8pt gold uppercase. Inline SVG/text (no external image refs, so n8n's HTML→PDF node won't 404 on a missing file).
- **Footer**: fixed at 8mm from bottom, format `Confidential | Iqra Quality Services Pvt. Ltd. | NSPL/EPE/{form-code}/{seq:04d}` on the left; `Page X of Y` on the right (uses Puppeteer's built-in `pageNumber` / `totalPages` classes).
- **Locked stamp**: when `is_locked = true`, a 60pt gold "LOCKED — FINAL" stamp at 30 % opacity, rotated −30 °, in the top-right corner.
- **Dual signoff block**: bottom of every form template. Two `min-height: 110px` boxes.
  - **NSPL** box always renders with `nspl_name` / `nspl_role` / `nspl_signed_date`.
  - **IQRA** box renders only if `iqra_signed_date` is truthy. If empty, a red "Pending IQRA approval — not for outward issue" banner takes its place.
  - **Rule A6** compliance: signatures are **text names only**, no signature images.

No third-party CSS framework. All styles inline in `<style>`. Fonts loaded from Google Fonts.

---

## Mustache placeholders

The templates use a Mustache-compatible subset (matches the `mustache` npm package
that the n8n `Code` node should `require`). Supported syntax:

| Syntax | Meaning |
|---|---|
| `{{field_name}}` | Simple substitution. HTML-escaped. |
| `{{a.b.c}}` | Nested object access (e.g. `{{chem.C}}`, `{{mech.yield}}`). |
| `{{#section}} ... {{/section}}` | Truthy block. If section is an array, iterates with each item as the current context. If it's an object, pushes it as a sub-context. |
| `{{^section}} ... {{/section}}` | Inverted: renders only when value is falsy / empty / missing. |

**Important n8n pattern**: in the `Code` node before HTML→PDF, do:

```js
const Mustache = require('mustache');
const template = $('Read template file').first().json.data;
const data = $json; // record + extras from prior Airtable nodes
return [{ json: { html: Mustache.render(template, data) } }];
```

Then feed `html` into the Puppeteer / HTML→PDF node.

---

## Sample data files (`sample-data/`)

| File | Shape |
|---|---|
| `imir-005.json` | Single record. `chem`/`spec`/`mech`/`mech_spec` are nested objects. `photos[]` is an array of `{title, filename, captured_at, ocr_confidence, ocr_status, note}`. |
| `traveller-006.json` | Single record. `has_parent_child` (bool) gates the parent-child table. `child_marks[]` array. `photos[]` array. |
| `cutting-007a.json` | Single record. `dimensions[]` array with `{name, specified, tolerance, measured, deviation, result, result_class}` — `result_class` is `result-pass` or `result-fail`. Edge/cut quality has flat fields `edge_straightness_*`, `slag_*`, etc. |
| `dispatch-017b.json` | Single record. `packages[]` (FRM-U2-017A package rows), `loading_photos[]`, `iqra_checks[]`. Weight reconciliation fields: `calculated_total_weight`, `weigh_slip_weight`, `weight_variance_mt`, `weight_variance_pct`, `variance_class` (`variance-ok` or `variance-bad`), `variance_flag_text`. |
| `nspl-weekly.json` | All 12 sections A-K (plus optional L) as nested arrays / objects. Matches the structure of `/tmp/iqra_NSPL_Status_Report_Illustrative_Example_EPE_Jinnaram.txt` 1:1. |

### Common fields on every form template

```
record_id, report_no, seq_padded, project_id, phase,
report_issue_date, activity_date,
iqra_review_status, iqra_review_date, iqra_reviewer, iqra_condition_note,
nspl_name, nspl_role, nspl_signed_date,
iqra_name, iqra_role, iqra_signed_date,    // iqra_signed_date may be ""
is_locked                                    // bool
```

---

## Local rendering / preview

```
cd /Users/sandy/iqra-airtable-build/pdf-templates
node render.mjs                       # renders all 23 templates as PDFs (Puppeteer)
node render.mjs drawing-issue-001     # renders one

# HTML-only (sandbox-friendly, no Puppeteer required):
node render-html-only.mjs             # writes preview/{name}.rendered.html for all 23

# Output:
#   preview/{name}.pdf
#   preview/{name}.rendered.html   (substituted HTML for quick eyeball)
```

`render.mjs` re-uses the Puppeteer install at
`/Users/sandy/Downloads/Claude Code/client-data/pilani-group/pitch-deck/node_modules/puppeteer`
and ships a tiny inline Mustache implementation (no extra `npm install` needed).

`render-html-only.mjs` is the sandbox-friendly companion: runs the same Mustache
implementation but skips Puppeteer, so it works in restricted shells where the
cross-directory Puppeteer install isn't reachable. It also flags any unresolved
`{{ placeholder }}` tags as a sanity check.

`screenshot.mjs` produces page-1 PNGs in `preview/` for visual QA.

---

## n8n integration (workflow `iqra-pdf-generation`)

**Trigger**: Airtable webhook on `iqra_review_status` change to `Accepted` or
`Accepted with condition` on any FRM-U2-XXX table.

**Node sequence**:

1. **Webhook**: receives `{table, recordId}`.
2. **Switch by table**: maps Airtable table → template filename (e.g. `tbl005…` → `imir-005.html`).
3. **Airtable: Get record** (full record).
4. **Airtable: Get linked records** (per template needs):
   - IMIR: Photo_Evidence_Register rows where `linked_record = recordId`, MTC OCR extract record.
   - Traveller: source IMIR Lot row, child part marks (rollup), photos.
   - Cutting: source Traveller row, dimension records, photos.
   - Dispatch: packages from `FRM-U2-017A` (filter trip_id), weigh slip, photos.
   - NSPL Weekly: most fields are aggregated by `iqra-status-propagation` into a dedicated `NSPL_Weekly_Snapshot` table; this node just reads the latest row.
5. **Code (shape data)**: transforms Airtable fields into the JSON shape shown in `sample-data/{name}.json`. Key transforms:
   - `severity_flag` → `severity_class` (`normal` / `amber` / `red` / `critical`)
   - dimension `result` → `result_class` (`result-pass` / `result-fail`)
   - weight variance % → `variance_class` (`variance-ok` if ≤ 5, else `variance-bad`)
   - `is_locked = (iqra_review_status === 'Accepted' && iqra_signed_date != null && report_issue_date != null)`
   - `seq_padded = String(seq).padStart(4, '0')`
6. **Read Binary File**: load `pdf-templates/{name}.html` from disk (or fetch via raw GitHub URL once committed).
7. **Code (Mustache render)**: `const Mustache = require('mustache'); return Mustache.render(html, data);`
8. **HTML → PDF (Puppeteer node)**: format A4, `printBackground: true`, margins as in the template.
9. **Drive upload**: into folder `1NbGic6olppElgWJudWXmqtM8ajP8WaQZ`, name `{record_id}.pdf`.
10. **Airtable: Update record**: set `pdf_url`, `report_issue_date = today`.

---

## Tone & content notes

- **IMIR / Traveller / Cutting / Dispatch** are IQRA inspection-voice reports. Pass/fail, deviations, OCR confidence are the load-bearing language.
- **NSPL Weekly** is **manufacturer-facing, calm, business-ready** (per Raghu's 14-Apr-2026 confirmation). Avoid IQRA-inspection language; mirror the verbatim phrasing in the illustrative example (e.g., "Under action", "first roof-linked fronts only", "one-week delay on affected fronts only").
- All 5 templates avoid the em-dash / dash divider style (per global writing rules) — section dividers use the gold underline on H2 instead.
- No emoji. No marketing flourishes. No QR codes. No external image references.

---

## Files

```
pdf-templates/
├── README.md                       (this file)
├── render.mjs                      local Mustache + Puppeteer renderer
├── screenshot.mjs                  page-1 PNG snapshots for QA
├── imir-005.html
├── traveller-006.html
├── cutting-007a.html
├── dispatch-017b.html
├── nspl-weekly.html
├── sample-data/
│   ├── imir-005.json
│   ├── traveller-006.json
│   ├── cutting-007a.json
│   ├── dispatch-017b.json
│   └── nspl-weekly.json
└── preview/                        gitignored — created by render.mjs
    ├── imir-005.pdf
    ├── imir-005.rendered.html
    ├── imir-005.page1.png
    ├── traveller-006.pdf
    ├── traveller-006.rendered.html
    ├── traveller-006.page1.png
    ├── cutting-007a.pdf
    ├── cutting-007a.rendered.html
    ├── cutting-007a.page1.png
    ├── dispatch-017b.pdf
    ├── dispatch-017b.rendered.html
    ├── dispatch-017b.page1.png
    ├── nspl-weekly.pdf
    ├── nspl-weekly.rendered.html
    └── nspl-weekly.page1.png
```

---

## Known TODOs (handoff to Sandy + Agent B)

1. **Real Iqra logo** — currently text "IQRA" + tagline placeholder per spec out-of-scope. Once Raghu provides SVG, swap the `<div class="brand">` block in all 5 templates.
2. **Mustache module in n8n** — confirm `mustache` (or `handlebars`) is available in the n8n Code node runtime; the project's Hostinger/Cloud n8n may need a custom env var or a Function node implementation.
3. **OCR extracted-vs-spec colouring** — currently flat. If Raghu wants per-cell pass/fail highlighting on the chemistry / mechanical tables, add `result_class` to each cell and a CSS `td.cell-fail` style.
4. **NSPL Weekly auto-aggregation** — Section C / D / E / F / G are currently dummy-data; needs the `NSPL_Weekly_Snapshot` aggregation logic from Agent B's `iqra-status-propagation` workflow to populate from live FRM-U2-XXX rows + Held Points tracker.
5. **Append progress log entries** — see `/Users/sandy/iqra-airtable-build/notes/build-log.md`.

---

Agent C build log appended to `/Users/sandy/iqra-airtable-build/notes/build-log.md`.
