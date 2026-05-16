#!/usr/bin/env python3
"""
Scrapea el índice de Leyes Federales de la Cámara de Diputados.

Fuente: https://www.diputados.gob.mx/LeyesBiblio/index.htm
Salida: catalog.json — lista de {sigla, titulo, pdf_url, ref_url, ultima_reforma}

El índice es una tabla. Cada ley es un <tr> con 3 celdas:
  1) título + enlace ref/<x>.htm + fecha de publicación "DOF dd/mm/aaaa"
  2) última reforma "DOF dd/mm/aaaa"   <- lo que nos importa para detectar cambios
  3) enlaces de descarga: pdf/<SIGLA>.pdf, doc/<SIGLA>.doc, pdf_mov/<titulo>.pdf
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

BASE = "https://www.diputados.gob.mx/LeyesBiblio/"
INDEX_URL = BASE + "index.htm"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) lex-mx/1.0 (+github.com/ingteranalvarez/lex-mx)"

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"

DOF_RE = re.compile(r"DOF\s+(\d{2})/(\d{2})/(\d{4})")
PDF_RE = re.compile(r'href="(pdf/[^"]+\.pdf)"', re.I)
DOC_RE = re.compile(r'href="(doc/[^"]+\.doc)"', re.I)
MOV_RE = re.compile(r'href="(pdf_mov/[^"]+\.pdf)"', re.I)
REF_RE = re.compile(r'href="(ref/[^"]+\.htm)"[^>]*>\s*(?:<font[^>]*>)?\s*([^<]+?)\s*(?:</font>)?\s*</a>', re.I)
NUMERIC_SIGLA_RE = re.compile(r"^\d")  # "79", "10_270614", "36_200521"...


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    # El sitio sirve Windows-1252; decodificar tolerante.
    try:
        return raw.decode("windows-1252")
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="replace")


def iso_date(m: re.Match) -> str:
    d, mo, y = m.groups()
    return f"{y}-{mo}-{d}"


def parse(html: str) -> list[dict]:
    rows = re.split(r"<tr[ >]", html, flags=re.I)
    out: list[dict] = []
    seen: set[str] = set()
    for row in rows:
        pdf = PDF_RE.search(row)
        if not pdf:
            continue
        pdf_path = pdf.group(1)
        # SIGLA = nombre de archivo del .doc si existe, si no del .pdf.
        doc = DOC_RE.search(row)
        if doc:
            sigla = Path(doc.group(1)).stem
        else:
            sigla = Path(pdf_path).stem
        # Saltar reglamentos del Congreso/Senado y duplicados.
        if sigla in seen:
            continue

        # Nombre descriptivo legible del paquete móvil (fallback de título y slug).
        mov = MOV_RE.search(row)
        mov_name = ""
        if mov:
            stem = Path(mov.group(1)).stem
            mov_name = unescape(urllib.parse.unquote(stem)).replace("_", " ").replace("-", " ")
            mov_name = re.sub(r"\s+", " ", mov_name).strip()

        ref = REF_RE.search(row)
        if ref:
            ref_url = BASE + ref.group(1)
            titulo = unescape(re.sub(r"\s+", " ", ref.group(2)).strip())
            titulo = normalize_title(titulo)
        else:
            ref_url = ""
            titulo = mov_name or sigla

        # slug = nombre de archivo en el repo. Los siglas canónicos (CFF, LIVA,
        # CPEUM...) se conservan; los numéricos/fechados se reemplazan por un
        # slug legible derivado del nombre descriptivo.
        if NUMERIC_SIGLA_RE.match(sigla) and mov_name:
            slug = slugify(mov_name)
        else:
            slug = sigla

        # Todas las fechas DOF de la fila, en orden. La última reforma es la
        # que aparece en la 2a celda: tomamos la ÚLTIMA fecha antes del bloque
        # de descargas (que empieza en el primer enlace pdf/).
        head = row[: row.lower().find('href="pdf/')]
        dates = list(DOF_RE.finditer(head))
        ultima_reforma = iso_date(dates[-1]) if dates else ""

        out.append(
            {
                "sigla": sigla,
                "slug": slug,
                "titulo": titulo,
                "pdf_url": BASE + pdf_path,
                "ref_url": ref_url,
                "ultima_reforma": ultima_reforma,
            }
        )
        seen.add(sigla)
    return out


def slugify(name: str) -> str:
    """Nombre de archivo seguro y legible: sin acentos, PalabrasUnidas."""
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    words = re.findall(r"[A-Za-z0-9]+", n)
    return "".join(w.capitalize() if not w.isupper() else w for w in words)[:80] or "Ley"


def normalize_title(t: str) -> str:
    """El índice grita la primera palabra (CÓDIGO/LEY/CONSTITUCIÓN). Normaliza
    solo esa primera palabra a Capitalizado, deja el resto como viene."""
    parts = t.split(" ", 1)
    if not parts:
        return t
    first = parts[0]
    if first.isupper() and len(first) > 1:
        first = first.capitalize()
    return first if len(parts) == 1 else f"{first} {parts[1]}"


def main() -> int:
    html = fetch(INDEX_URL)
    catalog = parse(html)
    if len(catalog) < 200:
        print(f"ERROR: solo {len(catalog)} leyes parseadas (esperado ~300+). "
              f"¿Cambió la estructura del sitio?", file=sys.stderr)
        return 2
    missing = [c["sigla"] for c in catalog if not c["ultima_reforma"]]
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(catalog)} leyes → {CATALOG.relative_to(ROOT)}")
    if missing:
        print(f"AVISO: {len(missing)} sin fecha de última reforma: {missing[:10]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
