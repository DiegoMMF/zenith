/**
 * Stub portable — generar guías HTML desde markdown.
 * Copiar a tools/build-doc-html.mjs y completar DOCS[].
 * Uso: node tools/build-doc-html.mjs
 *
 * Política: .md = contrato; .html = guía operativa.
 * Tras enriquecer HTML a mano: generate: false en la entrada DOCS.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const ASSETS_DIR = 'docs/assets/doc-html';
const INDEX_PATH = 'docs/index.html';

/** @type {{ src: string, title: string, subtitle: string, badge: string, variant?: string, persist?: string, generate?: boolean }[]} */
const DOCS = [
  // Ejemplo:
  // {
  //   src: 'docs/ops/runbook.md',
  //   title: 'Runbook',
  //   subtitle: 'Pasos operativos',
  //   badge: 'Ops',
  //   variant: 'checklist',
  //   persist: 'runbook',
  // },
];

function htmlPathFor(mdPath) {
  return mdPath.replace(/\.md$/, '.html');
}

function slugify(text) {
  return String(text)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 60);
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function assetPrefix(htmlOutPath) {
  const fromDir = path.join(ROOT, path.dirname(htmlOutPath));
  const assetsDir = path.join(ROOT, ASSETS_DIR);
  const rel = path.relative(fromDir, assetsDir).replace(/\\/g, '/');
  return (rel ? `${rel}/` : './').replace(/^(?!\.)/, './');
}

function inlineFormat(text) {
  let s = escapeHtml(text);
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  return s;
}

