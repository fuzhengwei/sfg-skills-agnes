#!/usr/bin/env python3
"""
Agnes AI 视频生成脚本

用法:
    # 文生视频（阻塞等待，直到完成）
    python3 scripts/agnes_video.py --prompt "描述" --width 1152 --height 768

    # 图生视频
    python3 scripts/agnes_video.py --prompt "描述" --image "https://example.com/img.png"

    # 多图视频
    python3 scripts/agnes_video.py --prompt "描述" --images "url1,url2"

    # 关键帧动画
    python3 scripts/agnes_video.py --prompt "描述" --images "url1,url2" --mode keyframes

    # 仅创建任务不等待
    python3 scripts/agnes_video.py --prompt "描述" --no-wait

    # 查询已有任务
    python3 scripts/agnes_video.py --query "video_xxxxxx"

    python3 scripts/agnes_video.py --help
"""

import argparse
import json
import sys
import time
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
            "message": "API Key 为空，请先运行: python3 scripts/agnes_video.py set --api-key YOUR_API_KEY"
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    return api_key


# === API 调用 ===

def create_video_task(
    prompt: str,
    image: str = None,
    images: list = None,
    mode: str = None,
    width: int = 1152,
    height: int = 768,
    num_frames: int = 121,
    frame_rate: int = 24,
    seed: int = None,
    negative_prompt: str = None,
) -> dict:
    """创建视频生成任务"""

    api_key = load_api_key()

    # 构建请求体
    body = {
        "model": "agnes-video-v2.0",
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_frames": num_frames,
        "frame_rate": frame_rate,
    }

    if seed is not None:
        body["seed"] = seed
    if negative_prompt:
        body["negative_prompt"] = negative_prompt

    # 处理图片输入
    if images:
        # 多图模式（含关键帧）
        body["extra_body"] = {"image": images}
        if mode == "keyframes":
            body["extra_body"]["mode"] = "keyframes"
    elif image:
        # 单图模式
        body["image"] = image

    # 发送请求
    url = f"{API_BASE}/v1/videos"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {
            "status": "error",
            "http_code": e.code,
            "message": f"创建任务失败 (HTTP {e.code}): {error_body}"
        }
    except urllib.error.URLError as e:
        return {
            "status": "error",
            "message": f"网络错误: {e.reason}"
        }

    return result


def query_video_result(video_id: str, model_name: str = None) -> dict:
    """查询视频生成结果（推荐方式，使用 video_id）"""

    api_key = load_api_key()

    url = f"{API_BASE}/agnesapi?video_id={video_id}"
    if model_name:
        url += f"&model_name={model_name}"

    headers = {"Authorization": f"Bearer {api_key}"}
    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {
            "status": "error",
            "http_code": e.code,
            "message": f"查询失败 (HTTP {e.code}): {error_body}"
        }
    except urllib.error.URLError as e:
        return {
            "status": "error",
            "message": f"网络错误: {e.reason}"
        }

    return result


