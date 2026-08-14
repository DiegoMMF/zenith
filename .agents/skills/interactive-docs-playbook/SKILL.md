---
name: interactive-docs-playbook
description: >-
  [DEPRECATED] Use rich-markdown-playbook instead. HTML guides require local server,
  don't render on GitHub, and are less portable than native Markdown with alerts.
  Only use if you need JS interactivity (tabs, persist) or have existing HTML infrastructure.
---

# Interactive Docs Playbook — MD largo → HTML operable

> [!WARNING]
> **SKILL DEPRECADO**
> 
> **Usar en su lugar:** [`rich-markdown-playbook`](../rich-markdown-playbook/) 
> 
> Razones:
> - ❌ HTML no se renderiza en GitHub (solo código fuente)
> - ❌ Requiere servidor local o Pages para visualizar
> - ❌ Menos portable que Markdown (no funciona en GitLab/Obsidian/VS Code sin setup)
> - ✅ Markdown nativo de GitHub soporta **alerts, Mermaid, collapsibles** desde 2023
> 
> **Solo usar HTML si:**
> - Necesitas tabs interactivos con JS
> - Necesitas progress bars persistentes en localStorage
> - Ya tienes infraestructura HTML establecida y no vale la pena migrar

---

Hoja de ruta **portable** para agentes. Destilada de migraciones reales: no asume
TraslaMarket. Objetivo: reemplazar markdowns de cientos de líneas por **guías HTML
enlazadas, interactivas y agradables**, con política clara en `AGENTS.md`.

**Prompt de arranque (usuario → agente):**

> Leé `.agents/skills/interactive-docs-playbook/SKILL.md` y seguí el playbook
> completo en este repo: inventario → toolchain → conversión → enriquecimiento →
> gobernanza en AGENTS.md. Usá los templates del skill. No dejes guías largas
> solo en Markdown.

---

## 1. Problema que resuelve

| Antes | Después |
| --- | --- |
| Runbooks / E2E / demos en `.md` de 300–600 líneas | Guías `.html` con sidebar, tabs, checklists, diagramas |
| “MD para agentes, HTML para humanos” (rígido) | Distinción por **función**: contrato vs guía |
| Docs ilegibles en operación | Índice HTML + enlaces cruzados + progreso persistente |

Los agentes **sí** se benefician del HTML en tareas operativas. El MD corto sigue
siendo el contrato grepeable para skills, PRs y CI.

---

## 2. Principio normativo (función, no especie)

| Función | Formato | Quién lo usa |
| --- | --- | --- |
| **Contrato normativo** | `.md` corto | Skills, PRs, CI, reglas duras citables |
| **Guía operativa / narrativa** | `.html` enriquecido | Humanos **y** agentes en ops/QA/demos |

Reglas:

1. Guía nueva (runbook, E2E, checklist go-live, manual, demo, stakeholder) → **HTML**.
2. Puede ser **solo HTML** si no hay reglas que skills deban citar.
3. Si hay reglas duras → par `foo.md` (contrato breve) + `foo.html` (guía).
4. Tras enriquecer HTML a mano → `generate: false` en el generador para no pisarlo.

**Anti-patrones:**

- Dejar procedimiento solo en MD largo.
- Dejar regla normativa solo en HTML sin contrato `.md`.
- Regenerar y pisar HTML enriquecido sin `generate: false`.
- Confundir “audiencia humana” con “formato HTML”.

Plantilla lista para pegar: [`templates/AGENTS-docs-section.md`](templates/AGENTS-docs-section.md).

---

## 3. Fase A — Inventario

Listar todos los `.md` bajo `docs/` (u otra raíz documentada). Clasificar cada uno:

| Clase | Criterio | Acción |
| --- | --- | --- |
| `GUIA` | Procedimiento, narrativa, checklist operativo, >~80–100 líneas orientadas a “hacer” | Convertir a HTML (+ enriquecer) |
| `CONTRATO` | Reglas duras, ADR, env vars, specs citables, plantillas cortas | Dejar en MD (opcional: HTML hermano si ayuda a ops) |
| `HISTORICO` | Research LLM, dumps, pre-acuerdo archivado | No migrar (o museo aparte) |
| `META` | README de assets, este playbook | Dejar en MD |

**Salida:** tabla `path | líneas | clase | prioridad`. Priorizar guías de uso diario (deploy, QA, onboarding).

---

## 4. Fase B — Toolchain

1. Copiar templates del skill al repo destino:

```bash
mkdir -p docs/assets/doc-html tools
cp .agents/skills/interactive-docs-playbook/templates/styles.css docs/assets/doc-html/
cp .agents/skills/interactive-docs-playbook/templates/app.js docs/assets/doc-html/
cp .agents/skills/interactive-docs-playbook/templates/build-doc-html.mjs tools/
```

2. Registrar entradas en el array `DOCS` de `tools/build-doc-html.mjs` (`src`, `title`, `subtitle`, `badge`, `variant`, `persist` opcional).

3. Ejecutar:

```bash
node tools/build-doc-html.mjs
```

4. Previsualizar: `npx serve docs -p 4321` → abrir `docs/index.html`.

**Variants útiles del stub:** `report`, `checklist`, `wizard`, `technical` (extender según el proyecto).

---

## 5. Fase C — Conversión

