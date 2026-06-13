#!/usr/bin/env python3
"""
Agnes AI 图像生成脚本

用法:
    # 文生图
    python3 scripts/agnes_image.py --prompt "描述" --size "1024x768"

    # 图生图（URL 输入）
    python3 scripts/agnes_image.py --prompt "描述" --size "1024x768" --image "https://example.com/img.png"

    # 图生图（本地文件输入）
    python3 scripts/agnes_image.py --prompt "描述" --size "1024x768" --image "/path/to/local/img.png"

    # 仅返回 URL 不下载
    python3 scripts/agnes_image.py --prompt "描述" --size "1024x768" --no-download

    python3 scripts/agnes_image.py --help
"""

import argparse
import base64
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path


# === 配置加载 ===

CONFIG_DIR = Path.home() / ".agnes"
CONFIG_FILE = CONFIG_DIR / "config.json"
API_BASE = "https://apihub.agnes-ai.com"


def load_api_key() -> str:
    """从本地配置加载 API Key"""
    if not CONFIG_FILE.exists():
        print(json.dumps({
            "status": "error",
            "message": "API Key 尚未配置，请先运行: python3 scripts/agnes_config.py set --api-key YOUR_API_KEY"
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    api_key = config.get("api_key", "")
    if not api_key:
        print(json.dumps({
            "status": "error",
            "message": "API Key 为空，请先运行: python3 scripts/agnes_config.py set --api-key YOUR_API_KEY"
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    return api_key


# === 图片处理 ===

def image_to_data_uri(image_path: str) -> str:
    """将本地图片文件转为 Data URI Base64"""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    # 推断 MIME 类型
    suffix = path.suffix.lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }
    mime = mime_map.get(suffix, "image/png")

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    return f"data:{mime};base64,{b64}"


def is_url(text: str) -> bool:
    """判断是否为 URL"""
    return text.startswith("http://") or text.startswith("https://")


# === API 调用 ===

def generate_image(
    prompt: str,
    size: str = "1024x768",
    image: str = None,
    output_format: str = "url",
    return_base64: bool = False,
) -> dict:
    """调用 Agnes Image API 生成图片"""

    api_key = load_api_key()

    # 构建请求体
    body = {
        "model": "agnes-image-2.1-flash",
        "prompt": prompt,
        "size": size,
    }

    # 图生图：处理输入图片
    if image:
        if is_url(image):
            body["image"] = [image]
        else:
            # 本地文件转 Data URI Base64
            data_uri = image_to_data_uri(image)
            body["image"] = [data_uri]

    # 输出格式处理
    # 注意：response_format 必须放在 extra_body 中！
    if image:
        # 图生图
        if output_format == "b64_json":
            body["extra_body"] = {"response_format": "b64_json", "image": body.pop("image")}
        else:
            body["extra_body"] = {"response_format": "url", "image": body.pop("image")}
    else:
        # 文生图
        if return_base64:
            body["return_base64"] = True
        else:
            body["extra_body"] = {"response_format": "url"}

    # 发送请求
    url = f"{API_BASE}/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=360) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {
            "status": "error",
            "http_code": e.code,
            "message": f"API 请求失败 (HTTP {e.code}): {error_body}"
        }
    except urllib.error.URLError as e:
        return {
            "status": "error",
            "message": f"网络错误: {e.reason}"
        }

    # 解析结果
    if "data" in result and len(result["data"]) > 0:
        item = result["data"][0]
        image_url = item.get("url")
        b64_data = item.get("b64_json")

        return {
            "status": "ok",
            "url": image_url,
            "b64_json": b64_data,
            "revised_prompt": item.get("revised_prompt"),
            "created": result.get("created"),
            "mode": "img2img" if image else "txt2img"
        }
    else:
        return {
            "status": "error",
            "message": "API 返回数据为空",
            "raw_response": result
        }


def download_image(url: str, output_dir: str, filename: str = None) -> str:
    """下载图片到本地"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not filename:
        # 从 URL 提取文件名或生成随机名
        url_path = url.split("?")[0].split("/")[-1]
        if "." in url_path:
            filename = url_path
        else:
            import time
            filename = f"agnes_image_{int(time.time())}.png"

    file_path = output_path / filename

    urllib.request.urlretrieve(url, str(file_path))
    return str(file_path.resolve())


# === 主函数 ===

def main():
    parser = argparse.ArgumentParser(
        description="Agnes AI 图像生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  # 文生图
  python3 scripts/agnes_image.py --prompt "A sunset over mountains" --size "1024x768"

  # 图生图（URL 输入）
  python3 scripts/agnes_image.py --prompt "Make it cyberpunk style" --size "1024x768" --image "https://example.com/img.png"

  # 图生图（本地文件输入）
  python3 scripts/agnes_image.py --prompt "Change to watercolor style" --size "1024x768" --image "./photo.png"

  # 仅返回 URL 不下载
  python3 scripts/agnes_image.py --prompt "A cat" --size "1024x768" --no-download"""
    )

    parser.add_argument("--prompt", required=True, help="图片生成提示词")
    parser.add_argument("--size", default="1024x768", help="输出图片尺寸 (默认: 1024x768)")
    parser.add_argument("--image", default=None, help="输入图片 URL 或本地文件路径（图生图时使用）")
    parser.add_argument("--output-format", choices=["url", "b64_json"], default="url",
                        help="输出格式 (默认: url)")
    parser.add_argument("--output-dir", default=".", help="图片保存目录 (默认: 当前目录)")
    parser.add_argument("--no-download", action="store_true",
                        help="仅返回 URL，不下载图片")
    parser.add_argument("--return-base64", action="store_true",
                        help="文生图时返回 Base64 数据")

    args = parser.parse_args()

    # 调用 API
    result = generate_image(
        prompt=args.prompt,
        size=args.size,
        image=args.image,
        output_format=args.output_format,
        return_base64=args.return_base64,
    )

    if result["status"] == "error":
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    # 下载图片
    if result.get("url") and not args.no_download and not args.return_base64:
        try:
            local_path = download_image(result["url"], args.output_dir)
            result["local_path"] = local_path
        except Exception as e:
            result["download_error"] = str(e)

    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2)

    # 如果有 b64_json 数据，单独输出到文件以避免终端刷屏
    if result.get("b64_json"):
        b64_len = len(result["b64_json"])
        result["b64_json"] = f"<{b64_len} chars, omitted from output>"

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
