#!/usr/bin/env node
/**
 * IQRA QMS - HTML-only renderer (no Puppeteer required)
 * Substitutes Mustache placeholders into ./{name}.html using
 * ./sample-data/{name}.json, writes preview/{name}.rendered.html.
 *
 * Use this for sandboxed environments where the Puppeteer install
 * lives outside the working directory. For PDF rendering, run
 * render.mjs (requires Puppeteer access).
 */

import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));

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
        // skip
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
  'nspl-weekly'
];

const only = process.argv[2];
const list = only ? [only] : templates;

const previewDir = path.join(__dirname, 'preview');
if (!fs.existsSync(previewDir)) fs.mkdirSync(previewDir, { recursive: true });

let okCount = 0;
let failCount = 0;
for (const name of list) {
  const tplPath = path.join(__dirname, `${name}.html`);
  const dataPath = path.join(__dirname, 'sample-data', `${name}.json`);
  if (!fs.existsSync(tplPath)) { console.error(`[skip] no template ${tplPath}`); failCount++; continue; }
  if (!fs.existsSync(dataPath)) { console.error(`[skip] no sample data ${dataPath}`); failCount++; continue; }
  try {
    const tpl = fs.readFileSync(tplPath, 'utf8');
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    const html = render(tpl, data);
    const outPath = path.join(previewDir, `${name}.rendered.html`);
    fs.writeFileSync(outPath, html, 'utf8');
    // Sanity check: did any unresolved Mustache placeholders remain?
    const unresolved = (html.match(/\{\{[^}]+\}\}/g) || []).filter(m => !m.includes('pageNumber') && !m.includes('totalPages'));
    const status = unresolved.length === 0 ? 'ok ' : `WARN(${unresolved.length} unresolved)`;
    console.log(`[${status}] ${name} -> ${outPath}`);
    okCount++;
  } catch (e) {
    console.error(`[fail] ${name}: ${e.message}`);
    failCount++;
  }
}
console.log(`\nRendered ${okCount}/${list.length} templates (failures: ${failCount})`);
