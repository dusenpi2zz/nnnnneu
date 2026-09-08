import argparse
import json
import re
import sys
from pathlib import Path

from . import __version__
from .catalog import find_methods, get_method, read_card
from .demo import make_demo
from .workflows import replay, run_config


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="研究方法检索、可复现运行与历史重放")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    search = commands.add_parser("search", help="离线检索方法与工具")
    search.add_argument("query", nargs="?", default="")
    search.add_argument("--domain")
    search.add_argument("--json", action="store_true")
    show = commands.add_parser("show", help="显示完整方法卡")
    show.add_argument("method_id")
    for name in ["run", "replay"]:
        item = commands.add_parser(name)
        item.add_argument("source")
        item.add_argument("--output", required=True)
    demo = commands.add_parser("demo", help="运行合成 ROI 提取及相关分析示例")
    demo.add_argument("--output", required=True)
    demo.add_argument("--seed", type=int, default=42)
    lfpy = commands.add_parser("lfpy-demo", help="运行可选 LFPy/NEURON 被动神经元正向模型")
    lfpy.add_argument("--output", required=True)
    lfpy.add_argument("--dt-ms", type=float, default=0.0625)
    lfpy.add_argument("--sigma", type=float, default=0.3)
    new = commands.add_parser("new-method", help="创建待整理方法卡；不自动提升验证状态")
    new.add_argument("method_id")
    new.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "search":
            rows = find_methods(args.query, args.domain)
            if args.json:
                print(json.dumps(rows, ensure_ascii=False, indent=2))
            else:
                for row in rows:
                    print(f"{row['id']:25} {row['domain']:16} {row['implementation']:22} {row['name']}")
                print(f"{len(rows)} results")
        elif args.command == "show":
            print(read_card(args.method_id))
        elif args.command == "run":
            print(run_config(args.source, args.output))
        elif args.command == "replay":
            print(replay(args.source, args.output))
        elif args.command == "demo":
            print(make_demo(args.output, args.seed))
        elif args.command == "lfpy-demo":
            from .lfpy_demo import run_lfpy_demo
            print(run_lfpy_demo(args.output, dt_ms=args.dt_ms, sigma=args.sigma))
        else:
            if not re.fullmatch(r"[a-z][a-z0-9-]{2,63}", args.method_id):
                raise ValueError("method ID must contain 3..64 lowercase letters/digits/hyphens")
            if any(r["id"] == args.method_id for r in find_methods()):
                raise ValueError("method ID already exists")
            output = Path(args.output)
            output.mkdir(parents=True, exist_ok=True)
            target = output / (args.method_id + ".md")
            with target.open("x", encoding="utf-8") as stream:
                stream.write(f"# {args.method_id}\n\n状态：待整理；尚未验证。\n\n" + "\n\n".join(
                    f"## {title}\n\n待填写。" for title in ["研究问题", "适用条件与不适用条件", "输入和输出",
                    "假设与关键参数", "操作流程", "质量检查与失败案例", "论文与官方来源", "版本与验证证据", "研究使用记录"]) + "\n")
            print(target)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0
