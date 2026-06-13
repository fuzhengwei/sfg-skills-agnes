#!/usr/bin/env python3
"""
Agnes AI 配置管理脚本

用法:
    python3 scripts/agnes_config.py set --api-key YOUR_API_KEY
    python3 scripts/agnes_config.py show
    python3 scripts/agnes_config.py delete
    python3 scripts/agnes_config.py --help
"""

import argparse
import json
import sys
from pathlib import Path


CONFIG_DIR = Path.home() / ".agnes"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """加载配置文件"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config: dict) -> None:
    """保存配置文件"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    # 设置文件权限为仅用户可读写，保护 API Key
    CONFIG_FILE.chmod(0o600)


def set_api_key(api_key: str) -> None:
    """设置 API Key"""
    config = load_config()
    config["api_key"] = api_key
    save_config(config)

    # 输出结果（隐藏部分 Key）
    masked = api_key[:8] + "****" + api_key[-4:] if len(api_key) > 12 else "****"
    result = {
        "status": "ok",
        "message": "API Key 已保存",
        "api_key_masked": masked,
        "config_path": str(CONFIG_FILE)
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def show_config() -> None:
    """显示当前配置"""
    config = load_config()

    if not config or "api_key" not in config:
        result = {
            "status": "not_configured",
            "message": "API Key 尚未配置，请运行: python3 scripts/agnes_config.py set --api-key YOUR_API_KEY",
            "config_path": str(CONFIG_FILE)
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    api_key = config["api_key"]
    masked = api_key[:8] + "****" + api_key[-4:] if len(api_key) > 12 else "****"

    result = {
        "status": "configured",
        "api_key_masked": masked,
        "config_path": str(CONFIG_FILE)
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def delete_config() -> None:
    """删除配置文件"""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        result = {
            "status": "ok",
            "message": "配置已删除",
            "config_path": str(CONFIG_FILE)
        }
    else:
        result = {
            "status": "not_found",
            "message": "配置文件不存在",
            "config_path": str(CONFIG_FILE)
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Agnes AI 配置管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python3 scripts/agnes_config.py set --api-key YOUR_API_KEY
  python3 scripts/agnes_config.py show
  python3 scripts/agnes_config.py delete"""
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # set
    set_parser = subparsers.add_parser("set", help="设置 API Key")
    set_parser.add_argument("--api-key", required=True, help="Agnes AI API Key")

    # show
    subparsers.add_parser("show", help="显示当前配置")

    # delete
    subparsers.add_parser("delete", help="删除配置文件")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "set":
        set_api_key(args.api_key)
    elif args.command == "show":
        show_config()
    elif args.command == "delete":
        delete_config()


if __name__ == "__main__":
    main()
