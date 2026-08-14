# Rich Markdown Playbook

Skill portable para enriquecer documentación Markdown con **features nativas de GitHub**: alerts, Mermaid, collapsibles, tables, y navegación cruzada. Sin toolchain externo, 100% portable.

## Usar en este repo

El agente debe leer [`SKILL.md`](./SKILL.md) y seguir las fases A→E.

## Copiar a otro proyecto

```bash
# Desde la raíz del repo destino
ORIGIN=/path/to/meridian/.agents/skills/rich-markdown-playbook
mkdir -p .agents/skills
cp -R "$ORIGIN" .agents/skills/rich-markdown-playbook

# Opcional: espejo Claude
mkdir -p .claude/skills
ln -sfn ../../.agents/skills/rich-markdown-playbook .claude/skills/rich-markdown-playbook
```

Luego, en el chat del otro agente:

```text
Leé .agents/skills/rich-markdown-playbook/SKILL.md y ejecutá el playbook
completo en este repositorio (inventario → conversión → enriquecimiento →
gobernanza). Usá Markdown nativo de GitHub, sin toolchain.
```

## Contenido

| Ruta | Rol |
| --- | --- |
| `SKILL.md` | Hoja de ruta completa para el agente |
| `ROLLBACK.md` | Guía para revertir de HTML a Markdown |

## Ventajas vs HTML

| Aspecto | HTML | Markdown enriquecido |
|---------|------|---------------------|
| Visualización en GitHub | ❌ Solo código | ✅ Renderizado nativo |
| Servidor local | ❌ Necesario | ✅ No necesario |
| Portabilidad | ❌ Solo HTML | ✅ GitLab, Obsidian, VS Code |
| Agentes | ✅ Leen bien | ✅ Parseo más simple |
| Edición | ❌ HTML manual | ✅ Texto plano / GitHub UI |
| Mantenimiento | ❌ Toolchain | ✅ Archivos .md simples |

## Features soportadas

- ✅ **GitHub Alerts** (5 tipos: NOTE, TIP, IMPORTANT, WARNING, CAUTION)
- ✅ **Mermaid diagrams** (flowchart, sequence, gantt, etc.)
- ✅ **Collapsibles** con `<details>`
- ✅ **Tables** con emojis para estados
- ✅ **Task lists** interactivas
- ✅ **Syntax highlight** en code blocks
- ✅ **Enlaces cruzados** dentro del proyecto
- ✅ **Footnotes** y referencias

## Nota

Esta skill reemplaza `interactive-docs-playbook` para proyectos que prefieren Markdown nativo sobre HTML. Ambas skills pueden coexistir: usa `ROLLBACK.md` si necesitas volver atrás.
