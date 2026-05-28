# Boating Day Map

Static GitHub Pages map for the May 28, 2026 boating itinerary.

## Files

- `index.html` is the shareable map page.
- `route.geojson` is the route and marker source of truth.

## Publish On GitHub Pages

1. Create a public GitHub repository, for example `boating-day-map`.
2. Upload `index.html`, `route.geojson`, and this `README.md` to the repository root.
3. In the repository, open `Settings` -> `Pages`.
4. Under `Build and deployment`, choose `Deploy from a branch`.
5. Choose the `main` branch and `/ (root)`, then save.
6. Share the Pages URL once it finishes publishing:
   `https://<github-username>.github.io/boating-day-map/`

For local preview, run this from the folder:

```sh
python3 -m http.server 8765
```

Then open `http://127.0.0.1:8765/`.