Para cada `GUIA`:

1. Asegurar `.md` fuente (o crear stub si solo existirá HTML).
2. Registrar en `DOCS` y generar `.html` hermano.
3. Actualizar índices: regenerar [`docs/index.html`](docs/index.html) con `node tools/build-doc-html.mjs` (catálogo completo; **debe** mantenerse al día) y apuntar skills/`AGENTS.md` a la **guía HTML** como superficie de lectura.
4. Decidir destino del MD:
   - **Fuente regenerable:** conservar MD largo, regenerar HTML hasta enriquecer.
   - **Contrato breve + HTML a mano:** recortar MD; `generate: false`.
   - **HTML-only:** borrar MD tras validar HTML; footer “sin .md hermano”.

Commits: preferir `docs:` aparte; si hay par generado, commitear `.md` + `.html` juntos.

---

## 6. Fase D — Enriquecimiento (no solo “cambio de formato”)

Cada guía enriquecida debe cumplir **≥ 2** de:

1. **Interacción** — tabs, checklist `data-persist`, `<details>`, botón Copiar.
2. **Jerarquía visual** — `status-matrix`, `phase-grid`, `timeline`, `url-grid`, banners.
3. **Diagrama / flujo** — Mermaid (`pre.mermaid`) o esquema HTML claro.

### Catálogo de patrones (CSS/JS ya en templates)

| Patrón | Uso típico |
| --- | --- |
| `.tabs` / `.tab-panel` | Local vs staging; first-time vs subsequent |
| `.checklist[data-persist]` + progress | Go-live, QA, readiness |
| `.status-matrix` / `.status-card.ok\|warn\|danger` | Semáforos de blockers |
| `.phase-grid` / `.phase-card` | Fases de un plan |
| `.timeline` + `data-step` | Flujos paso a paso |
| `details` / `summary` | Errores comunes, riesgos |
| `.url-grid` / `.url-card` | Links de entornos |
| `.decision-tree` | “¿Toca X? → Y” |
| `.flow-diagram` + `pre.mermaid` | Pipelines, deploy |
| `.copy-btn` (auto en `app.js`) | Comandos copiables |

**Workflow de enriquecimiento:**

1. Generar HTML base desde MD (parser arreglado: fences indentados, IDs únicos).
2. Insertar bloque de enriquecimiento tras el `hero` (y/o reestructurar secciones clave).
3. Marcar `generate: false` en `DOCS` para esa entrada.
4. Verificar en navegador: tabs, persist, copy, mermaid.

Referencia de esqueleto: [`templates/sample-guide.html`](templates/sample-guide.html).

---

## 7. Fase E — Gobernanza

1. Pegar/adaptar [`templates/AGENTS-docs-section.md`](templates/AGENTS-docs-section.md) en `AGENTS.md` (o `CLAUDE.md` / equivalente).
2. Actualizar índice canónico: `node tools/build-doc-html.mjs` → `docs/index.html` (guías `.html` + contratos `.md`; mantener siempre al día).
3. Añadir anti-patrones de documentación.
4. Enlaces cruzados entre guías relacionadas (`url-grid` o links en callouts).
5. Documentar en el README del repo: `node tools/build-doc-html.mjs` + `docs/index.html`.

---

## 8. Criterios de aceptación

- [ ] Inventario clasificado (GUIA / CONTRATO / HISTORICO).
- [ ] `docs/assets/doc-html/{styles.css,app.js}` presentes.
- [ ] `tools/build-doc-html.mjs` regenera `docs/index.html` con el catálogo completo (guías + contratos).
- [ ] Tras alta/baja de docs se committea el índice actualizado.
- [ ] Guías prioritarias en HTML con ≥2 patrones de enriquecimiento.
- [ ] Guías enriquecidas a mano tienen `generate: false`.
- [ ] `AGENTS.md` incluye contrato vs guía + anti-patrones.
- [ ] Enlaces del README/AGENTS apuntan a HTML para lectura operativa.
- [ ] Smoke: `npx serve docs -p 4321` — tabs, checklist persist, copy en `<pre>`.

---

## 9. Orden de commits sugerido

1. `chore:` / `docs:` toolchain (assets + build stub).
2. `docs:` conversión de un lote de guías.
3. `docs:` enriquecimiento interactivo + `generate: false`.
4. `docs:` sección AGENTS + índices.

---

## 10. Si el repo es TraslaMarket (referencia opcional)

Implementación madura (no copiar a ciegas; preferir templates del skill):

- Generador: `tools/build-doc-html.mjs`
- Assets: `docs/assets/doc-html/`
- Política: sección *contrato vs guía* en `AGENTS.md`
- Ejemplos ricos: `docs/06_operations/go-live-checklist.html`, `docs/08_legal/02_QA_GUIA_LEGAL_FASE_1.html`

---

## Checklist rápido del agente

```text
[ ] Leer este SKILL.md completo
[ ] Inventario de docs/
[ ] Copiar templates → docs/assets/doc-html + tools/build-doc-html.mjs
[ ] Registrar DOCS[] y generar
[ ] Convertir GUIAs prioritarias
[ ] Enriquecer (≥2 patrones) + generate:false
[ ] Actualizar AGENTS.md + índices
[ ] Smoke en navegador
[ ] Commits docs: limpios
```
