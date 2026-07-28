# Customization

## Replace the Photo

Put your portrait at:

```text
assets/my_pic.png
```

Then regenerate:

```bash
python scripts/build_banner.py
```

The banner build will:

- crop the portrait to a head-and-shoulders composition
- enhance contrast and clarity
- dither the image into a vector-friendly grid
- export the dark and light banner variants

## Replace the Logos

Swap these files if you want alternate morph targets:

- `assets/flutter logo.png`
- `assets/code logo.png`
- `assets/developer.svg`

The animation layer in `scripts/morph.py` reads those paths and exposes them in the banner.

## Regenerate the SVG

Use:

```bash
python scripts/build_banner.py
```

If you only want optimization:

```bash
python scripts/optimize_svg.py dark.svg
python scripts/optimize_svg.py light.svg
```

## Update Social Links

Edit the badge URLs in `README.md` to match:

- LinkedIn profile
- Email address
- Portfolio URL

## Notes on the Preview

`preview.png` is a local raster preview for quick inspection. It is regenerated from the same build pipeline and is safe to commit.
