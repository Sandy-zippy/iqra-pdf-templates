#!/usr/bin/env node
/**
 * IQRA QMS — PDF template renderer
 * Usage: node render.mjs                     # renders all templates
 *        node render.mjs imir-005            # renders one template
 *
 * Reads ./sample-data/{name}.json, substitutes Mustache placeholders into
 * ./{name}.html, and writes the PDF to ./preview/{name}.pdf.
 *
 * Uses Puppeteer from the pilani-group pitch-deck install (per memory).
 */

import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';
import { hydrateLoops } from './hydrate-loops.mjs';

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));
const PUPPETEER_PATH = '/Users/sandy/zippyscale-hub/client-data/pilani-group/pitch-deck/node_modules/puppeteer';

// ---- Tiny mustache implementation (subset) ----------------------------
// Supports:
//   {{ var }} and {{ a.b.c }}
//   {{# section }}...{{/ section }}   (truthy / array iteration)
//   {{^ section }}...{{/ section }}   (inverted)
//
// Good enough for our 5 templates; n8n production will use the native
// Puppeteer node + a Mustache module which is fully compliant.

function lookup(ctxStack, key) {
  if (key === '.') return ctxStack[ctxStack.length - 1];
  const parts = key.split('.');
  for (let i = ctxStack.length - 1; i >= 0; i--) {
    let val = ctxStack[i];
    let ok = true;
    for (const p of parts) {
      if (val != null && Object.prototype.hasOwnProperty.call(val, p)) {
        val = val[p];
      } else { ok = false; break; }
    }
    if (ok) return val;
  }
  return undefined;
}

function isTruthy(v) {
  if (v == null || v === false) return false;
  if (typeof v === 'string' && v.length === 0) return false;
  if (Array.isArray(v) && v.length === 0) return false;
  return true;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function render(tpl, data) {
  const ctxStack = [data];

  function walk(str) {
    let out = '';
    let i = 0;
    while (i < str.length) {
      const open = str.indexOf('{{', i);
      if (open === -1) { out += str.slice(i); break; }
      out += str.slice(i, open);
      const close = str.indexOf('}}', open + 2);
      if (close === -1) { out += str.slice(open); break; }
      const tag = str.slice(open + 2, close).trim();
      i = close + 2;

      if (tag.startsWith('#') || tag.startsWith('^')) {
        const inverted = tag.startsWith('^');
        const key = tag.slice(1).trim();
        const endTag = '{{/' + key + '}}';
        const endIdx = str.indexOf(endTag, i);
        if (endIdx === -1) { out += '[unclosed section ' + key + ']'; break; }
        const inner = str.slice(i, endIdx);
        i = endIdx + endTag.length;
        const val = lookup(ctxStack, key);
        if (inverted) {
          if (!isTruthy(val)) out += walk(inner);
        } else if (Array.isArray(val)) {
          for (const item of val) {
            ctxStack.push(item);
            out += walk(inner);
            ctxStack.pop();
          }
        } else if (isTruthy(val)) {
          if (typeof val === 'object') {
            ctxStack.push(val);
            out += walk(inner);
            ctxStack.pop();
          } else {
            out += walk(inner);
          }
        }
      } else if (tag.startsWith('/')) {
        // stray closer — skip
      } else {
        const val = lookup(ctxStack, tag);
        if (val == null) out += '';
        else out += escapeHtml(val);
      }
    }
    return out;
  }

  return walk(tpl);
}

// ---- Main -------------------------------------------------------------

const templates = [
  'drawing-issue-001',
  'document-master-002',
  'calibration-003',
  'readiness-004',
  'imir-005',
  'traveller-006',
  'cutting-007a',
  'drilling-parts-007b',
  'drilling-builtup-007c',
  'fitup-saw-008a',
  'fitup-fcaw-008b',
  'welding-saw-012a',
  'welding-fcaw-012b',
  'pt-dpt-013',
  'repair-014',
  'final-release-015',
  'blasting-016a',
  'primer-016b',
  'final-coat-016c',
  'marking-packing-017a',
  'dispatch-017b',
  'dossier-index-018',
  'dossier-index-site',
  'nspl-weekly'
];
const only = process.argv[2];
const list = only ? [only] : templates;

const previewDir = path.join(__dirname, 'preview');
if (!fs.existsSync(previewDir)) fs.mkdirSync(previewDir, { recursive: true });

const puppeteer = (await import(path.join(PUPPETEER_PATH, 'lib', 'esm', 'puppeteer', 'puppeteer.js'))).default;

const browser = await puppeteer.launch({
  headless: 'new',
  ...(process.env.PUPPETEER_EXECUTABLE_PATH ? { executablePath: process.env.PUPPETEER_EXECUTABLE_PATH } : {}), // ponytail: pin cached Chrome-for-Testing when bundled ver missing
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
});

try {
  for (const name of list) {
    const tplPath = path.join(__dirname, `${name}.html`);
    const dataPath = path.join(__dirname, 'sample-data', `${name}.json`);
    const outPath = path.join(previewDir, `${name}.pdf`);

    if (!fs.existsSync(tplPath)) { console.error(`[skip] no template ${tplPath}`); continue; }
    if (!fs.existsSync(dataPath)) { console.error(`[skip] no sample data ${dataPath}`); continue; }

    const tpl = fs.readFileSync(tplPath, 'utf8');
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    hydrateLoops(data, tpl);
    const html = render(tpl, data);

    // also drop the rendered HTML for visual inspection
    const renderedHtmlPath = path.join(previewDir, `${name}.rendered.html`);
    fs.writeFileSync(renderedHtmlPath, html, 'utf8');

    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle0' });
    await page.pdf({
      path: outPath,
      format: 'A4',
      printBackground: true,
      displayHeaderFooter: false,
      margin: { top: '15mm', right: '15mm', bottom: '22mm', left: '15mm' },
    });
    await page.close();
    console.log(`[ok] ${name} -> ${outPath}`);
  }
} finally {
  await browser.close();
}
