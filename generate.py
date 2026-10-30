import json
import os
import re
from pathlib import Path
from google import genai
from google.genai import types

ROOT = Path(__file__).parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

def load_config():
    with (ROOT / "config.json").open(encoding="utf-8") as f:
        return json.load(f)

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Missing GEMINI_API_KEY. Add it under GitHub Settings > Secrets and variables > Actions.")
    cfg = load_config()
    affiliate = cfg["affiliate_link"]
    if affiliate == "REPLACE_WITH_YOUR_REAL_CLICKBANK_HOPLINK":
        affiliate_note = "Do not invent a URL. Use a neutral placeholder and clearly mark it for later replacement."
    else:
        affiliate_note = f"Use this affiliate URL exactly as supplied: {affiliate}"

    client = genai.Client(api_key=api_key)
    prompt = f"""
You are a careful US-English health-product explainer and consumer-review scriptwriter.
Create a useful, original YouTube draft about {cfg['product_name']} for the channel
{cfg['channel_name']}. Target about {cfg['target_duration_minutes']} minutes of narration.

IMPORTANT EDITORIAL RULES:
- Do not claim the writer or host personally used or tested the product.
- Do not claim it prevents, treats, cures, or reverses Alzheimer's, dementia, memory loss,
  or any disease. Do not promise results or imply guaranteed efficacy.
- Do not invent ingredients, dosages, clinical trials, certifications, endorsements,
  customer reviews, prices, refund terms, manufacturer details, or product availability.
- Product-specific facts have not been independently verified. Explicitly say viewers
  should verify the current label and official seller information.
- Distinguish general ingredient research from evidence about the finished product.
- Explain that supplements are not a substitute for medical advice or prescribed care.
- Encourage viewers who take medication, are pregnant, have a medical condition, or
  are considering a supplement to consult a qualified healthcare professional.
- Avoid fake urgency, fabricated scarcity, and manipulative claims.
- Include balanced sections: what it is (only at a high level), what to verify on the
  label, how to evaluate evidence, potential limitations, questions to ask before buying,
  and a fair conclusion.
- Include a clear spoken affiliate disclosure: the channel may earn a commission if
  viewers buy through the link, at no extra cost to them.
- Do not cite imaginary sources. Include a short research checklist of primary sources
  the human editor must verify before publication.
- {affiliate_note}

Return ONLY valid JSON with these keys:
"title": string,
"script_markdown": string,
"description": string,
"tags": array of strings,
"thumbnail_concept": string,
"chapters": array of objects with "time" and "title",
"fact_check_before_publish": array of strings
"""
    response = client.models.generate_content(
        model=cfg.get("model", "gemini-flash-latest"),
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.5,
            max_output_tokens=7000,
        ),
    )
    raw = response.text or ""
    data = json.loads(raw)
    script = data.get("script_markdown", "").strip()
    if len(script.split()) < 450:
        raise RuntimeError("Generated script is unexpectedly short. Re-run or review model output.")
    # Add disclosure to description if the model omitted it.
    desc = data.get("description", "").strip()
    if "affiliate" not in desc.lower() and "commission" not in desc.lower():
        desc += "\n\nAffiliate disclosure: This description contains an affiliate link. If you purchase through it, this channel may earn a commission at no additional cost to you."
    (OUT / "script.md").write_text(
        f"# {data.get('title', cfg['product_name'] + ' Review')}\n\n{script}\n",
        encoding="utf-8"
    )
    (OUT / "metadata.json").write_text(
        json.dumps({k: v for k, v in data.items() if k != "script_markdown"} | {"description": desc}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print("Draft generated. Review output/script.md and output/metadata.json before use.")

if __name__ == "__main__":
    main()
