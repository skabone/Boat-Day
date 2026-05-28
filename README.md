# Anchors Aweigh Boat Day

Static GitHub Pages package for the May 28, 2026 boating sendoff for Drs. Hana and Ruth.

Live site: https://skabone.github.io/Boat-Day/

## Files

- `index.html` is the shareable map page.
- `itinerary.html` is the designed itinerary, packing list, weather snapshot, and group text page.
- `itinerary.pdf` is the printable/shareable PDF.
- `route.geojson` is the route and marker source of truth.
- `assets/` contains the web/PDF images.
- `scripts/build_itinerary_pdf.py` regenerates the PDF from local assets.

## Local Preview

Run this from the folder:

```sh
python3 -m http.server 8765
```

Then open `http://127.0.0.1:8765/`.

## GitHub Pages

This repository is published from the `main` branch at `/ (root)`.
