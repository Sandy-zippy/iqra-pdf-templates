#!/usr/bin/env python3
"""
IQRA QMS — Phase 3 PDF template generator.

Generates one Mustache HTML template + one sample-data JSON per form for:
  - 22 Unit I forms (FRM-U1-001 .. FRM-U1-022)
  - 41 Site Erection forms (SE-001 .. SE-042, SKIP SE-013 already built)

Templates share the IMIR-005 / site-receipt-013 style:
  - A4 portrait, Inter body, Cormorant Garamond brand, gold #D4A017 H2 underline
  - Dual signoff (NSPL maker + IQRA checker)
  - Locked stamp when iqra_review_status = Accepted
  - Renders L1 fields as a key-value table
  - L2/5 derived/system fields as a separate block
  - Attachment list with companions
  - Iqra branding (warm cream bg via @page, charcoal text)
"""
import json
import re
import os
from pathlib import Path

ROOT = Path('/Users/sandy/iqra-airtable-build/pdf-templates')
SAMPLE_DIR = ROOT / 'sample-data'
SAMPLE_DIR.mkdir(exist_ok=True)

U1_SPEC = Path('/Users/sandy/iqra-airtable-build/notes/unit-i-form-specs.json')
SE_SPEC = Path('/Users/sandy/iqra-airtable-build/notes/site-erection-form-specs.json')

PROJECT_ID = 'J-126 EPE Jinnaram PEB'

# Shared CSS extracted from imir-005.html and site-receipt-013.html, with
# Iqra/ZippyScale touches (cream bg behind page, lime accent option). All values
# tuned for Browserless PDF rendering — every var ends up inside @page padding.
CSS_BLOCK = r"""<style>
  @page { size: A4 portrait; margin: 15mm 15mm 22mm 15mm; }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0; background: #FFFDF7;
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    font-size: 10.5pt; color: #2A2A35; line-height: 1.42;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
  }
  h1, h2, h3, h4 { color: #000; font-weight: 600; margin: 0; }
  h1 { font-size: 16pt; letter-spacing: 0.5px; }
  h2 { font-size: 12pt; margin: 14px 0 6px; padding-bottom: 3px; border-bottom: 1.5px solid #D4A017; text-transform: uppercase; letter-spacing: 0.5px; }
  h3 { font-size: 10.5pt; margin: 10px 0 4px; color: #000; }
  .small { font-size: 9pt; color: #666; }
  .muted { color: #777; }
  .accent { color: #D4A017; font-weight: 600; }
  .lime-pill { display: inline-block; background: #D5EB4B; color: #2A2A35; padding: 2px 9px; border-radius: 3px; font-size: 9pt; font-weight: 700; letter-spacing: 0.4px; }
  .doc-header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 14px; }
  .brand { display: flex; align-items: center; gap: 10px; }
  .brand .logo { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 24pt; font-weight: 700; color: #000; line-height: 1; letter-spacing: 2px; }
  .brand .tag { font-size: 8pt; color: #D4A017; letter-spacing: 1px; font-weight: 600; text-transform: uppercase; }
  .header-meta { text-align: right; font-size: 9pt; color: #444; }
  .header-meta .title { font-size: 13pt; color: #000; font-weight: 700; letter-spacing: 0.5px; }
  .header-meta .row { margin-top: 3px; }
  .header-meta .label { color: #888; }
  table { width: 100%; border-collapse: collapse; margin: 6px 0 10px; font-size: 9.5pt; }
  th, td { border: 0.6pt solid #BBB; padding: 5px 7px; vertical-align: top; text-align: left; }
  th { background: #F5F5F5; color: #000; font-weight: 600; font-size: 9pt; text-transform: uppercase; letter-spacing: 0.4px; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; }
  .kv-table th { width: 32%; }
  .compact td, .compact th { padding: 3.5px 6px; font-size: 9pt; }
  .photo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 6px 0; }
  .photo-tile { border: 0.6pt solid #BBB; padding: 6px; text-align: center; background: #FAFAFA; }
  .photo-tile .ph { background: #ECECEC; height: 80px; display: flex; align-items: center; justify-content: center; color: #777; font-size: 9pt; }
  .photo-tile .cap { margin-top: 4px; font-size: 8.5pt; color: #555; word-wrap: break-word; }
  .review-banner { background: #FFF8DC; border-left: 3px solid #D4A017; padding: 8px 10px; margin: 8px 0; font-size: 9.5pt; }
  .signoff { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 16px; padding-top: 12px; border-top: 1.5px solid #000; page-break-inside: avoid; }
  .signoff .box { border: 0.6pt solid #BBB; padding: 8px 10px; min-height: 110px; background: #FAFAFA; }
  .signoff .box .role { font-size: 8.5pt; color: #888; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
  .signoff .box .name { font-size: 12pt; font-weight: 600; color: #000; margin-top: 22px; font-family: 'Cormorant Garamond', Georgia, serif; }
  .signoff .box .date { font-size: 9pt; color: #555; margin-top: 4px; }
  .pending-block { background: #FFEBEB; border-left: 3px solid #C0392B; padding: 8px 10px; min-height: 90px; color: #C0392B; font-weight: 600; font-size: 10pt; }
  .footer { position: fixed; bottom: 8mm; left: 15mm; right: 15mm; display: flex; justify-content: space-between; font-size: 8pt; color: #888; border-top: 0.5pt solid #CCC; padding-top: 4px; }
  .locked-stamp { position: fixed; top: 30mm; right: 18mm; font-size: 60pt; color: #D4A017; opacity: 0.30; transform: rotate(-30deg); font-weight: 700; pointer-events: none; font-family: 'Cormorant Garamond', Georgia, serif; letter-spacing: 2px; }
  .placeholder-banner { background: #FFF3E0; border: 1px dashed #D4A017; padding: 16px 18px; margin: 14px 0; color: #8A6A00; font-size: 10.5pt; }
  .placeholder-banner strong { color: #5A4400; }
  section { page-break-inside: avoid; }
</style>"""


