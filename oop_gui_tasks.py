#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_gui_tasks.py - 后台任务执行器

图形界面的一条铁律: 编译(2~5 秒)、联网找题(可达 10 秒)、题库自检(几十秒)
绝不能跑在 Tk 主线程里 —— 否则窗口会变成"未响应", 用户以为程序死了。

这个模块只做三件事:
    run()   提交一个任务
    (后台线程) 执行它
    poll()  主线程取走结果并触发回调

它**不引用任何控件**, 所以能脱离 Tk 做单元测试 —— 这是把它单独拆出来的理由。
"""

from __future__ import annotations

import queue
import threading
from typing import Any, Callable, Optional, Tuple

import oop_common as oc

Callback = Optional[Callable[[Any], None]]


class TaskRunner:
    """串行后台任务: 同一时刻只跑一个, 结果由主线程 poll() 取走。

    刻意不做并发队列 —— 避免同时编译两份, 也避免用户连点把状态搞乱。
    正在忙的时候 run() 直接返回 False, 由界面提示"上一个任务还没结束"。
    """

    def __init__(self) -> None:
        self._queue: "queue.Queue[Tuple[bool, Any, Callback]]" = queue.Queue()
        self._busy = False
        self._label = ""
        self.last_error: Optional[BaseException] = None

    # ---- 状态 -----------------------------------------------------------
    @property
    def busy(self) -> bool:
        return self._busy

    @property
    def label(self) -> str:
        return self._label

    # ---- 提交 -----------------------------------------------------------
    def run(self, fn: Callable[[], Any], on_done: Callback = None,
            on_error: Callback = None, label: str = "") -> bool:
        """提交任务。已有任务在跑时**拒绝**并返回 False(不排队)。"""
        if self._busy:
            return False
        self._busy = True
        self._label = label or getattr(fn, "__name__", "task")
        self.last_error = None

        def worker() -> None:
            try:
                value = fn()
            except BaseException as exc:      # 必须捕获一切: 否则异常会让线程静默死掉
                self._queue.put((False, exc, on_error))
            else:
                self._queue.put((True, value, on_done))

        threading.Thread(target=worker, name="oop-gui-task", daemon=True).start()
        return True

    # ---- 主线程侧轮询 ---------------------------------------------------
    def poll(self) -> bool:
        """在主线程里调用(配合 root.after): 取走一个已完成任务并触发回调。

        返回 True 表示这次处理了一个任务 —— 界面据此刷新状态栏。
        没有任务时返回 False, 永不阻塞。
        """
        try:
            ok, value, callback = self._queue.get_nowait()
        except queue.Empty:
            return False
        self._busy = False
        self._label = ""
        if ok:
            if callback is not None:
                callback(value)
        elif callback is not None:
            callback(value)
        else:
            # 调用方没给错误回调: 记下来 + 写日志, 绝不把异常抛回 Tk 的事件循环
            self.last_error = value
            oc.LOG.warning("后台任务失败: %s", value)
        return True
