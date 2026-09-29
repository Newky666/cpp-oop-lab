#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_app.py - 图形界面入口

这个文件是打包成 OOPLab.exe 的**入口**。它只做两件事:

  1. 补上被 --windowed 抹掉的 stdout/stderr(否则任何 print/isatty 都会崩);
  2. 启动主窗口。

命令行版仍然是 oop_lab.py —— 两者互不影响, 各用各的。
"""

from __future__ import annotations

import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def ensure_streams() -> None:
    """--windowed 打包后 sys.stdout / sys.stderr 是 None。

    Python 的 print() 遇到 None 会静默丢弃, 但任何 .write() / .isatty() /
    .reconfigure() 都会抛 AttributeError —— 而 oop_lab 与 oop_common 里都有这些调用。
    这里塞一个空壳把它们救回来, 是"无控制台 exe 能启动"的第一道保险。
    """
    if sys.stdout is None:
        sys.stdout = io.StringIO()
    if sys.stderr is None:
        sys.stderr = io.StringIO()


def main(argv=None) -> int:
    ensure_streams()
    # 无控制台的 exe 里, 日志文件是唯一能事后排查的地方 —— 必须一开始就打开。
    try:
        import oop_common as oc
        oc.setup_logging()
    except Exception:
        pass
    try:
        import oop_gui_app
        return oop_gui_app.main(argv)
    except Exception:
        # 窗口都起不来时, 至少把栈写进日志并弹一个消息框, 而不是双击后静默消失
        import traceback
        detail = traceback.format_exc()
        try:
            import oop_common as oc
            oc.LOG.exception("图形界面启动失败")
        except Exception:
            pass
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0, "图形界面启动失败:\n\n" + detail[-1200:], "OOP Lab", 0x10)
        except Exception:
            sys.stderr.write(detail)
        return 1


if __name__ == "__main__":
    sys.exit(main())