# ---------- HELPERS -------------------------------------------------------

def slugify_form_id(form_id):
    """FRM-U1-001 -> frm-u1-001; SE-001 -> se-001"""
    return form_id.lower().replace('_', '-')


def normalize_u1_field(field):
    """Normalize Unit I field record into common shape."""
    return {
        'name': field.get('name') or field.get('field_id'),
        'label': field.get('label') or field.get('name'),
        'type': field.get('type') or field.get('raw_type') or 'text',
        'who_fills': field.get('who_fills') or '',
    }


def normalize_se_field(field):
    """Normalize Site Erection field record into common shape."""
    fid = field.get('field_id') or ''
    return {
        'name': fid,
        'label': field.get('field_label') or fid,
        'type': field.get('field_type') or 'text',
        'who_fills': field.get('who_fills') or '',
    }


def normalize_attachment(att, lane):
    """Both U1 and SE attachment formats."""
    if lane == 'U1':
        return {
            'name': att.get('name'),
            'label': att.get('label') or att.get('name'),
            'ocr_required': bool(att.get('ocr_required')),
        }
    # SE
    return {
        'name': att.get('field_id') or att.get('name'),
        'label': att.get('field_label') or att.get('label') or att.get('field_id'),
        'ocr_required': True,
    }


def render_l1_table(fields):
    """Render layer 1 fields as Mustache key-value rows."""
    if not fields:
        return '<p class="small">No Layer 1 fields defined for this form yet.</p>'
    # Skip pure attachment fields (handled in their own section).
    rendered_fields = [f for f in fields if f['name'] and (f['type'] or '').lower() != 'attachment']
    if not rendered_fields:
        return '<p class="small">All Layer 1 evidence captured in the attachments section below.</p>'
    rows = []
    for f in rendered_fields:
        name = f['name']
        label = f['label']
        rows.append(f'    <tr><th>{label}</th><td>{{{{{name}}}}}</td></tr>')
    return (
        '<table class="kv-table compact">\n'
        + '\n'.join(rows)
        + '\n  </table>'
    )


