# Lex MX 🇲🇽 — Leyes Federales de México en Markdown

> Toda la legislación federal mexicana vigente, en Markdown limpio, versionada
> con git y **actualizada automáticamente cada día** desde la fuente oficial.
>
> *All Mexican federal law as clean, AI-ready Markdown — git-versioned and
> auto-updated daily.*

![Leyes](https://img.shields.io/badge/leyes-316-1f6feb)
![Actualización](https://img.shields.io/badge/actualización-diaria-2da44e)
![Fuente](https://img.shields.io/badge/fuente-DOF%20%2F%20Diputados-555)
![Texto](https://img.shields.io/badge/texto-dominio%20público-2da44e)
![Pipeline](https://img.shields.io/badge/pipeline-MIT-1f6feb)

## Úsalo con tu IA — una sola línea

Las IAs alucinan artículos y citan leyes ya derogadas. Este repo es el texto
**vigente, fechado y citable**. Lo único que tienes que escribirle a tu IA es:

> *Mi caso/pregunta es: \<lo que sea\>. Usa este repo de leyes federales mexicanas
> para responder con base en el texto vigente, no de memoria: https://github.com/ingteranalvarez/lex-mx*

Eso es todo. Cualquier IA con navegación (ChatGPT Plus/Team, Claude.ai,
Gemini, Perplexity, Cursor) lee el archivo [`llms.txt`](./llms.txt) del repo,
identifica la ley relevante en [`catalog.json`](./catalog.json), abre el `.md`
correspondiente desde `raw.githubusercontent.com`, y cita textualmente con la
fecha de última reforma. Sin intervención adicional tuya.

**Por si tu IA no soporta navegación** (ChatGPT gratis sin browsing): abre la
ley que necesites desde `leyes/<CLAVE>.md` en GitHub, copia el contenido y
pégalo en el chat. El listado de claves está en `catalog.json`. Las más usadas:

| Clave | Ley |
|---|---|
| `CPEUM` | Constitución Política |
| `CFF` | Código Fiscal de la Federación |
| `LISR` | Ley del ISR |
| `LIVA` | Ley del IVA |
| `LIEPS` | Ley del IEPS |
| `LFT` | Ley Federal del Trabajo |
| `LGSM` | Ley General de Sociedades Mercantiles |

**Para usar el repo como contexto persistente** (Claude Projects, ChatGPT
Custom GPTs, Cursor): `git clone` localmente o sube el `.md` de la ley
como archivo fijo. `git pull` cada semana mantiene tu copia al día.

## Por qué hice esto

Estudio una maestría y llevo derecho fiscal. Trabajando casos me la pasaba
peleando con las leyes en **PDF**: copiar y pegar artículos, perder el formato,
y nunca saber con certeza si la versión que tenía era la vigente.

Me di cuenta de que ese hueco no era solo mío: cualquiera que construya algo
sobre la ley mexicana —una app fiscal, un asistente con IA, un análisis de
reformas— empieza parseando esos mismos PDFs a mano. Proyectos como
[`legalize`](https://github.com/code4romania/legalize) cubren decenas de países;
México no estaba.

Así que lo cubrí. Pasé toda la ley federal a Markdown limpio y monté un proceso
que la mantiene **actualizada sola, todos los días**. Esto es el resultado.

## Qué hay aquí

- **316 leyes y códigos federales vigentes**: la Constitución, todos los
  códigos, las leyes federales y los reglamentos del Congreso.
- **Una ley por archivo** en [`leyes/`](leyes/), Markdown con estructura
  semántica (`#` ley · `##`/`###` títulos y capítulos · `**Artículo N.-**`).
- **Versionado con git** — el diferenciador real:

```bash
git log --oneline -- leyes/LIVA.md      # historia de reformas de la Ley del IVA
git diff HEAD~1 -- leyes/CFF.md         # qué cambió exactamente en la última reforma
```

Ver qué cambió entre versiones de una ley, artículo por artículo, no existía en
abierto para México. Ahora lo hace `git`, gratis, para siempre.

## Para quién

| Si eres… | Lo usas para… |
|---|---|
| Dev de una app legal/fiscal | Alimentar tu RAG sin parsear PDFs |
| Builder de un asistente con IA | Pegar texto limpio directo a un LLM |
| Contador / abogado / fiscalista | `git diff` de una reforma; texto citable |
| Investigador / periodista de datos | Dataset legislativo reproducible y fechado |
| Entrenar / evaluar modelos | Corpus jurídico en español, estructurado |

## Empezar

```bash
git clone https://github.com/ingteranalvarez/lex-mx.git

# o una sola ley, sin clonar
curl -O https://raw.githubusercontent.com/ingteranalvarez/lex-mx/main/leyes/LIVA.md
```

Más consultadas:
[Constitución](leyes/CPEUM.md) · [CFF](leyes/CFF.md) · [LISR](leyes/LISR.md) ·
[LIVA](leyes/LIVA.md) · [LIEPS](leyes/LIEPS.md) · [LFT](leyes/LFT.md) ·
[Código Penal](leyes/CPF.md) · [Código Civil](leyes/CCF.md)
— índice completo en [`catalog.json`](catalog.json), esquema en
[`SCHEMA.md`](SCHEMA.md).

## Cómo se mantiene actualizado

Un [GitHub Action](.github/workflows/update.yml) corre **todos los días**:
lee el índice oficial de la Cámara de Diputados, detecta qué leyes cambiaron de
"última reforma", reconvierte solo esas y hace **un commit por ley reformada**
(`reforma: LIVA — DOF 2026-…`). La mayoría de los días no cambia nada. El
`git log` es, literalmente, la bitácora de reformas de México.

## Fuente y base legal

Fuente: PDFs oficiales de la
[Cámara de Diputados](https://www.diputados.gob.mx/LeyesBiblio/). El texto de
las leyes publicado en el DOF es de **dominio público** (Art. 14, Ley Federal
del Derecho de Autor): su redistribución está permitida. El valor agregado aquí
es el formato, la estructura y el mantenimiento.

## Aviso

Conversión automatizada **best-effort**. Puede contener artefactos de la
extracción de PDF. **No es una fuente oficial.** Para efectos legales consulta
siempre el texto publicado en el [DOF](https://www.dof.gob.mx/). Sin garantía.

## Contribuir

¿Un artículo mal extraído, un encabezado raro? Abre un
[issue](https://github.com/ingteranalvarez/lex-mx/issues) con la ley y la línea,
o manda un PR al normalizador (`pipeline/`).

## Licencia

Texto de las leyes: **dominio público**. Código del pipeline: **MIT**.

---

<sub>leyes de México · legislación mexicana · Mexican law dataset · Constitución ·
Código Fiscal · Ley del IVA · ISR · legislación en Markdown · corpus jurídico
español · RAG legal · LLM legal México · diputados.gob.mx · DOF</sub>
