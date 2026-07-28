# Setup

This repository is designed to be cloned and used immediately, but it is also fully regenerable from the included Python scripts.

## Prerequisites

- Python 3.12+
- Pillow
- GitHub account with permission to edit profile repositories
- Optional: a Vercel account for self-hosting GitHub Readme Stats

## Quick Start

1. Replace `assets/my_pic.png` with your own portrait photo.
2. Replace `assets/flutter logo.png` and `assets/code logo.png` if you want different morph targets.
3. Regenerate the banner and preview:

```bash
python scripts/build_banner.py
```

4. Commit the generated `dark.svg`, `light.svg`, and `preview.png`.
5. Add the repository as your GitHub profile repository.

## Regenerate Everything

The scripts are intentionally small and composable:

- `scripts/image_processor.py` crops and enhances the portrait
- `scripts/dither.py` applies Floyd-Steinberg dithering
- `scripts/morph.py` builds the logo animation layers
- `scripts/optimize_svg.py` trims unnecessary SVG whitespace
- `scripts/build_banner.py` orchestrates the full export

You can run the orchestrator directly:

```bash
python scripts/build_banner.py --avatar "assets/my_pic.png" --output .
```

## Self-Hosted GitHub Stats

The profile README is configured to support self-hosted stats through a Vercel deployment of the GitHub Readme Stats service.

Recommended flow:

1. Fork the GitHub Readme Stats project.
2. Deploy it to Vercel.
3. Set the environment variables required by that project.
4. Update the URLs in `README.md` to point to your deployment.

### Token Instructions

Use a fine-grained personal access token or a classic token with the minimum permissions required by the stats service.

Keep the token:

- In Vercel environment variables
- Out of your README
- Out of the repository

## GitHub Actions

The included `snake.yml` workflow uses the repository token to publish contribution snake SVGs.

Before enabling it:

1. Confirm Actions are enabled in the repository.
2. Ensure the workflow has permission to write contents.
3. Leave the default branch set correctly.

## Deployment

To use this repository as a GitHub profile:

1. Rename the repository to match your GitHub username if needed.
2. Ensure the repo is public.
3. Pin it as your profile repository.
4. Verify the README renders correctly on the profile page.