def render_l2_table(fields):
    """Render layer 2/5 derived/system fields."""
    keepers = [f for f in fields if f['name'] and f['name'] not in {
        'record_id', 'project_id', 'lane', 'form_version',
        'iqra_review_status', 'iqra_condition_note',
        'submission_timestamp', 'activity_date', 'review_date', 'report_issue_date',
        'maker_name', 'checker_name', 'iqra_review_date',
        'backfill_flag', 'backfill_work_packet_id',
        'return_hold_reason_note',
    }]
    if not keepers:
        return '<p class="small">Derived fields handled by IQRA review block (below).</p>'
    rows = []
    for f in keepers[:20]:  # cap to keep PDF readable
        rows.append(
            f'    <tr><th>{f["label"]}</th><td>{{{{{f["name"]}}}}}</td></tr>'
        )
    return (
        '<table class="kv-table compact">\n'
        + '\n'.join(rows)
        + '\n  </table>'
    )


def render_attachments_block(attachments):
    """Mustache section for attachments (with companions)."""
    if not attachments:
        return '<p class="small">No attachments expected for this form.</p>'
    tiles = []
    for att in attachments:
        if not att['name']:
            continue
        nm = att['name']
        label = att['label']
        tiles.append(
            f'    <div class="photo-tile">\n'
            f'      <div class="ph">{label}</div>\n'
            f'      <div class="cap">{{{{#{nm}_drive_url}}}}<a href="{{{{{nm}_drive_url}}}}">{{{{{nm}_filename}}}}{{{{^{nm}_filename}}}}Open in Drive{{{{/{nm}_filename}}}}</a>{{{{/{nm}_drive_url}}}}{{{{^{nm}_drive_url}}}}<span class="muted">Not uploaded</span>{{{{/{nm}_drive_url}}}}</div>\n'
            f'      <div class="cap small">OCR: {{{{{nm}_ocr_status}}}}{{{{#{nm}_ocr_confidence}}}} ({{{{{nm}_ocr_confidence}}}}%){{{{/{nm}_ocr_confidence}}}}</div>\n'
            f'    </div>'
        )
    if not tiles:
        return '<p class="small">No named attachments resolved yet.</p>'
    return '<div class="photo-grid">\n' + '\n'.join(tiles) + '\n  </div>'


# ---------- TEMPLATE BUILDER ---------------------------------------------

