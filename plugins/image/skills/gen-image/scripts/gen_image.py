#!/usr/bin/env python3
"""
Generate an image using various providers (Gemini, OpenAI) from a final prompt.

Requires:
- python package: google-genai (for Gemini)
- python package: openai (for OpenAI)
- env var: GEMINI_API_KEY (for Gemini)
- env var: OPENAI_API_KEY (for OpenAI)
"""

import argparse
import base64
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path


# --- Providers ---

class ImageProvider(ABC):
    """图像生成提供者抽象基类"""
    @abstractmethod
    def generate(self, prompt: str, model: str) -> bytes:
        """
        生成图像
        :param prompt: 提示词
        :param model: 模型名称
        :return: 图像的二进制数据 (bytes)
        """
        pass


class GeminiProvider(ImageProvider):
    """Google Gemini 图像生成实现"""
    
    def generate(self, prompt: str, model: str) -> bytes:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Environment variable GEMINI_API_KEY is not set.")

        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise ImportError("google-genai is not installed. Install with: pip install google-genai")

        client = genai.Client(api_key=api_key)
        
        # 注意：原代码 model 默认为 "gemini-3-pro-image-preview"
        target_model = model if model else "gemini-3-pro-image-preview"
        
        response = client.models.generate_content(
            model=target_model,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )
        
        return self._extract_image_bytes(response)

    def _extract_image_bytes(self, response):
        """从 Gemini 响应中提取图像字节"""
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


class OpenAIProvider(ImageProvider):
    """OpenAI 图像生成实现"""

    def generate(self, prompt: str, model: str) -> bytes:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Environment variable OPENAI_API_KEY is not set.")

        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai is not installed. Install with: pip install openai")

        client = OpenAI(api_key=api_key)
        
        target_model = model if model else "dall-e-3"

        # 调用 OpenAI API
        # response_format="b64_json" 直接返回 base64 数据，比 url 更稳健
        response = client.images.generate(
            model=target_model,
            prompt=prompt,
            response_format="b64_json",
            n=1,
            # size="1024x1024" # 默认为 1024x1024
        )

        b64_data = response.data[0].b64_json
        return base64.b64decode(b64_data)


def get_provider(name: str) -> ImageProvider:
    """根据名称获取 Provider 实例"""
    providers = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
    }
    if name not in providers:
        raise ValueError(f"Unknown provider: {name}. Available: {list(providers.keys())}")
    return providers[name]()


# --- Main ---

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Generate a PNG image using AI providers.")
    parser.add_argument("--prompt", required=True, help="Final prompt to send to the model")
    parser.add_argument("--out", required=True, help="Output file path (PNG)")
    parser.add_argument(
        "--provider",
        default="gemini",
        choices=["gemini", "openai"],
        help="Image generation provider (default: gemini)",
    )
    parser.add_argument(
        "--model",
        help="Model name (default depends on provider, e.g., gemini-3-pro-image-preview or dall-e-3)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate arguments without calling the API",
    )
    return parser.parse_args()


def ensure_png_path(path_str):
    """确保输出路径以 .png 结尾"""
    if path_str.lower().endswith(".png"):
        return path_str
    return f"{path_str}.png"


def main():
    """主函数"""
    args = parse_args()

    if args.dry_run:
        print(f"Dry run OK. Provider: {args.provider}, Model: {args.model}")
        return 0

    try:
        provider = get_provider(args.provider)
        
        # 简单的 loading 提示
        print(f"Generating image with {args.provider} (model: {args.model or 'default'})...")
        
        image_bytes = provider.generate(args.prompt, args.model)
        
        if not image_bytes:
            print("Error: No image data returned.", file=sys.stderr)
            return 1
            
        out_path = Path(ensure_png_path(args.out))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(image_bytes)

        print(f"Saved image: {out_path}")
        return 0

    except ImportError as e:
        print(f"Dependency Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
