#!/usr/bin/env python3
"""
Convierte las leyes del catálogo a Markdown.

Flujo por ley:  PDF oficial → pdftotext → limpieza → Markdown + frontmatter.

Detección de cambios: si state.json[slug] == ultima_reforma y el .md existe,
se salta. Así el run diario solo reprocesa leyes reformadas y los commits
quedan atómicos por reforma.

Uso:
  python3 pipeline/build.py                 # todas las que cambiaron
  python3 pipeline/build.py --limit 3       # primeras 3 (prueba)
  python3 pipeline/build.py --only LIVA,CFF # solo esas siglas/slugs
  python3 pipeline/build.py --force         # ignora state.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"
STATE = ROOT / "state.json"
LEYES = ROOT / "leyes"
ERRORS = ROOT / "errors.log"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) lex-mx/1.0 (+github.com/ingteranalvarez/lex-mx)"

# --- Líneas de cabecera/pie que pdftotext repite en cada página ---
CRUFT = [
    re.compile(r"^\s*\d+\s+de\s+\d+\s*$"),                       # "12 de 128"
    re.compile(r"^\s*C[ÁA]MARA DE DIPUTADOS DEL H\.?\s*CONGRESO DE LA UNI[ÓO]N\s*$", re.I),
    re.compile(r"^\s*Secretar[íi]a General\s*$", re.I),
    re.compile(r"^\s*Secretar[íi]a de Servicios Parlamentarios\s*$", re.I),
    re.compile(r"^\s*[ÚU]ltima Reforma DOF \d{2}-\d{2}-\d{4}\s*$", re.I),
    re.compile(r"^\s*$"),  # se normaliza aparte (placeholder, ver collapse)
]
CRUFT = CRUFT[:-1]  # los blancos se tratan en el colapso, no se borran del todo

START_RE = re.compile(
    r"^\s*(Nuevo Código|Nueva Ley|NUEVA LEY|NUEVO CÓDIGO|TEXTO VIGENTE|"
    r"CONSTITUCIÓN POLÍTICA|Texto Vigente|Ley publicada|Código publicado|"
    r"Ordenamiento publicado|Reglamento publicado|Estatuto publicado|"
    r"Presupuesto publicado|Decreto publicado)",
    re.I,
)

# Encabezados estructurales. Acepta MAYÚSCULAS o Título (leyes 2024+ usan
# "Capítulo I"). Para no confundir prosa ("en el capítulo anterior..."), el
# marcador debe ir seguido SOLO de numeral romano / ordinal / dígito / ÚNICO
# y la línea completa debe ser corta.
_ORD = (r"(?:[IVXLCDM]+|\d+|[ÚU]NICO|PRELIMINAR|BIS|TER|"
        r"PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[ÉE]PTIMO|OCTAVO|NOVENO|"
        r"D[ÉE]CIMO|UND[ÉE]CIMO|DUOD[ÉE]CIMO|VIG[ÉE]SIMO|TRIG[ÉE]SIMO|"
        r"CUADRAG[ÉE]SIMO|QUINCUAG[ÉE]SIMO|"
        r"PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|S[ÉE]PTIMA|OCTAVA|NOVENA|"
        r"D[ÉE]CIMA|UND[ÉE]CIMA|DUOD[ÉE]CIMA)")


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


# Vocabulario de ordinales (sin keyword): para re-unir fragmentos partidos
# por pdftotext. NFC + sin acentos como clave → tolera NFD y faltantes.
_ORD_WORDS = (
    "PRIMERO SEGUNDO TERCERO CUARTO QUINTO SEXTO SEPTIMO OCTAVO NOVENO DECIMO "
    "UNDECIMO DUODECIMO DECIMOPRIMERO DECIMOSEGUNDO DECIMOTERCERO "
    "VIGESIMO TRIGESIMO CUADRAGESIMO QUINCUAGESIMO "
    "PRIMERA SEGUNDA TERCERA CUARTA QUINTA SEXTA SEPTIMA OCTAVA NOVENA DECIMA "
    "UNDECIMA DUODECIMA UNICO UNICA PRELIMINAR BIS TER QUATER"
).split()


def _deaccent(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                    if not unicodedata.combining(c)).upper()


_ORD_SET = {_deaccent(w) for w in _ORD_WORDS}


def fix_heading(head: str, tail: str) -> str:
    """pdftotext parte palabras en headings con tracking ('Ter cera' → 'Tercera').
    Re-une SOLO fragmentos cuyo despaciado es un ordinal conocido; preserva
    casing del original y nunca toca el keyword. Lista cerrada = seguro."""
    raw = _nfc((head + (" " + tail if tail else "")).strip())
    toks = raw.split()
    fixed: list[str] = []
    i = 0
    while i < len(toks):
        merged = None
        for span in (4, 3, 2):
            if i + span <= len(toks):
                joined = "".join(toks[i:i + span])
                if _deaccent(joined).rstrip(".°º") in _ORD_SET:
                    merged = joined
                    i += span
                    break
        if merged is not None:
            fixed.append(merged.capitalize() if merged[:1].islower()
                         or merged.istitle() else merged)
        else:
            fixed.append(toks[i])
            i += 1
    return " ".join(fixed)


def _hrule(word: str) -> re.Pattern:
    # palabra clave + (espacio + ordinal)? + resto corto, toda la línea ≤ 90.
    return re.compile(
        rf"^\s*((?:{word})(?:\s+{_ORD}[º°o]?(?:\s+{_ORD})?)?\.?)\s*(.{{0,55}})?$",
        re.I,
    )


HEADING_RULES = [
    (_hrule(r"LIBRO"), "## "),
    (re.compile(r"^\s*(T[ÍI]TULO\s+PRELIMINAR)\b\s*(.{0,55})?$", re.I), "## "),
    (_hrule(r"T[ÍI]TULO"), "## "),
    (_hrule(r"CAP[ÍI]TULO"), "### "),
    (_hrule(r"SECCI[ÓO]N"), "#### "),
    (_hrule(r"AP[ÉE]NDICE"), "## "),
    (re.compile(r"^\s*(TRANSITORIOS?)\s*$", re.I), "## "),
]

# Inicio de artículo: "Artículo 1o.-", "Artículo 25.-", "Artículo 32-A.-",
# "Artículo 25 Bis.-", "ARTÍCULO PRIMERO.-", "Artículo Único.-".
ARTICLE_RE = re.compile(
    r"^((?:ART[ÍI]CULO|Art[íi]culo)\s+"
    r"(?:\d+[ºo°]?(?:[ -][A-Za-z]+)?|[A-ZÁÉÍÓÚ][a-záéíóú]+|[IVXLC]+)"
    r"\s*\.?\s*-?\s*\.?-?)\s+",
)


def fetch_pdf(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        dest.write_bytes(r.read())


def pdf_to_text(pdf: Path) -> str:
    out = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", "-nopgbrk", str(pdf), "-"],
        capture_output=True,
        timeout=180,
    )
    if out.returncode != 0:
        raise RuntimeError(f"pdftotext rc={out.returncode}: {out.stderr.decode()[:200]}")
    return out.stdout.decode("utf-8", errors="replace")


def clean(text: str) -> str:
    lines = text.splitlines()

    # 1) Quitar cabecera/pie repetido.
    kept: list[str] = []
    for ln in lines:
        if any(rx.match(ln) for rx in CRUFT):
            continue
        kept.append(ln.rstrip())

    # 2) Recortar el preámbulo de portada hasta el primer ancla real.
    start = 0
    for i, ln in enumerate(kept[:60]):
        if START_RE.match(ln):
            start = i
            break
    body = kept[start:]

    # 3) Normalizar headings y negritas de artículo.
    out: list[str] = []
    for ln in body:
        s = ln.strip()
        h = None
        for rx, prefix in HEADING_RULES:
            m = rx.match(ln)
            if m:
                head = m.group(1).strip()
                tail = (m.group(2) or "").strip() if m.lastindex and m.lastindex >= 2 else ""
                h = f"\n{prefix}{fix_heading(head, tail)}"
                break
        if h is not None:
            out.append(h)
            continue
        m = ARTICLE_RE.match(ln)
        if m:
            label = m.group(1).strip()
            rest = ln[m.end():]
            out.append(f"\n**{label}** {rest}".rstrip())
            continue
        out.append(ln)

    # 4) Re-unir marcadores de lista huérfanos ("I.-", "1.-", "a)", "A.-")
    #    que pdftotext deja solos en una línea, con su contenido.
    out = rejoin_markers(out)

    txt = "\n".join(out)
    # 5) Colapsar 3+ líneas en blanco a una.
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip() + "\n"


ORPHAN_RE = re.compile(r"^\s*((?:[IVXLCDM]+|\d+)\s*\.-|[a-zA-Z]\)|[A-Z]\s*\.-)\s*$")


def rejoin_markers(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        m = ORPHAN_RE.match(ln)
        if m:
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            if j < n and not lines[j].lstrip().startswith(("#", "**")):
                out.append(f"{m.group(1)} {lines[j].strip()}")
                i = j + 1
                continue
        out.append(ln)
        i += 1
    return out


def to_markdown(entry: dict, body: str) -> str:
    iso = entry["ultima_reforma"]                       # YYYY-MM-DD
    dmy = "-".join(reversed(iso.split("-"))) if iso else ""
    n_art = len(re.findall(r"^\*\*(?:Art[íi]culo|ART[ÍI]CULO)\b", body, re.M))
    titulo = entry["titulo"].replace('"', "'")
    fm = [
        "---",
        "type: ley-federal",
        f"sigla: {entry['sigla']}",
        f"slug: {entry['slug']}",
        f'titulo: "{titulo}"',
        f'ultima_reforma: "{iso}"',
        f'fuente: "DOF / Cámara de Diputados"',
        f"fuente_pdf: {entry['pdf_url']}",
        f"articulos: {n_art}",
        "tags: [ley, federal]",
        "---",
        "",
        f"# {entry['titulo']}",
    ]
    header = "\n".join(fm)
    if dmy:
        header += f"\n> Última reforma publicada DOF {dmy}"
    return header + "\n\n" + body


def load_json(p: Path, default):
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return default


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    catalog = load_json(CATALOG, None)
    if not catalog:
        print("ERROR: catalog.json vacío. Corre scrape_index.py primero.", file=sys.stderr)
        return 2
    state = load_json(STATE, {})
    LEYES.mkdir(exist_ok=True)

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    if only:
        catalog = [c for c in catalog if c["sigla"] in only or c["slug"] in only]
    if args.limit:
        catalog = catalog[: args.limit]

    done = skipped = failed = 0
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for c in catalog:
            slug = c["slug"]
            md_path = LEYES / f"{slug}.md"
            if (not args.force and md_path.exists()
                    and state.get(slug) == c["ultima_reforma"]):
                skipped += 1
                continue
            try:
                pdf = tmp / f"{slug}.pdf"
                fetch_pdf(c["pdf_url"], pdf)
                raw = pdf_to_text(pdf)
                body = clean(raw)
                if len(body) < 400:
                    raise RuntimeError(f"cuerpo sospechosamente corto ({len(body)} chars)")
                md_path.write_text(to_markdown(c, body), encoding="utf-8")
                state[slug] = c["ultima_reforma"]
                done += 1
                print(f"  ✓ {slug}  ({c['ultima_reforma']})")
            except Exception as e:  # noqa: BLE001 — best-effort: log y sigue
                failed += 1
                msg = f"{slug}\t{c['pdf_url']}\t{type(e).__name__}: {e}"
                errors.append(msg)
                print(f"  ✗ {slug}  {e}", file=sys.stderr)

    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2,
                                sort_keys=True) + "\n", encoding="utf-8")
    if errors:
        ERRORS.write_text("\n".join(errors) + "\n", encoding="utf-8")
    print(f"\nconvertidas={done}  sin-cambio={skipped}  fallidas={failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