def build_template(form_id, form_title, owner_role, checker_role, lane,
                   l1_fields, l2_fields, attachments, placeholder=False,
                   purpose=''):
    title_safe = form_title.replace('—', '-').strip()
    phase_label = 'Site Erection' if lane == 'SE' else 'Unit I — Workshop'

    if placeholder:
        body_sections = f"""
<div class="placeholder-banner">
  <strong>Form schema pending Raghu's review.</strong><br>
  This template is a placeholder. The Layer 1 field set for <strong>{form_id}</strong>
  has not yet been finalised in the canonical workbook. PDF generation for this form
  is on hold until field detail is added in the source spec and this template is
  regenerated.
</div>

<h2>Record Metadata</h2>
<table class="kv-table compact">
  <tr><th>Record ID</th><td>{{{{record_id}}}}</td></tr>
  <tr><th>Project</th><td>{PROJECT_ID}</td></tr>
  <tr><th>Phase</th><td>{phase_label}</td></tr>
  <tr><th>Activity Date</th><td>{{{{activity_date}}}}</td></tr>
  <tr><th>Submission Date</th><td>{{{{submission_timestamp}}}}</td></tr>
  <tr><th>IQRA Review Date</th><td>{{{{iqra_review_date}}}}</td></tr>
  <tr><th>Report Issue Date</th><td>{{{{report_issue_date}}}}</td></tr>
</table>
""".strip()
    else:
        l1_html = render_l1_table(l1_fields)
        l2_html = render_l2_table(l2_fields)
        att_html = render_attachments_block(attachments)
        purpose_html = ''
        if purpose:
            safe_purpose = purpose.replace('—', '-').strip()
            purpose_html = f'<p class="small"><strong>Purpose:</strong> {safe_purpose}</p>'
        body_sections = f"""
{purpose_html}

<h2>Record Metadata</h2>
<table class="kv-table compact">
  <tr><th>Record ID</th><td>{{{{record_id}}}}</td></tr>
  <tr><th>Project</th><td>{PROJECT_ID}</td></tr>
  <tr><th>Phase</th><td>{phase_label}</td></tr>
  <tr><th>Activity Date</th><td>{{{{activity_date}}}}</td></tr>
  <tr><th>Submission Date</th><td>{{{{submission_timestamp}}}}</td></tr>
  <tr><th>IQRA Review Date</th><td>{{{{iqra_review_date}}}}</td></tr>
  <tr><th>Report Issue Date</th><td>{{{{report_issue_date}}}}</td></tr>
</table>

<h2>Layer 1 — NSPL Submission Data</h2>
{l1_html}

<h2>Layer 2 / 5 — Derived &amp; System Fields</h2>
{l2_html}

<h2>Attachments</h2>
{att_html}
""".strip()

    review_section = """
<h2>IQRA Review</h2>
<div class="review-banner">
  <strong>Status:</strong> {{iqra_review_status}}
  {{#iqra_condition_note}}<br><strong>Condition:</strong> {{iqra_condition_note}}{{/iqra_condition_note}}
  {{#return_hold_reason_note}}<br><strong>Return / Hold Reason:</strong> {{return_hold_reason_note}}{{/return_hold_reason_note}}
</div>
""".strip()

    signoff = f"""
<div class="signoff">
  <div class="box">
    <div class="role">NSPL — Maker</div>
    <div class="name">{{{{nspl_name}}}}</div>
    <div class="date">{{{{nspl_role}}}}{{{{^nspl_role}}}}{owner_role}{{{{/nspl_role}}}}</div>
    <div class="date">{{{{#nspl_mobile}}}}Mobile: {{{{nspl_mobile}}}} &middot; {{{{/nspl_mobile}}}}Signed: {{{{nspl_signed_date}}}}</div>
  </div>
  {{{{#iqra_signed_date}}}}
  <div class="box">
    <div class="role">IQRA — Checker</div>
    <div class="name">{{{{iqra_name}}}}</div>
    <div class="date">{{{{iqra_role}}}}{{{{^iqra_role}}}}{checker_role}{{{{/iqra_role}}}}</div>
    <div class="date">Signed: {{{{iqra_signed_date}}}}</div>
  </div>
  {{{{/iqra_signed_date}}}}
  {{{{^iqra_signed_date}}}}
  <div class="pending-block">
    Pending IQRA approval — record not yet locked for outward issue.
  </div>
  {{{{/iqra_signed_date}}}}
</div>
""".strip()

    header_form_no = form_id
    title_uppercase = title_safe.upper()
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>{form_id} - {title_safe} - {{{{record_id}}}}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
{CSS_BLOCK}
</head>
<body>

