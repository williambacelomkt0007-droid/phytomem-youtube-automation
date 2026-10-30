# Phytomem YouTube Automation — starter

This starter safely generates **one English-language video script and YouTube metadata package** using the Gemini API. It does not upload or publish videos. Review every output before publication.

## Requirements
- A GitHub repository (private recommended)
- GitHub Actions enabled
- Repository secret named `GEMINI_API_KEY`
- Gemini API access on a no-cost tier, subject to Google's changing quotas and model availability

## Install
1. Download and unzip this package.
2. In your GitHub repository, choose **Add file → Upload files**.
3. Upload the *contents* of this folder (including `.github`).
4. Commit to the default branch.
5. Open **Actions** and enable workflows if GitHub asks.
6. Select **Generate draft** → **Run workflow**.
7. When it finishes, download the `draft-package` artifact.

## What it creates
- `output/script.md` — narration script
- `output/metadata.json` — title, description, tags, thumbnail concept and chapters

## Important safeguards
- No automatic YouTube upload is configured.
- No daily schedule is enabled yet. First validate quality, quota use and the actual product facts.
- Never commit API keys. Keep `GEMINI_API_KEY` only in GitHub Actions Secrets.
- Do not publish medical promises, disease-treatment claims, fabricated testimonials, invented clinical evidence, or claims that you personally tested the supplement.
- The supplied affiliate link in `config.json` is deliberately a placeholder. Replace it only with the real ClickBank HopLink from your account.
- The generated content is a draft, not verified product research. Confirm ingredients, serving details, price, refund terms and claims against current official materials before publishing.
- Add a clear affiliate disclosure near the beginning of the description and, ideally, spoken in the video.

## Free-tier reality
GitHub Actions, Gemini API and YouTube API have changing limits and eligibility rules. Free access is not unlimited or guaranteed. This workflow runs only when manually triggered to avoid unexpected quota use.
