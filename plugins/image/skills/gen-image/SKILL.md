---
name: gen-image
description: 基于用户提供的主体 Prompt 生成图片，支持内置风格与图片参数（分辨率、宽高比）选择。适用于用户要求特定风格生成、需要选择风格/参数、或希望通过 google-genai (Gemini) 使用 GEMINI_API_KEY 生成 PNG 的场景。
---

# Gen Image

## 概览
将主体 Prompt、所选内置风格 Prompt 与图片参数拼接为最终 Prompt，并调用内置 Python 脚本生成单张 PNG。

## 流程
1. 获取用户的主体 Prompt。
2. 判断风格：若用户未指定，让其从内置风格中选择。
3. 判断图片参数：若缺失，让其从常量中选择分辨率与宽高比。
4. 读取所选风格文件并组装最终 Prompt。
5. 根据主体 Prompt 生成输出文件名（<=10 字）。
6. 在 Python 虚拟环境中运行 `scripts/gen_image.py`。
7. 告知图片保存路径。

## 内置风格（仅在选择后加载）
- `references/工程蓝图纸绘风.md`
- `references/思维导图手绘.md`
- `references/暖色手绘信息图.md`

## 图片参数常量
- Resolution: `1K`, `2K`, `4K`
- Aspect ratio: `1:1`, `9:16`, `16:9`

## Prompt 拼接
使用以下模板（除非用户要求翻译，否则保留主体原文）：

```
Subject: {subject}
Style: {style_prompt}
Parameters: Resolution={resolution}; Aspect ratio={ratio}; Output=PNG
```

## 输出命名
- 从主体 Prompt 派生文件名。
- 不超过 10 个字符（中文按 1 计）。
- 去除空格与标点，若清理后为空则使用 `image`。
- 保存到当前项目目录，确保 `.png` 扩展名。

## 运行生成器（必须在 venv）
- 在项目根目录创建或复用 `.venv`。
- 安装依赖：`pip install google-genai`。
- 运行：

```
./.venv/bin/python scripts/gen_image.py --prompt "<final_prompt>" --out "<output_path>"
```

- 可选覆盖：`--model "gemini-3-pro-image-preview"`。
- 若缺少 `GEMINI_API_KEY`，停止并提示用户设置。
