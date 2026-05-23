#!/usr/bin/env node
// Renders each .rendered.html in preview/ to a PNG for quick visual QA
import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';
const __dirname = path.dirname(url.fileURLToPath(import.meta.url));
const PUPPETEER_PATH = '/Users/sandy/Downloads/Claude Code/client-data/pilani-group/pitch-deck/node_modules/puppeteer';
const puppeteer = (await import(path.join(PUPPETEER_PATH, 'lib', 'esm', 'puppeteer', 'puppeteer.js'))).default;

const previewDir = path.join(__dirname, 'preview');
const files = fs.readdirSync(previewDir).filter(f => f.endsWith('.rendered.html'));

const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
for (const f of files) {
  const name = f.replace('.rendered.html', '');
  const page = await browser.newPage();
  await page.setViewport({ width: 794, height: 1123, deviceScaleFactor: 1.5 }); // A4 @ ~96dpi
  await page.goto('file://' + path.join(previewDir, f), { waitUntil: 'networkidle0' });
  await page.screenshot({ path: path.join(previewDir, `${name}.page1.png`), fullPage: false });
  await page.close();
  console.log('shot', name);
}
await browser.close();
