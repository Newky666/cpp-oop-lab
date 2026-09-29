#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_exe.py - 用 PyInstaller 把图形界面打包成单文件 exe

    py build_exe.py              ->  dist\\OOPLab.exe       (单文件, 拷贝方便)
    py build_exe.py --onedir     ->  dist\\OOPLab\\          (文件夹, 启动更快)

不需要 --add-data: 题库是 .py 模块, PyInstaller 会自动收集; 源码里没有
必须随包分发的数据文件(data/sources.json 首次运行会自动生成)。

打包后 exe 可以放在任意目录, 首次运行会在**它旁边**创建 data\\ 与 workspace\\
(靠 oop_common._detect_base_dir() 里的 sys.frozen 分支)。
"""

from __future__ import annotations

import os
import subprocess
import sys

APP_NAME = "OOPLab"
ENTRY = "oop_app.py"
HERE = os.path.dirname(os.path.abspath(__file__))


def _build_pyinstaller_args(onedir: bool = False) -> list:
    """拼 PyInstaller 参数。单独拆出来是为了能被单元测试检查(不用真的打包)。"""
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--log-level", "WARN",
        "--onedir" if onedir else "--onefile",
        "--windowed",
        "--name", APP_NAME,
    ]
    # 文件图标: PyInstaller 的 --icon 必须绝对路径(相对路径会按 specpath 解析失败);
    # 没有 .ico 时静默跳过, 不让缺图标阻塞打包。
    icon = os.path.join(HERE, "oop_lab.ico")
    if os.path.isfile(icon):
        args.extend(["--icon", icon])
    args.append(os.path.join(HERE, ENTRY))
    return args


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    onedir = "--onedir" in argv
    args = _build_pyinstaller_args(onedir=onedir)
    print("正在打包: %s" % " ".join(args[2:]))
    code = subprocess.call(args, cwd=HERE)
    if code != 0:
        print("打包失败(退出码 %d)" % code)
        return code
    target = (os.path.join(HERE, "dist", APP_NAME) if onedir
              else os.path.join(HERE, "dist", APP_NAME + ".exe"))
    if not os.path.exists(target):
        print("打包命令成功了, 但找不到产物: %s" % target)
        return 1
    print("产物: %s" % target)
    if os.path.isfile(target):
        print("大小: %.1f MB" % (os.path.getsize(target) / 1024.0 / 1024.0))
    print("把它拷到任意目录双击即可; data\\ 与 workspace\\ 会生成在 exe 旁边。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