def poll_until_complete(
    video_id: str,
    poll_interval: int = 5,
    timeout: int = 600,
) -> dict:
    """轮询等待视频生成完成"""

    start_time = time.time()
    last_progress = -1

    print(f"🎬 视频生成任务已创建", file=sys.stderr)
    print(f"   视频 ID: {video_id}", file=sys.stderr)
    print(f"   开始轮询，间隔 {poll_interval} 秒...\n", file=sys.stderr)

    while True:
        elapsed = int(time.time() - start_time)
        if elapsed > timeout:
            return {
                "status": "timeout",
                "message": f"超时（{timeout} 秒），请稍后手动查询: python3 scripts/agnes_video.py --query {video_id}"
            }

        result = query_video_result(video_id)

        if result.get("status") == "error":
            return result

        task_status = result.get("status", "unknown")
        progress = result.get("progress", 0)

        # 更新进度显示
        if progress != last_progress:
            bar_width = 20
            filled = int(bar_width * progress / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            print(f"   [{bar}] {progress}%  (状态: {task_status}, 已等待: {elapsed}s)", file=sys.stderr)
            last_progress = progress

        if task_status == "completed":
            print(f"\n✅ 视频生成完成！", file=sys.stderr)
            return result
        elif task_status == "failed":
            return {
                "status": "error",
                "message": f"视频生成失败: {result.get('error', '未知错误')}",
                "raw_response": result
            }

        time.sleep(poll_interval)


# === 命令行输出美化 ===

def print_create_result(result: dict) -> None:
    """打印创建任务结果"""
    if result.get("status") == "error":
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        return

    video_id = result.get("video_id", "")
    task_id = result.get("task_id", "")
    task_status = result.get("status", "queued")
    seconds = result.get("seconds", "N/A")
    size = result.get("size", "N/A")

    print(f"✅ 任务创建成功", file=sys.stderr)
    print(f"   任务 ID:  {task_id}", file=sys.stderr)
    print(f"   视频 ID:  {video_id}", file=sys.stderr)
    print(f"   状态:     {task_status}", file=sys.stderr)
    print(f"   预计时长: {seconds} 秒", file=sys.stderr)
    print(f"   分辨率:   {size}", file=sys.stderr)


def print_video_result(result: dict) -> None:
    """打印视频生成完成结果"""
    video_url = result.get("remixed_from_video_id", "")
    video_id = result.get("video_id", "")
    seconds = result.get("seconds", "N/A")
    size = result.get("size", "N/A")

    print(json.dumps({
        "status": "ok",
        "video_id": video_id,
        "video_url": video_url,
        "seconds": seconds,
        "size": size,
    }, ensure_ascii=False, indent=2))


# === 主函数 ===

def main():
    parser = argparse.ArgumentParser(
        description="Agnes AI 视频生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  # 文生视频（阻塞等待）
  python3 scripts/agnes_video.py --prompt "A cat walking on beach" --width 1152 --height 768

  # 图生视频
  python3 scripts/agnes_video.py --prompt "slowly turn around" --image "https://example.com/img.png"

  # 多图视频
  python3 scripts/agnes_video.py --prompt "smooth transformation" --images "url1,url2"

  # 关键帧动画
  python3 scripts/agnes_video.py --prompt "smooth transition" --images "url1,url2" --mode keyframes

  # 仅创建任务不等待
  python3 scripts/agnes_video.py --prompt "..." --no-wait

  # 查询已有任务
  python3 scripts/agnes_video.py --query "video_xxxxxx\""""
    )

    # 创建任务参数
    parser.add_argument("--prompt", help="视频生成提示词")
    parser.add_argument("--image", default=None, help="输入图片 URL（图生视频时使用）")
    parser.add_argument("--images", default=None, help="多张输入图片 URL，逗号分隔")
    parser.add_argument("--mode", choices=["ti2vid", "keyframes"], default="ti2vid",
                        help="生成模式 (默认: ti2vid)")
    parser.add_argument("--width", type=int, default=1152, help="视频宽度 (默认: 1152)")
    parser.add_argument("--height", type=int, default=768, help="视频高度 (默认: 768)")
    parser.add_argument("--num-frames", type=int, default=121,
                        help="视频帧数，必须 ≤ 441 且满足 8n+1 (默认: 121)")
    parser.add_argument("--frame-rate", type=int, default=24,
                        help="视频 FPS，1-60 (默认: 24)")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--negative-prompt", default=None, help="负向提示词")
    parser.add_argument("--poll-interval", type=int, default=5, help="轮询间隔秒数 (默认: 5)")
    parser.add_argument("--timeout", type=int, default=600, help="最大等待秒数 (默认: 600)")
    parser.add_argument("--no-wait", action="store_true",
                        help="仅创建任务，不等待完成")

    # 查询参数
    parser.add_argument("--query", default=None, help="查询已有任务的 video_id")

    args = parser.parse_args()

    # 查询模式
    if args.query:
        result = query_video_result(args.query)
        print_video_result(result)
        sys.exit(0 if result.get("status") == "completed" else 1)

    # 创建任务模式
    if not args.prompt:
        parser.print_help()
        sys.exit(0)

    # 帧数校验
    if args.num_frames > 441:
        print(json.dumps({
            "status": "error",
            "message": f"num_frames ({args.num_frames}) 必须 ≤ 441"
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    if (args.num_frames - 1) % 8 != 0:
        print(json.dumps({
            "status": "error",
            "message": f"num_frames ({args.num_frames}) 必须满足 8n+1（如 81/121/161/241/441）"
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    # 解析多图
    images_list = None
    if args.images:
        images_list = [u.strip() for u in args.images.split(",")]

    # 创建任务
    create_result = create_video_task(
        prompt=args.prompt,
        image=args.image,
        images=images_list,
        mode=args.mode if images_list else None,
        width=args.width,
        height=args.height,
        num_frames=args.num_frames,
        frame_rate=args.frame_rate,
        seed=args.seed,
        negative_prompt=args.negative_prompt,
    )

    if create_result.get("status") == "error":
        print(json.dumps(create_result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    print_create_result(create_result)

    video_id = create_result.get("video_id", "")
    if not video_id:
        print(json.dumps({"status": "error", "message": "未返回 video_id"}, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    # 等待完成
    if args.no_wait:
        print(json.dumps({
            "status": "created",
            "video_id": video_id,
            "task_id": create_result.get("task_id", ""),
            "message": f"任务已创建，请稍后查询: python3 scripts/agnes_video.py --query {video_id}"
        }, ensure_ascii=False, indent=2))
        sys.exit(0)

    # 轮询等待
    final_result = poll_until_complete(
        video_id=video_id,
        poll_interval=args.poll_interval,
        timeout=args.timeout,
    )

    if final_result.get("status") == "error":
        print(json.dumps(final_result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    print_video_result(final_result)


if __name__ == "__main__":
    main()
