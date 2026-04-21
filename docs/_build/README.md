# Build helpers for Lumina's GitHub Pages

These scripts are **not** part of the Lumina skill itself. They only exist to
regenerate the visual assets (favicon, OG card, illustration vignettes) that
ship inside `docs/assets/`.

You never need to run them to use Lumina — they live here only so future me
can rebuild the site if the source illustrations change.

| Script | What it does |
|---|---|
| `build_assets.py` | Builds favicon family + OG card from the main portrait |
| `paper_vignette.py` | Softens the edges of scene illustrations into paper color (#F7F5EE) |
| `match_paper_bg.py` | Replaces near-white backgrounds in generated art with paper color |

## Requirements

```bash
pip install pillow
```

Source illustrations live in a separate `webdev-static-assets/` directory
(not committed here) — edit the path constants at the top of each script if
you want to regenerate.
