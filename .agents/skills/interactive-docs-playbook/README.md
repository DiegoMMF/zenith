# Interactive Docs Playbook

> [!WARNING]
> **DEPRECADO:** Este skill está obsoleto para la mayoría de proyectos.
> 
> **Usar en su lugar:** [`rich-markdown-playbook`](../rich-markdown-playbook/) — Markdown enriquecido nativo de GitHub (alerts, Mermaid, collapsibles) sin toolchain.
> 
> **¿Por qué?** HTML no se ve en GitHub, requiere servidor local, y es menos portable que Markdown nativo.

---

Skill portable para migrar documentación Markdown larga a **guías HTML interactivas**, con política **contrato vs guía** en `AGENTS.md`.

⚠️ **Solo usar si:**
- Necesitas interactividad que Markdown no soporta (tabs con JS, progress bars persistentes)
- Ya tienes infraestructura HTML establecida
- El proyecto se visualiza vía GitHub Pages o servidor dedicado

## Migrar a Markdown enriquecido

Ver [`rich-markdown-playbook/ROLLBACK.md`](../rich-markdown-playbook/ROLLBACK.md) para revertir HTML a Markdown.

## Usar en este repo (no recomendado)

El agente debe leer [`SKILL.md`](./SKILL.md) y seguir las fases A→E.

## Copiar a otro proyecto

```bash
# Desde la raíz del repo destino (ajustá ORIGIN)
ORIGIN=/path/to/traslamarket/.agents/skills/interactive-docs-playbook
mkdir -p .agents/skills
cp -R "$ORIGIN" .agents/skills/interactive-docs-playbook

# Opcional: espejo Claude
mkdir -p .claude/skills
ln -sfn ../../.agents/skills/interactive-docs-playbook .claude/skills/interactive-docs-playbook
```

Luego, en el chat del otro agente:

```text
Leé .agents/skills/interactive-docs-playbook/SKILL.md y ejecutá el playbook
completo en este repositorio (inventario → toolchain → conversión →
enriquecimiento → AGENTS.md). Usá los templates del skill.
```

## Contenido

| Ruta | Rol |
| --- | --- |
| `SKILL.md` | Hoja de ruta para el agente |
| `templates/AGENTS-docs-section.md` | Bloque normativo para `AGENTS.md` |
| `templates/build-doc-html.mjs` | Stub del generador |
| `templates/styles.css` / `app.js` | Assets compartidos |
| `templates/sample-guide.html` | Ejemplo enriquecido |

## Nota

Los templates son **genéricos**. Si el destino ya tiene un generador más maduro, reutilizalo y aplicá solo la política + criterios de enriquecimiento del `SKILL.md`.
