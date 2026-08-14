## Documentación: contrato (Markdown) vs guía (HTML)

El proyecto distingue formatos por **función**, no por especie (humano vs agente):

| Función | Formato | Rol |
| --- | --- | --- |
| Contrato normativo | `.md` corto | Reglas duras, grepeables y citables; skills, PRs, CI |
| Guía operativa / narrativa | `.html` enriquecido | Procedimiento expandido (tabs, checklists, diagramas); humanos **y** agentes en ops/QA |

El markdown no es “para agentes”: es el **contrato estable**. El HTML no es “solo para humanos”: en runbooks/E2E/go-live un agente **puede y debe** leer la guía HTML.

**Regla fuerte:** guías nuevas (runbooks, E2E, demos, checklists, manuales, stakeholders) viven en **HTML**, no en markdown de cientos de líneas. Guía solo HTML OK si no hay reglas que citar. Si hay reglas: `foo.md` + `foo.html`.

**Índice canónico (mantener actualizado):** [`docs/index.html`](docs/index.html). Al crear/renombrar/borrar docs → `node tools/build-doc-html.mjs` y commitear el índice.

### Regenerar / enriquecer

```bash
node tools/build-doc-html.mjs
```

- MD registrado sin `generate: false` → regenera el `.html` hermano.
- HTML enriquecido a mano → `generate: false` en `DOCS` (no pisar).
- El script regenera el catálogo completo en `docs/index.html`.
- Commitear `.html` (+ `.md` si hay contrato) **y** `docs/index.html` tras altas/bajas.
- Preview: `npx serve docs -p 4321`.
- Las guías usan **dark theme fijo** desde `docs/assets/doc-html/{styles.css,app.js}`: no agregar toggle, variantes claras ni reglas basadas en `prefers-color-scheme`.
- Todo cambio al CSS/JS compartido debe sincronizarse con los templates equivalentes del playbook para que las guías nuevas hereden el mismo runtime.

### Anti-patrones (docs)

- Procedimiento solo en markdown largo.
- Regla normativa solo en HTML sin contrato `.md`.
- Regenerar y sobrescribir HTML enriquecido.
- Índices que apuntan al `.md` largo como superficie de lectura operativa.
- Docs nuevos o borrados sin regenerar `docs/index.html`.
- Paletas claras, estilos de tema inline o selectores que cambien el tema según el sistema operativo.
- Cambiar los assets compartidos sin actualizar los templates equivalentes del playbook.