function mdToBody(md, docSlug = 'doc') {
  const lines = md.split('\n');
  const sections = [];
  let current = { title: 'Intro', id: 'intro', lines: [] };
  const nav = [];
  let checkSeq = 0;

  for (const line of lines) {
    const h2 = line.match(/^## (.+)/);
    if (h2) {
      if (current.lines.length || current.title !== 'Intro') sections.push(current);
      const title = h2[1].trim();
      const id = slugify(title) || `section-${sections.length}`;
      current = { title, id, lines: [] };
      nav.push({ id, title, level: 2 });
      continue;
    }
    const h3 = line.match(/^### (.+)/);
    if (h3) {
      current.lines.push({ type: 'h3', text: h3[1] });
      nav.push({ id: slugify(h3[1]), title: h3[1], level: 3 });
      continue;
    }
    if (line.match(/^# /)) continue;
    current.lines.push({ type: 'raw', text: line });
  }
  if (current.lines.length) sections.push(current);

  let html = '';
  let hasChecklists = false;
  for (const sec of sections) {
    html += `<section class="section" id="${sec.id}"><h2>${inlineFormat(sec.title)}</h2>\n`;
    let i = 0;
    const items = sec.lines;
    while (i < items.length) {
      const item = items[i];
      if (item.type === 'h3') {
        html += `<h3 id="${slugify(item.text)}">${inlineFormat(item.text)}</h3>\n`;
        i++;
        continue;
      }
      const line = item.text;
      const fence = line.match(/^(\s*)```(\w*)\s*$/);
      if (fence) {
        const indent = fence[1].length;
        const lang = fence[2];
        const code = [];
        i++;
        while (i < items.length && !items[i].text.match(/^\s*```\s*$/)) {
          let cl = items[i].text;
          if (indent && cl.startsWith(' '.repeat(indent))) cl = cl.slice(indent);
          code.push(cl);
          i++;
        }
        i++;
        if (lang === 'mermaid') {
          html += `<div class="flow-diagram"><pre class="mermaid">${escapeHtml(code.join('\n'))}</pre></div>\n`;
        } else {
          html += `<pre${lang ? ` data-lang="${escapeHtml(lang)}"` : ''}>${escapeHtml(code.join('\n'))}</pre>\n`;
        }
        continue;
      }
      if (line.match(/^- \[[ xX]\] /)) {
        hasChecklists = true;
        html += '<ul class="checklist">\n';
        while (i < items.length && items[i].text.match(/^- \[[ xX]\] /)) {
          const m = items[i].text.match(/^- \[([ xX])\] (.+)/);
          const cid = `${docSlug}-${sec.id}-c${checkSeq++}`;
          html += `<li><label class="${m[1] !== ' ' ? 'done' : ''}"><input type="checkbox" id="${cid}"${m[1] !== ' ' ? ' checked' : ''}><span>${inlineFormat(m[2])}</span></label></li>\n`;
          i++;
        }
        html += '</ul>\n';
        continue;
      }
      if (line.match(/^[-*] /)) {
        html += '<ul>\n';
        while (i < items.length && items[i].text.match(/^[-*] /)) {
          html += `<li>${inlineFormat(items[i].text.replace(/^[-*] /, ''))}</li>\n`;
          i++;
        }
        html += '</ul>\n';
        continue;
      }
      if (line.trim() && line.trim() !== '---') html += `<p>${inlineFormat(line)}</p>\n`;
      i++;
    }
    html += '</section>\n';
  }
  return { html, nav, hasChecklists };
}

function enhanceChecklist(html, persist) {
  return html.replace(
    /<ul class="checklist">/g,
    `<div class="progress-bar"><span style="width:0%"></span></div><p data-progress-label class="meta">Progreso: 0%</p><ul class="checklist" data-persist="${persist}">`,
  );
}

function wrapPage(doc, htmlOut, body, nav, extras = '') {
  const assets = assetPrefix(htmlOut);
  const mdBasename = path.basename(doc.src);
  const mdExists = fs.existsSync(path.join(ROOT, doc.src));
  const indexRel = path.relative(path.dirname(path.join(ROOT, htmlOut)), path.join(ROOT, INDEX_PATH)).replace(/\\/g, '/');
  const navHtml = nav
    .map((n) => `<a class="${n.level === 3 ? 'nav-h3' : ''}" href="#${n.id}">${escapeHtml(n.title)}</a>`)
    .join('\n');
  const contract = mdExists
    ? `<a href="./${mdBasename}">Contrato .md</a>`
    : `<span>Guía HTML</span>`;
  const footer = mdExists
    ? `Contrato: <a href="./${mdBasename}"><code>${escapeHtml(mdBasename)}</code></a> — guía expandida (humanos y agentes).`
    : `Guía expandida (humanos y agentes). Sin <code>.md</code> hermano.`;

  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(doc.title)}</title>
  <link rel="stylesheet" href="${assets}styles.css">
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <p class="meta"><a href="${indexRel.startsWith('.') ? indexRel : './' + indexRel}">← Índice</a> · ${contract}</p>
      <span class="meta">${escapeHtml(doc.badge)}</span>
      <h1>${escapeHtml(doc.title)}</h1>
      <p class="meta">${escapeHtml(doc.subtitle)}</p>
      <nav>${navHtml}</nav>
    </aside>
    <main class="main">
      <header class="hero" id="top">
        <h2>${escapeHtml(doc.title)}</h2>
        <p>${escapeHtml(doc.subtitle)}</p>
      </header>
      ${extras}
      ${body}
      <footer class="footer-note">${footer}</footer>
    </main>
  </div>
  <script src="${assets}app.js"></script>
</body>
</html>`;
}

fs.mkdirSync(path.join(ROOT, ASSETS_DIR), { recursive: true });

for (const doc of DOCS) {
  const htmlOut = htmlPathFor(doc.src);
  if (doc.generate === false) {
    console.warn('⊘ skip (HTML a mano):', htmlOut);
    continue;
  }
  const mdPath = path.join(ROOT, doc.src);
  if (!fs.existsSync(mdPath)) {
    console.warn('⊘ skip (sin .md):', doc.src);
    continue;
  }
  const md = fs.readFileSync(mdPath, 'utf8');
  const slug = slugify(path.basename(doc.src, '.md')) || 'doc';
  const { html, nav, hasChecklists } = mdToBody(md, slug);
  const persist = doc.persist || (hasChecklists ? slug : null);
  let body = persist && html.includes('class="checklist"') ? enhanceChecklist(html, persist) : html;
  let extras = '';
  if (doc.variant === 'checklist' || (doc.variant !== 'wizard' && hasChecklists)) {
    extras =
      '<div class="banner warn"><strong>Checklist interactivo</strong> Progreso en este navegador (localStorage).</div>';
  }
  if (doc.variant === 'wizard') {
    extras =
      '<div class="banner info"><strong>Guía paso a paso</strong> Seguí el orden de las secciones.</div>';
  }
  fs.mkdirSync(path.dirname(path.join(ROOT, htmlOut)), { recursive: true });
  fs.writeFileSync(path.join(ROOT, htmlOut), wrapPage(doc, htmlOut, body, nav, extras));
  console.log('✓', htmlOut);
}

const indexAssets = assetPrefix(INDEX_PATH);
const cards = DOCS.map((d) => {
  const href = path.relative(path.dirname(INDEX_PATH), htmlPathFor(d.src)).replace(/\\/g, '/');
  return `<a class="doc-card" href="${href}"><span class="badge">${escapeHtml(d.badge)}</span><h3>${escapeHtml(d.title)}</h3><p>${escapeHtml(d.subtitle)}</p></a>`;
}).join('\n');

fs.writeFileSync(
  path.join(ROOT, INDEX_PATH),
  `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Documentación HTML</title>
  <link rel="stylesheet" href="${indexAssets}styles.css">
  <style>
    .index-main { max-width: 1100px; margin: 0 auto; padding: 2.5rem; }
    .doc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; margin-top: 1.5rem; }
    .doc-card { display: block; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; text-decoration: none; color: inherit; box-shadow: var(--shadow); }
    .doc-card:hover { border-color: var(--accent); text-decoration: none; }
    .doc-card h3 { margin: 0.5rem 0 0.25rem; }
    .badge { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: var(--accent); background: var(--accent-soft); padding: 0.2rem 0.5rem; border-radius: 4px; }
  </style>
</head>
<body>
  <main class="index-main">
    <header class="hero">
      <h2>Documentación HTML</h2>
      <p>Guías operativas. Regenerar: <code>node tools/build-doc-html.mjs</code></p>
    </header>
    <div class="doc-grid">${cards}</div>
  </main>
</body>
</html>`,
);
console.log('✓', INDEX_PATH);
