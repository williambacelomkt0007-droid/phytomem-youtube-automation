# Phytomem media module

Adds neural English narration and a basic 16:9 video render to the existing script workflow.

## Install/update
Upload `make_video.py`, replace `requirements.txt`, and upload `.github/workflows/build-video.yml` to the existing private GitHub repository. Keep the existing `generate.py`, `config.json`, and script-generation workflow.

## Run
1. Run the existing script-generation workflow first.
2. Open Actions → Build narrated video → Run workflow.
3. Download the `phytomem-video` artifact.

## Notes
- Uses the Edge TTS online service through an unofficial Python client. Availability, terms, throttling and voice access may change; it is not a guaranteed or unlimited service.
- FFmpeg creates a simple original text-card video. It is a working technical prototype, not a polished documentary edit.
- No YouTube upload is configured.
- Review medical and product claims and verify every product-specific detail before publishing.
