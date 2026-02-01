#!/usr/bin/env python3
"""
Generate an image using Google GenAI (Gemini) from a final prompt.

Requires:
- python package: google-genai
- env var: GEMINI_API_KEY
"""

import argparse
import base64
import os
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a PNG image with Gemini.")
    parser.add_argument("--prompt", required=True, help="Final prompt to send to the model")
    parser.add_argument("--out", required=True, help="Output file path (PNG)")
    parser.add_argument(
        "--model",
        default="gemini-3-pro-image-preview",
        help="Model name (default: gemini-3-pro-image-preview)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate arguments without calling the API",
    )
    return parser.parse_args()


def ensure_png_path(path_str):
    if path_str.lower().endswith(".png"):
        return path_str
    return f"{path_str}.png"


def load_client(api_key):
    try:
        from google import genai
    except ImportError:
        print(
            "google-genai is not installed. Install with: pip install google-genai",
            file=sys.stderr,
        )
        return None
    return genai.Client(api_key=api_key)


def extract_image_bytes(response):
    parts = getattr(response, "parts", None)
    if not parts:
        candidates = getattr(response, "candidates", None) or []
        if candidates:
            content = getattr(candidates[0], "content", None)
            parts = getattr(content, "parts", None)
    parts = parts or []
    for part in parts:
        inline = getattr(part, "inline_data", None)
        data = getattr(inline, "data", None) if inline else None
        if data:
            if isinstance(data, str):
                try:
                    return base64.b64decode(data)
                except Exception:
                    return data.encode("utf-8")
            return data
    return None


def main():
    args = parse_args()

    if args.dry_run:
        print("Dry run OK")
        return 0

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set.", file=sys.stderr)
        return 1
    if "GOOGLE_API_KEY" in os.environ:
        os.environ.pop("GOOGLE_API_KEY")

    client = load_client(api_key)
    if client is None:
        return 1

    try:
        from google.genai import types
    except ImportError:
        print(
            "google-genai is not installed. Install with: pip install google-genai",
            file=sys.stderr,
        )
        return 1

    response = client.models.generate_content(
        model=args.model,
        contents=args.prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )

    image_bytes = extract_image_bytes(response)
    if image_bytes is None:
        print("No image data returned by the model.", file=sys.stderr)
        return 1

    out_path = Path(ensure_png_path(args.out))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(image_bytes)

    print(f"Saved image: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
