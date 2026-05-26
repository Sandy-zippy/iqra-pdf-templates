#!/usr/bin/env python3
"""Swap text-only IQRA placeholder + add NSPL logo + stamps on all 87 PDF templates.

Uses local brand assets in pdf-templates/brand-assets/:
  - iqra-logo.jpg
  - iqra-stamp.png
  - nspl-logo.jpeg
  - nspl-qc-stamp.png

After this, templates render with real logos + stamps when GH Pages serves them.
"""
import re
from pathlib import Path

PDF_DIR = Path("/Users/sandy/iqra-airtable-build/pdf-templates")
TEMPLATES = sorted([p for p in PDF_DIR.glob("*.html") if p.name != "index.html"])

# CSS additions for logos + stamps (injected before </style>)
CSS_PATCH = """
  /* Brand asset injection — added 2026-05-26 */
  .brand .logo-img { height: 56px; width: auto; display: block; }
  .brand .nspl-logo-img { height: 50px; width: auto; display: block; margin-top: 4px; }
  .brand-row { display: flex; flex-direction: column; gap: 4px; }
  .stamp-img { height: 90px; width: auto; opacity: 0.88; margin-top: 8px; display: block; }
  .sigbox { position: relative; }
"""

# Replacement for the text-only IQRA logo block
LOGO_OLD = re.compile(
    r'<div class="brand">\s*<div>\s*<div class="logo">IQRA</div>\s*<div class="tag">Quality Assured\.</div>\s*</div>\s*</div>',
    re.DOTALL,
)
LOGO_NEW = '''<div class="brand">
    <div class="brand-row">
      <img class="logo-img" src="brand-assets/iqra-logo.jpg" alt="Iqra Quality Services">
      <div class="tag">Quality Assured.</div>
    </div>
    <div class="brand-row" style="margin-left:18px;">
      <img class="nspl-logo-img" src="brand-assets/nspl-logo.jpeg" alt="Nischay Steels Pvt Ltd">
      <div class="tag" style="font-size:7.5pt;">Nischay Steels Pvt. Ltd.</div>
    </div>
  </div>'''

# NSPL signoff stamp injection — broadened to match: Submitted/Confirmed/Maintained/Compiled by NSPL ...
NSPL_SIGNOFF_PATTERNS = [
    re.compile(r'(<div class="siglabel">(?:Submitted|Submitted &amp; confirmed|Confirmed|Maintained|Compiled) (?:&amp; |)by NSPL[^<]*</div>)'),
    re.compile(r'(<h4>Compiled by NSPL[^<]*</h4>)'),
    re.compile(r'(<h4>NSPL[^<]*(?:Maker|Checker|Checked|Signed)[^<]*</h4>)'),
    re.compile(r'(<div class="role">NSPL[^<]*</div>)'),
]
NSPL_SIGNOFF_INSERT = '\n    {{#nspl_signed_date}}<img class="stamp-img" src="brand-assets/nspl-qc-stamp.png" alt="NSPL QC Stamp">{{/nspl_signed_date}}'

# IQRA signoff stamp injection — U2 pattern
IQRA_SIGNOFF_OLD = re.compile(
    r'(<div class="siglabel">Owner-side verification \(Iqra Quality Services\)</div>)',
)
IQRA_SIGNOFF_NEW = r'\1\n    <img class="stamp-img" src="brand-assets/iqra-stamp.png" alt="IQRA Stamp">'

# NSPL signoff stamp — U1/SE pattern (Agent Q generated)
NSPL_SIGNOFF_OLD_U1 = re.compile(
    r'(<div class="role">NSPL — Maker</div>)',
)
NSPL_SIGNOFF_NEW_U1 = r'\1\n    {{#nspl_signed_date}}<img class="stamp-img" src="brand-assets/nspl-qc-stamp.png" alt="NSPL QC Stamp">{{/nspl_signed_date}}'

# IQRA signoff stamp — U1/SE pattern (Agent Q generated)
IQRA_SIGNOFF_OLD_U1 = re.compile(
    r'(<div class="role">IQRA — Checker</div>)',
)
IQRA_SIGNOFF_NEW_U1 = r'\1\n    <img class="stamp-img" src="brand-assets/iqra-stamp.png" alt="IQRA Stamp">'

# Footer text — update to include both org names
FOOTER_OLD = re.compile(r'Confidential \| Iqra Quality Services Pvt\. Ltd\. \|')
FOOTER_NEW = 'Confidential | Iqra Quality Services Pvt. Ltd. + Nischay Steels Pvt. Ltd. |'


def patch_template(path: Path) -> dict:
    text = path.read_text()
    original_len = len(text)
    changes = []

    # 1. CSS injection — only if not already added
    if "/* Brand asset injection" not in text:
        text = text.replace("</style>", CSS_PATCH + "</style>", 1)
        changes.append("css")

    # 2. IQRA logo block swap
    new_text = LOGO_OLD.sub(LOGO_NEW, text)
    if new_text != text:
        text = new_text
        changes.append("logo")

    # 3. NSPL signoff stamp — try each pattern in turn until one matches
    nspl_stamped = False
    if "nspl-qc-stamp.png" not in text:
        for pat in NSPL_SIGNOFF_PATTERNS:
            new_text = pat.sub(lambda m: m.group(1) + NSPL_SIGNOFF_INSERT, text, count=1)
            if new_text != text:
                text = new_text
                nspl_stamped = True
                break
    if nspl_stamped:
        changes.append("nspl-stamp")

    # 4. IQRA signoff stamp — try U2 pattern first, then U1/SE pattern
    new_text = IQRA_SIGNOFF_OLD.sub(IQRA_SIGNOFF_NEW, text)
    if new_text == text:
        new_text = IQRA_SIGNOFF_OLD_U1.sub(IQRA_SIGNOFF_NEW_U1, text)
    if new_text != text:
        text = new_text
        changes.append("iqra-stamp")

    # 5. Footer text
    new_text = FOOTER_OLD.sub(FOOTER_NEW, text)
    if new_text != text:
        text = new_text
        changes.append("footer")

    if changes:
        path.write_text(text)
    return {"file": path.name, "changes": changes, "delta_bytes": len(text) - original_len}


def main():
    print(f"Patching {len(TEMPLATES)} templates...\n")
    results = {"ok": 0, "no_change": 0, "patches": []}
    for t in TEMPLATES:
        r = patch_template(t)
        results["patches"].append(r)
        if r["changes"]:
            results["ok"] += 1
        else:
            results["no_change"] += 1
        print(f"  {r['file']:50s} -> {r['changes']}")
    print(f"\n{'='*60}")
    print(f"Patched: {results['ok']} / {len(TEMPLATES)}")
    print(f"No-change: {results['no_change']}")
    # List which templates didn't get all 5 changes
    incomplete = [p for p in results["patches"] if len(p["changes"]) < 5 and p["changes"]]
    if incomplete:
        print(f"\nIncomplete patches ({len(incomplete)} files — may indicate template variants):")
        for p in incomplete[:10]:
            missing = set(["css", "logo", "nspl-stamp", "iqra-stamp", "footer"]) - set(p["changes"])
            print(f"  {p['file']:50s} missing: {missing}")


if __name__ == "__main__":
    main()
