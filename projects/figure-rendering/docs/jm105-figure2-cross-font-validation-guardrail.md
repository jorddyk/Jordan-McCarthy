# JM105 Figure 2 cross-font validation guardrail

Date: 2026-07-14

## Incident

Figure 2 v4 passed local collision checks under Liberation Sans but failed on Euler because Euler resolved the requested Arial font to DejaVu Sans. The wider DejaVu text caused the Panel A legend label `0.5% glucose CR (n=98)` to extend beyond the fixed canvas. The fail-closed gate stopped the render, but the package should never have been delivered without validation under Euler's actual fallback font.

## Permanent rule

A fixed-canvas figure renderer is not deliverable after testing under only one resolved font.

Before delivery, render the complete figure under every font that can actually be selected by the declared fallback chain on the target systems. For the JM105 Euler/Windows workflow this means, at minimum:

1. Arial when available;
2. Liberation Sans;
3. DejaVu Sans, which is the observed Euler fallback.

The complete A-F render must pass under each tested font. Testing one panel or only the local default font is insufficient.

## Required hard checks per font

For every panel and every tested font:

- no text bbox outside the fixed figure canvas;
- no text-text overlap;
- no visible systematic ORF identifiers;
- no point inside a visible label bbox;
- no legend/data-axes intersection;
- no automatic tight cropping;
- every SVG/PDF/PNG/white-preview output exists and is non-empty.

## Layout rule for legends

Do not rely on a horizontal multi-column Matplotlib legend when the canvas is narrow and fallback font metrics can change. Use a dedicated fixed legend lane with one item per row, or prove the longest label fits under every target font.

## v4.1 repair

- Panel A legend changed to a fixed two-row manual legend lane.
- Panel B legend changed to a fixed two-row manual legend lane.
- Panel B right-label slots expanded for DejaVu metrics.
- Panel C left/right quadrant body columns moved farther apart.
- The full A-F renderer passed under both Liberation Sans and DejaVu Sans before packaging.

## Handoff requirement

Future chats must report the resolved font and the result of the complete cross-font matrix. A claim such as `collision audit passed` is incomplete unless the target Euler fallback font was included.
