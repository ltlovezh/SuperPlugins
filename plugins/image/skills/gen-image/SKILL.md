---
name: gen-image
description: 基于用户提供的主题Prompt，借助OpenAI DALL-E、Google Nano Banana等大模型生成图片，支持选择图片风格和图片参数（分辨率、宽高比）。当用户要求生成图片时使用。
---

# Gen Image

## 概览
将用户输入的主题Prompt、选择的内置图片风格Prompt与图片参数拼接为最终Prompt，并调用内置Python脚本生成单张PNG。

## 流程
1. 获取用户输入的主题Prompt
2. 判断风格：若用户未指定，让其从内置图片风格中选择
3. 判断图片参数：若用户未指定，让其从常量中选择分辨率与宽高比
4. 读取所选的内置图片风格文件，并组装成Final Prompt
5. 根据主题Prompt，生成简短的文件名（<=10字），使用`.png`后缀
6. 在Python虚拟环境中运行 `scripts/gen_image.py`
7. 告知用户图片保存路径

## 内置图片风格（仅在选择后加载）
- `references/工程蓝图纸绘风格.md`
- `references/思维导图手绘风格.md`
- `references/暖色手绘插画风格.md`

## 图片参数常量
- Resolution: `1K`, `2K`, `4K`
- Aspect ratio: `1:1`, `9:16`, `16:9`

## Prompt 拼接
使用以下模板（除非用户要求翻译，否则保留主题原文）：

```
Subject: {subject}
Style: {style_prompt}
Parameters: Resolution={resolution}; Aspect ratio={ratio}; Output=PNG
```

## 运行生成器（必须Python虚拟环境）
- 在项目根目录创建或复用Python虚拟环境 `.venv`。
- 安装依赖：`pip install google-genai` (Gemini) 或 `pip install openai` (OpenAI)。
- 运行：

```
./.venv/bin/python scripts/gen_image.py --prompt "<final_prompt>" --out "<output_path>" --provider <gemini|openai>
```

- 可选参数：
  - `--provider`: 默认为 `gemini`
  - `--model`: 覆盖默认模型 (Gemini 默认为 `gemini-3-pro-image-preview`, OpenAI 默认为 `dall-e-3`)。
- 环境变量：需根据 Provider 设置 `GEMINI_API_KEY` 或 `OPENAI_API_KEY`
