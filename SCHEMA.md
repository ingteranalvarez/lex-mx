# Esquema de datos

## Archivos de ley — `leyes/<slug>.md`

Cada ley es un Markdown con frontmatter YAML:

```yaml
---
type: ley-federal
sigla: LIVA                        # sigla oficial de la Cámara de Diputados
slug: LIVA                         # nombre de archivo (= sigla, o slug legible si es numérica)
titulo: "Ley del Impuesto al Valor Agregado"
ultima_reforma: "2021-11-12"       # ISO YYYY-MM-DD — fecha DOF de la última reforma
fuente: "DOF / Cámara de Diputados"
fuente_pdf: https://www.diputados.gob.mx/LeyesBiblio/pdf/LIVA.pdf
articulos: 99                      # conteo aproximado de artículos (heurístico)
tags: [ley, federal]
---
```

Cuerpo:

```
# <Título de la ley>
> Última reforma publicada DOF dd-mm-aaaa

<preámbulo: decreto de promulgación>

## TITULO PRIMERO            ← h2: LIBRO / TÍTULO / TRANSITORIOS
### CAPITULO I               ← h3: CAPÍTULO
#### SECCION PRIMERA         ← h4: SECCIÓN

**Artículo 1o.-** Texto del artículo…
I.- fracción…
a) inciso…
```

### Reglas de estructura

| Elemento | Markdown | Origen |
|---|---|---|
| Ley | `# Título` | título del catálogo |
| Libro / Título | `##` | línea en mayúsculas `LIBRO`/`TÍTULO` |
| Capítulo | `###` | línea `CAPÍTULO` |
| Sección | `####` | línea `SECCIÓN` |
| Artículo | `**Artículo N.-**` en negritas | inicio de línea |
| Fracción / inciso | `I.-`, `a)` en línea con su texto | re-unido del PDF |

## `catalog.json`

Array de objetos, uno por ley vigente en el índice:

```json
{
  "sigla": "LIVA",
  "slug": "LIVA",
  "titulo": "Ley del Impuesto al Valor Agregado",
  "pdf_url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LIVA.pdf",
  "ref_url": "https://www.diputados.gob.mx/LeyesBiblio/ref/liva.htm",
  "ultima_reforma": "2021-11-12"
}
```

## `state.json`

Mapa `{slug: ultima_reforma}` del último estado convertido. El pipeline
reconvierte una ley solo si su `ultima_reforma` en `catalog.json` difiere de
`state.json`. Así los commits quedan atómicos por reforma.

## `errors.log`

Una línea por ley que falló en el último run: `slug \t pdf_url \t error`.
Conversión best-effort: una ley que falla no aborta el resto.