{{{{#is_locked}}}}<div class="locked-stamp">LOCKED — FINAL</div>{{{{/is_locked}}}}

<div class="doc-header">
  <div class="brand">
    <div>
      <div class="logo">IQRA</div>
      <div class="tag">Quality Assured.</div>
    </div>
  </div>
  <div class="header-meta">
    <div class="title">{title_uppercase}</div>
    <div class="row"><span class="label">Form:</span> <span class="lime-pill">{header_form_no}</span></div>
    <div class="row"><span class="label">Project:</span> {PROJECT_ID}</div>
    <div class="row"><span class="label">Phase:</span> {phase_label}</div>
    <div class="row"><span class="label">Record:</span> <strong>{{{{record_id}}}}</strong></div>
    <div class="row"><span class="label">Issue Date:</span> {{{{report_issue_date}}}}</div>
  </div>
</div>

{body_sections}

{review_section}

{signoff}

<div class="footer">
  <div>Confidential | Iqra Quality Services Pvt. Ltd. | {form_id} | NSPL/EPE/{{{{record_id}}}}</div>
  <div>Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>
</div>

</body>
</html>
"""
    return html


# ---------- SAMPLE DATA BUILDER ------------------------------------------

def build_sample_data(form_id, form_title, owner_role, checker_role, lane,
                      l1_fields, l2_fields, attachments, placeholder=False):
    record_id = f"NSPL-EPE-{form_id}-0001"
    phase_label = 'Site Erection' if lane == 'SE' else 'Unit I — Workshop'
    sample = {
        'record_id': record_id,
        'project_id': PROJECT_ID,
        'phase': phase_label,
        'lane': lane,
        'activity_date': '2026-05-20',
        'submission_timestamp': '2026-05-20T11:42:00+05:30',
        'review_date': '2026-05-21T10:15:00+05:30',
        'iqra_review_date': '2026-05-21',
        'report_issue_date': '2026-05-21',
        'iqra_review_status': 'Accepted',
        'iqra_condition_note': '',
        'return_hold_reason_note': '',
        'maker_name': 'A. Verma',
        'checker_name': 'P. Krishnan (IQRA)',
        'nspl_name': 'A. Verma',
        'nspl_role': owner_role,
        'nspl_mobile': '+91 98480 12345',
        'nspl_signed_date': '2026-05-20',
        'iqra_name': 'P. Krishnan',
        'iqra_role': checker_role,
        'iqra_signed_date': '2026-05-21',
        'is_locked': True,
    }
    if placeholder:
        return sample

    # Fill L1 fields with plausible placeholders so the PDF preview reads well.
    for f in l1_fields:
        nm = f['name']
        if not nm or nm in sample:
            continue
        t = (f['type'] or 'text').lower()
        label = f['label']
        if t in ('attachment', 'document'):
            continue
        if t in ('date',):
            sample[nm] = '2026-05-20'
        elif t in ('datetime',):
            sample[nm] = '2026-05-20T10:00:00+05:30'
        elif t in ('checkbox', 'boolean'):
            sample[nm] = True
        elif t in ('number', 'currency', 'percent'):
            sample[nm] = 0
        elif t.startswith('multi'):
            sample[nm] = 'Sample A, Sample B'
        elif t in ('select', 'single_select', 'object-first dropdown'):
            sample[nm] = f'Sample {label}'
        else:
            sample[nm] = f'Sample {label}'

    # Fill L2/5 fields with realistic mock values too.
    for f in l2_fields:
        nm = f['name']
        if not nm or nm in sample:
            continue
        t = (f['type'] or 'text').lower()
        label = f['label']
        if t in ('attachment', 'document'):
            continue
        if t in ('date',):
            sample[nm] = '2026-05-20'
        elif t in ('datetime',):
            sample[nm] = '2026-05-20T10:00:00+05:30'
        elif t in ('checkbox', 'boolean'):
            sample[nm] = False
        elif t in ('number', 'currency', 'percent'):
            sample[nm] = 0
        elif t in ('linked_record', 'lookup'):
            sample[nm] = label
        else:
            sample[nm] = f'(auto) {label}'

    # Attachments + companions
    for att in attachments:
        nm = att['name']
        if not nm:
            continue
        sample[f'{nm}_filename'] = f'{nm}_sample.pdf'
        sample[f'{nm}_drive_url'] = f'https://drive.google.com/file/d/sample-{nm}/view'
        sample[f'{nm}_ocr_status'] = 'OK'
        sample[f'{nm}_ocr_confidence'] = 96

    return sample


# ---------- DRIVER -------------------------------------------------------

def main():
    written = []

    # --- Unit I ---
    with open(U1_SPEC) as f:
        u1 = json.load(f)
    for form in u1['forms']:
        form_id = form['form_id']
        l1 = [normalize_u1_field(x) for x in (form.get('layer_1_fields') or [])]
        l2 = [normalize_u1_field(x) for x in (form.get('layer_2_5_fields') or [])]
        atts = [normalize_attachment(x, 'U1') for x in (form.get('attachments') or [])]
        html = build_template(
            form_id=form_id,
            form_title=form.get('form_title') or form_id,
            owner_role=form.get('owner_role') or 'NSPL Unit I',
            checker_role=form.get('checker_role') or 'IQRA',
            lane='U1',
            l1_fields=l1, l2_fields=l2, attachments=atts,
            placeholder=False,
            purpose=form.get('purpose') or '',
        )
        sample = build_sample_data(
            form_id=form_id,
            form_title=form.get('form_title') or form_id,
            owner_role=form.get('owner_role') or 'NSPL Unit I',
            checker_role=form.get('checker_role') or 'IQRA',
            lane='U1',
            l1_fields=l1, l2_fields=l2, attachments=atts,
            placeholder=False,
        )
        slug = slugify_form_id(form_id)
        (ROOT / f'{slug}.html').write_text(html)
        (SAMPLE_DIR / f'{slug}.json').write_text(json.dumps(sample, indent=2))
        written.append((form_id, slug, form.get('form_title')))

    # --- Site Erection ---
    with open(SE_SPEC) as f:
        se = json.load(f)
    for form in se['forms']:
        form_id = form['form_id']
        if form.get('already_built'):
            # SE-013 — skip, has its own hand-tuned template.
            continue
        is_placeholder = bool(form.get('unclear')) or (
            not form.get('layer_1_fields') and not form.get('layer_2_5_fields')
        )
        # Also detect SE forms where every layer1 field has `name: None`
        l1_raw = form.get('layer_1_fields') or []
        l1 = [normalize_se_field(x) for x in l1_raw]
        l1 = [f for f in l1 if f['name']]
        l2_raw = form.get('layer_2_5_fields') or []
        l2 = [normalize_se_field(x) for x in l2_raw]
        l2 = [f for f in l2 if f['name']]
        atts = [normalize_attachment(x, 'SE') for x in (form.get('attachments') or [])]

        if not l1 and not l2 and not atts:
            is_placeholder = True

        html = build_template(
            form_id=form_id,
            form_title=form.get('form_title') or form_id,
            owner_role=form.get('owner_role') or 'NSPL Site QC',
            checker_role=form.get('checker_role') or 'IQRA',
            lane='SE',
            l1_fields=l1, l2_fields=l2, attachments=atts,
            placeholder=is_placeholder,
            purpose=form.get('purpose') or '',
        )
        sample = build_sample_data(
            form_id=form_id,
            form_title=form.get('form_title') or form_id,
            owner_role=form.get('owner_role') or 'NSPL Site QC',
            checker_role=form.get('checker_role') or 'IQRA',
            lane='SE',
            l1_fields=l1, l2_fields=l2, attachments=atts,
            placeholder=is_placeholder,
        )
        slug = slugify_form_id(form_id)
        (ROOT / f'{slug}.html').write_text(html)
        (SAMPLE_DIR / f'{slug}.json').write_text(json.dumps(sample, indent=2))
        written.append((form_id, slug, form.get('form_title')))

    print(f'Wrote {len(written)} templates:')
    for fid, slug, title in written:
        print(f'  {fid} -> {slug}.html  ({title})')

    # Manifest for later steps (n8n router mapping + share-links update).
    manifest = [
        {'form_id': fid, 'slug': slug, 'title': title}
        for fid, slug, title in written
    ]
    (ROOT / '_phase3_manifest.json').write_text(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
