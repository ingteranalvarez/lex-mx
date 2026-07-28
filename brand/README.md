# Brand / Identidad Visual — Lex MX

Este paquete toma como fuente visual principal `brand/source/logo.png` y `brand/source/logocompleto.png`. El símbolo reconocido es el bloque `{LX}`; no se introduce otro isotipo.

## Colores

| Rol | HEX | RGB | CMYK aprox. |
|---|---:|---:|---:|
| Azul principal | `#0C4EA9` | `(12, 78, 169)` | `(93, 54, 0, 34)` |
| Azul acento | `#1878F0` | `(24, 120, 240)` | `(90, 50, 0, 6)` |
| Azul profundo | `#083A90` | `(8, 58, 144)` | `(94, 60, 0, 44)` |
| Tinta | `#111827` | `(17, 24, 39)` | `(56, 38, 0, 85)` |
| Fondo claro | `#F8FAFC` | `(248, 250, 252)` | `(2, 1, 0, 1)` |
| Línea neutra | `#E5E7EB` | `(229, 231, 235)` | `(3, 2, 0, 8)` |

## Versiones

- **Principal / clara:** símbolo y logotipo azul sobre fondo blanco o transparente. Usar `logo-horizontal.svg`, `logo-vertical.svg` e `icon.svg`.
- **Oscura:** usar versiones `*-dark.*` sobre `#0B1220` o fondos oscuros equivalentes.
- **Monocromática:** usar `*-mono.*` en una sola tinta cuando la reproducción no admita color.
- **Icono corto:** usar `icon.svg` o los PNG `icon-*.png` cuando el espacio sea pequeño.

## Tipografía Sugerida

- **Inter** para interfaces, README, documentación y piezas digitales.
- **IBM Plex Sans** como alternativa editorial cuando se quiera un tono más institucional.
- Mantener títulos en peso 700 y texto en 400/500. Evitar condensadas, serif decorativas o estilos manuscritos.

## Uso Permitido

- Respetar el símbolo `{LX}` y su proporción.
- Usar la versión horizontal cuando haya espacio suficiente.
- Usar el icono solo para favicon, avatar, app icon o espacios menores a 160 px de ancho.
- Mantener margen mínimo igual a la altura de la `L` interna alrededor del logo.
- Preferir SVG para interfaces y PNG para plataformas que lo exijan.

## Uso Prohibido

- No crear otro isotipo ni separar las llaves del `LX` como símbolos independientes.
- No aplicar sombras, gradientes, efectos 3D, biseles ni texturas.
- No cambiar el azul principal por colores ajenos a la paleta.
- No deformar, inclinar, comprimir ni estirar el logo.
- No colocar el logo azul sobre fondos de bajo contraste.
- No usar datos reales, secretos o información privada dentro de assets de marca.

## Tamaños Recomendados

- Favicon: `favicon.svg`, `favicon.ico`, `icon-16.png`, `icon-32.png`.
- Web app/PWA: `android-chrome-192.png`, `android-chrome-512.png`, `site.webmanifest`.
- Apple/iOS: `apple-touch-icon.png`.
- GitHub: `avatar-github.svg`, `avatar-github-512.png`, `banner-github.png`.
- Social preview: `og-image.png`.

## Nota Técnica

Los PNG fuente no incluyen canal alpha. Para este paquete se removió el fondo blanco por máscara de luminancia, se limpiaron halos de borde y se aplanó la marca a la paleta documentada para mantener proporciones consistentes sin sombras, gradientes ni texturas.
