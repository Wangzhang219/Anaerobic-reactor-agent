# -*- coding: utf-8 -*-
"""
厌氧反应器智能诊断系统 — 一键启动器
双击此文件或在终端执行: python launcher.py
"""
import sys
import os
import webbrowser
import subprocess
import time

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

BANNER = """
╔══════════════════════════════════════════╗
║     厌氧反应器智能诊断系统 v0.2.0       ║
║     Anaerobic Reactor Intelligent Agent ║
╚══════════════════════════════════════════╝
"""

MENU = """
请选择运行模式:
  [1] Web 可视化界面 (推荐)
  [2] CLI 命令行快速诊断
  [3] Demo 演示脚本
  [4] 运行测试
  [0] 退出
"""


def check_deps():
    """Quick dependency check."""
    try:
        import streamlit
        import plotly
        import yaml
        import pydantic
        import rich
        return True
    except ImportError as e:
        print(f"[!] 缺少依赖: {e}")
        print("[*] 正在安装依赖...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
            cwd=PROJECT_DIR,
        )
        print("[OK] 依赖安装完成")
        return True


def run_web():
    """Start Streamlit Web interface."""
    print("\n[*] 正在启动 Web 界面...")
    port = 8501
    url = f"http://localhost:{port}"

    print(f"[*] 浏览器将自动打开: {url}")
    print("[*] 按 Ctrl+C 停止服务\n")

    # Open browser after a short delay
    time.sleep(2)
    webbrowser.open(url)

    os.chdir(PROJECT_DIR)
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "anaerobic_reactor_agent/web/app.py",
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ])


def run_cli():
    """Run CLI interactive mode."""
    print("\n[*] 启动命令行交互模式...\n")
    os.chdir(PROJECT_DIR)
    subprocess.run([
        sys.executable, "-m", "anaerobic_reactor_agent", "interactive",
    ])


def run_demo():
    """Run demo script."""
    print("\n[*] 运行 Demo 演示...\n")
    os.chdir(PROJECT_DIR)
    subprocess.run([sys.executable, "demo.py"])


def run_tests():
    """Run test suite."""
    print("\n[*] 运行测试...\n")
    os.chdir(PROJECT_DIR)
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])


def main():
    os.system("cls" if sys.platform == "win32" else "clear")
    print(BANNER)

    if not check_deps():
        print("[!] 依赖安装失败，请手动执行: pip install -r requirements.txt")
        input("\n按 Enter 退出...")
        sys.exit(1)

    while True:
        print(MENU)
        choice = input("请输入选项 [1]: ").strip() or "1"

        if choice == "1":
            run_web()
            break
        elif choice == "2":
            run_cli()
            break
        elif choice == "3":
            run_demo()
            break
        elif choice == "4":
            run_tests()
            break
        elif choice == "0":
            print("\n再见！")
            break
        else:
            print(f"\n[!] 无效选项: {choice}，请重新输入\n")

    input("\n按 Enter 关闭...")


if __name__ == "__main__":
    main()
