#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_judge.py - 编译与评测引擎

设计要点:
  * 双后端: MinGW-w64(g++/clang++) 与 MSVC(cl.exe)。
    MSVC 不能直接跑, 必须先进 vcvars64.bat 的编译环境, 所以这里生成一个临时
    批处理再执行 —— 比手工拼 cmd 的引号转义可靠得多(实测踩过一次)。
  * 评测比对走 oop_common.normalize_output, 容忍行尾空格与结尾空行,
    但严格比较每一行的内容与顺序。
  * 任何一步失败都不抛异常, 而是把失败原因写进报告 —— 界面层只需展示。

单独使用:
    py oop_judge.py doctor                     环境自检
    py oop_judge.py run  <源文件> [用例文件]    编译并跑一个程序
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

import oop_common as oc

DEFAULT_STD = "c++17"
DEFAULT_TIMEOUT = 10.0
COMPILE_TIMEOUT = 180.0
EXE_NAME = "main.exe" if oc.IS_WINDOWS else "main"

VERDICT_TEXT = {
    "AC": ("通过", "green"),
    "CE": ("编译失败", "red"),
    "WA": ("答案错误", "red"),
    "RE": ("运行时错误", "red"),
    "TLE": ("运行超时", "yellow"),
    "SKIP": ("无自动用例", "yellow"),
    "NA": ("未评测", "grey"),
    # 编译验证型(教材第 2~8 章的 MFC 题, 没有控制台用例)
    "COMPILED": ("编译通过", "green"),
    "STATIC": ("静态检查通过", "yellow"),
    "CHECK_FAIL": ("要点未达标", "red"),
}


# ---------------------------------------------------------------------------
# 输出解码 / 编译后端
# ---------------------------------------------------------------------------
def _decode(blob: Any) -> str:
    """把子进程的字节输出转成文本(编译器可能是 UTF-8 也可能是 GBK)。"""
    if blob is None:
        return ""
    if isinstance(blob, str):
        return blob
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return blob.decode(enc)
        except (UnicodeDecodeError, AttributeError):
            continue
    return str(blob)


class Toolchain:
    """一个可用的 C++ 编译后端。"""

    def __init__(self, kind: str, compiler: str, vcvars: Optional[str] = None,
                 label: Optional[str] = None) -> None:
        self.kind = kind                 # g++ / clang++ / cl / custom
        self.compiler = compiler
        self.vcvars = vcvars
        self.label = label or kind

    @property
    def is_msvc(self) -> bool:
        return self.kind == "cl"

    def describe(self) -> str:
        if self.is_msvc:
            return "%s  [%s]" % (self.label, self.vcvars or "找不到 vcvars64.bat")
        return "%s  [%s]" % (self.label, self.compiler)

    def __repr__(self) -> str:  # pragma: no cover - 调试用
        return "<Toolchain %s>" % self.label


def find_vcvars() -> Optional[str]:
    """定位 vcvars64.bat: 先问 vswhere, 再扫常见安装目录。"""
    env_path = os.environ.get("OOP_VCVARS")
    if env_path and os.path.isfile(env_path):
        return env_path
    if not oc.IS_WINDOWS:
        return None

    vswhere = os.path.join(
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        "Microsoft Visual Studio", "Installer", "vswhere.exe")
    if os.path.isfile(vswhere):
        try:
            proc = subprocess.run(
                [vswhere, "-latest", "-prerelease", "-products", "*",
                 "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                 "-property", "installationPath"],
                capture_output=True, timeout=30)
            for line in _decode(proc.stdout).splitlines():
                line = line.strip()
                if not line:
                    continue
                candidate = os.path.join(line, "VC", "Auxiliary", "Build", "vcvars64.bat")
                if os.path.isfile(candidate):
                    return candidate
        except (OSError, subprocess.SubprocessError):
            pass

    roots = [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        r"C:\Program Files",
        r"C:\Program Files (x86)",
    ]
    for root in roots:
        if not root:
            continue
        vs_root = os.path.join(root, "Microsoft Visual Studio")
        if not os.path.isdir(vs_root):
            continue
        try:
            years = sorted(os.listdir(vs_root), reverse=True)
        except OSError:
            continue
        for year in years:
            for edition in ("Community", "Professional", "Enterprise", "BuildTools", "Preview"):
                candidate = os.path.join(vs_root, year, edition,
                                         "VC", "Auxiliary", "Build", "vcvars64.bat")
                if os.path.isfile(candidate):
                    return candidate
    return None


def vs_root() -> str:
    """从 vcvars64.bat 的位置反推 Visual Studio 安装根目录。

    <VSROOT>\\VC\\Auxiliary\\Build\\vcvars64.bat -> 往上退四层才是 <VSROOT>。
    """
    vcvars = find_vcvars()
    if not vcvars:
        return ""
    path = vcvars
    for _ in range(4):
        path = os.path.dirname(path)
    return path


def detect_platform_toolset() -> str:
    """推断该用哪个 PlatformToolset 写进 .vcxproj。

    写死会在别的机器上报 MSB8020(找不到工具集), 所以按已安装的 MSVC 版本推断:
    14.5x -> v145(VS18) / 14.3~14.4x -> v143(VS2022) / 14.2x -> v142(VS2019) /
    14.1x -> v141(VS2017)。可用环境变量 OOP_PLATFORM_TOOLSET 覆盖。
    """
    override = os.environ.get("OOP_PLATFORM_TOOLSET")
    if override:
        return override
    tools = os.path.join(vs_root(), "VC", "Tools", "MSVC") if vs_root() else ""
    versions: List[str] = []
    if tools and os.path.isdir(tools):
        try:
            versions = sorted(os.listdir(tools), reverse=True)
        except OSError:
            versions = []
    for version in versions:
        parts = version.split(".")
        if len(parts) < 2 or not parts[0].isdigit() or not parts[1].isdigit():
            continue
        major, minor = int(parts[0]), int(parts[1])
        if major != 14:
            continue
        if minor >= 50:
            return "v145"
        if minor >= 30:                     # 14.3x / 14.4x 都是 v143
            return "v143"
        if minor >= 20:
            return "v142"
        return "v141"
    return "v143"                           # 猜不到时给个最常见的


def find_devenv() -> Optional[str]:
    """找 Visual Studio 的 devenv.exe。"""
    root = vs_root()
    if not root:
        return None
    path = os.path.join(root, "Common7", "IDE", "devenv.exe")
    return path if os.path.isfile(path) else None


def find_code_cli() -> Optional[str]:
    """找 VSCode 的 code 命令(不在 PATH 里时去常规安装位置捞一次)。"""
    found = None
    try:
        import shutil
        found = shutil.which("code") or shutil.which("code.cmd")
    except Exception:
        found = None
    if found:
        return found
    if not oc.IS_WINDOWS:
        return None
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs",
                     "Microsoft VS Code", "bin", "code.cmd"),
        r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
        r"C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs",
                     "Microsoft VS Code Insiders", "bin", "code-insiders.cmd"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def find_toolchain(prefer: Optional[str] = None) -> Optional[Toolchain]:
    """按优先级找出可用编译器; 全部找不到返回 None。"""
    override = os.environ.get("OOP_CXX")
    if override:
        return Toolchain("custom", override, label="自定义(OOP_CXX)")

    candidates: List[Toolchain] = []
    for name, kind, label in (
        ("g++", "g++", "g++ (MinGW-w64)"),
        ("clang++", "clang++", "clang++"),
    ):
        path = None
        try:
            import shutil
            path = shutil.which(name)
        except Exception:
            path = None
        if path:
            candidates.append(Toolchain(kind, path, label=label))

    if oc.IS_WINDOWS:
        vcvars = find_vcvars()
        if vcvars:
            candidates.append(Toolchain("cl", "cl.exe", vcvars=vcvars,
                                        label="MSVC (cl.exe + vcvars64)"))

    if not candidates:
        return None
    if prefer:
        for item in candidates:
            if item.kind == prefer:
                return item
    return candidates[0]


# ---------------------------------------------------------------------------
# MFC / Windows 可视化题目支持(教材第 2~8 章)
# ---------------------------------------------------------------------------
MFC_INSTALL_HINT = ("VS Installer → 修改 → 单个组件 → 勾选「适用于最新 v143 生成工具的 "
                    "C++ MFC(x86 和 x64)」后重新打开终端")


def detect_mfc() -> Optional[str]:
    """找 MFC 头文件 afxwin.h: 装了返回路径, 没装返回 None。

    教材(黄维通《Visual C++面向对象与可视化程序设计》第 5 版)第 2~8 章全部基于 MFC,
    这是「可视化题目能不能真编译」的前提。
    """
    root = vs_root()
    if not root:
        return None
    tools = os.path.join(root, "VC", "Tools", "MSVC")
    if not os.path.isdir(tools):
        return None
    try:
        versions = sorted(os.listdir(tools), reverse=True)
    except OSError:
        return None
    for version in versions:
        header = os.path.join(tools, version, "atlmfc", "include", "afxwin.h")
        if os.path.isfile(header):
            return header
    return None


def extra_compile_args(problem: Optional[Dict[str, Any]]) -> List[str]:
    """按题目声明拼 MSVC 的额外编译参数(框架宏 + 题目自定义 defines)。"""
    problem = problem or {}
    framework = str(problem.get("framework") or "console").lower()
    args: List[str] = []
    if framework == "mfc":
        # /D_AFXDLL = 动态链接 MFC(配 /MD); 刻意不强制 UNICODE ——
        # 教材示例大量直接写 "字符串字面量", 强制 UNICODE 会让它们编不过。
        args += ["/D_AFXDLL", "/DWIN32", "/D_WINDOWS", "/MD"]
    args += ["/D" + str(item) for item in problem.get("defines") or []]
    return args


def extra_link_args(problem: Optional[Dict[str, Any]]) -> str:
    """按题目声明拼 MSVC 的链接参数(子系统 + 库); 没有就返回空串。"""
    problem = problem or {}
    framework = str(problem.get("framework") or "console").lower()
    subsystem = str(problem.get("subsystem")
                    or ("windows" if framework == "mfc" else "")).lower()
    libs = [str(item) for item in problem.get("libs") or []]
    parts: List[str] = []
    if subsystem in ("windows", "console"):
        parts.append("/SUBSYSTEM:" + subsystem.upper())
        if subsystem == "windows":
            libs += ["user32.lib", "gdi32.lib"]
    if not parts and not libs:
        return ""
    return " ".join(["/link"] + parts + libs)


class CheckResult:
    """一条静态检查规则的结果(教材类题目没有控制台用例, 靠这些规则把关要点)。"""

    def __init__(self, pattern: str, hint: str, ok: bool, required: bool = True) -> None:
        self.pattern = pattern
        self.hint = hint
        self.ok = ok
        self.required = required


def run_checks(source_text: str, checks: Optional[List[Dict[str, Any]]]) -> List[CheckResult]:
    """逐条跑题目的静态检查规则(正则匹配学生源码)。纯函数, 可单测。"""
    results: List[CheckResult] = []
    for item in checks or []:
        if not isinstance(item, dict):
            continue
        pattern = str(item.get("pattern") or "")
        hint = str(item.get("hint") or "")
        required = bool(item.get("required", True))
        ok = False
        if not pattern:
            hint = hint or "规则缺少 pattern"
        else:
            try:
                ok = re.search(pattern, source_text or "") is not None
            except re.error as exc:
                hint = "正则非法: %s" % exc
        results.append(CheckResult(pattern, hint, ok, required))
    return results


def render_checks(results: List[CheckResult]) -> List[str]:
    """把静态检查结果渲染成报告行。"""
    if not results:
        return []
    lines = ["", oc.color("要点检查(对照题目要求):", "bold")]
    for index, item in enumerate(results, start=1):
        if item.ok:
            mark = oc.color("[OK]", "green")
        elif item.required:
            mark = oc.color("[X ]", "red")
        else:
            mark = oc.color("[--]", "grey")
        text = item.hint or item.pattern
        if not item.ok and not item.required:
            text += "(可选项, 未做到不影响通过)"
        lines.append("  %s %d. %s" % (mark, index, text))
    return lines


# ---------------------------------------------------------------------------
# 编译
# ---------------------------------------------------------------------------
class CompileResult:
    def __init__(self, ok: bool, exe: str = "", log: str = "",
                 seconds: float = 0.0, command: str = "") -> None:
        self.ok = ok
        self.exe = exe
        self.log = log
        self.seconds = seconds
        self.command = command


_MSVC_BAT = (
    "@echo off\r\n"
    "rem VSLANG=1033 让 MSVC 用英文报错 —— 中文报错每台机器翻译都不一样, 没法做稳定诊断\r\n"
    "set VSLANG=1033\r\n"
    'call "{vcvars}" >nul 2>&1\r\n'
    'if errorlevel 1 echo [oop_lab] 调用 vcvars64.bat 失败: {vcvars}\r\n'
    'cl /nologo /utf-8 /EHsc /std:{std} /W3 /I"{srcdir}" {extra} /Fe:"{exe}" "{src}" {link}\r\n'
    "exit /b %ERRORLEVEL%\r\n"
)


def compile_file(toolchain: Toolchain, source_path: str, build_dir: str,
                 std: str = DEFAULT_STD, timeout: float = COMPILE_TIMEOUT,
                 problem: Optional[Dict[str, Any]] = None) -> CompileResult:
    """编译单个 .cpp, 产物放到 build_dir/main.exe。

    problem 不为空时按题目声明追加参数(framework/defines/libs/subsystem):
    MFC 题需要 /D_AFXDLL 与 /SUBSYSTEM:WINDOWS, 这些都在 extra_* 里拼。
    """
    src = os.path.abspath(source_path)
    if not os.path.isfile(src):
        return CompileResult(False, log="找不到源文件: %s" % src)
    framework = str((problem or {}).get("framework") or "console").lower()
    oc.ensure_dir(build_dir)
    build_dir = os.path.abspath(build_dir)
    exe = os.path.join(build_dir, EXE_NAME)
    started = time.time()

    try:
        if toolchain.is_msvc:
            bat_path = os.path.join(build_dir, "_oop_build.bat")
            script = _MSVC_BAT.format(
                vcvars=toolchain.vcvars or "", std=std,
                srcdir=os.path.dirname(src), exe=exe, src=src,
                extra=" ".join(extra_compile_args(problem)),
                link=extra_link_args(problem))
            with open(bat_path, "w", encoding="utf-8", newline="") as fh:
                fh.write(script)
            command = [os.environ.get("COMSPEC", "cmd.exe"), "/c", bat_path]
        else:
            if framework == "mfc":
                return CompileResult(
                    False, log="这道题是 MFC 可视化题, 需要 MSVC(cl.exe); 当前编译器是 %s"
                               " —— 先跑 py oop_lab.py doctor 看安装建议" % toolchain.label)
            extra: List[str] = []
            if toolchain.kind in ("g++", "clang++"):
                extra = ["-std=" + std, "-O0", "-g", "-Wall", "-Wextra"]
            else:
                extra = []
            command = [toolchain.compiler] + extra + ["-o", exe, src]

        proc = subprocess.run(command, cwd=build_dir, capture_output=True, timeout=timeout)
        log = (_decode(proc.stdout) + _decode(proc.stderr)).strip()
        ok = proc.returncode == 0 and os.path.isfile(exe)
        return CompileResult(ok, exe if ok else "", log,
                             time.time() - started, " ".join(command))
    except subprocess.TimeoutExpired:
        return CompileResult(False, log="编译超时(%.0f 秒)" % timeout,
                             seconds=time.time() - started)
    except OSError as exc:
        return CompileResult(False, log="无法启动编译器: %s" % exc,
                             seconds=time.time() - started)


def compile_text(toolchain: Toolchain, source_text: str, work_dir: str,
                 std: str = DEFAULT_STD, file_name: str = "main.cpp",
                 problem: Optional[Dict[str, Any]] = None) -> CompileResult:
    """先落盘再编译(给 selftest 用: 把参考解写进临时目录)。"""
    oc.ensure_dir(work_dir)
    path = os.path.join(work_dir, file_name)
    try:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(source_text.replace("\r\n", "\n"))
    except OSError as exc:
        return CompileResult(False, log="写入源文件失败: %s" % exc)
    return compile_file(toolchain, path, os.path.join(work_dir, "build"), std=std,
                        problem=problem)


# ---------------------------------------------------------------------------
# 运行
# ---------------------------------------------------------------------------
class RunResult:
    def __init__(self, code: int, stdout: str = "", stderr: str = "",
                 seconds: float = 0.0, timed_out: bool = False) -> None:
        self.code = code
        self.stdout = stdout
        self.stderr = stderr
        self.seconds = seconds
        self.timed_out = timed_out

    @property
    def ok(self) -> bool:
        return (not self.timed_out) and self.code == 0


_ERROR_MODE_SET = False

# Windows: 关掉“程序已停止工作”对话框。不关的话, 学生写出野指针导致崩溃时,
# 每个用例都要等 WER 弹窗超时, 4 个用例能拖掉 20 多秒。
_SEM_FAILCRITICALERRORS = 0x0001
_SEM_NOGPFAULTERRORBOX = 0x0002


def _suppress_error_dialogs() -> None:
    global _ERROR_MODE_SET
    if _ERROR_MODE_SET or not oc.IS_WINDOWS:
        return
    _ERROR_MODE_SET = True
    try:
        import ctypes
        ctypes.WinDLL("kernel32", use_last_error=True).SetErrorMode(
            _SEM_FAILCRITICALERRORS | _SEM_NOGPFAULTERRORBOX)
    except Exception:  # pragma: no cover - 拿不到就算了
        pass


def exit_code_text(code: int) -> str:
    """把退出码写成人能看懂的形式(Windows 的崩溃码是 0xC0000xxx 这种)。"""
    if code < 0:
        return "无退出码"
    if code > 255:
        return "退出码 %d (0x%08X)" % (code, code)
    return "退出码 %d" % code


def crash_hint(code: int) -> str:
    """Windows 上的几个经典崩溃码 -> 一句话解释。"""
    hints = {
        0xC0000005: "访问冲突: 读写了一个非法地址(空指针 / 越界 / 已释放的内存)",
        0xC00000FD: "栈溢出: 很可能是递归没有终止条件",
        0xC0000374: "堆损坏: 几乎一定是重复释放或越界写(深拷贝没写?)",
        0xC0000409: "栈缓冲区越界被安全检查拦下",
        0xC0000094: "整数除零",
    }
    return hints.get(code & 0xFFFFFFFF, "")


def run_binary(exe: str, stdin_text: str = "", timeout: float = DEFAULT_TIMEOUT,
               cwd: Optional[str] = None) -> RunResult:
    """用字节流喂输入, 避免 Windows 区域设置把中文输入转码转坏。"""
    _suppress_error_dialogs()
    data = (stdin_text or "").encode("utf-8")
    started = time.time()
    try:
        proc = subprocess.run([exe], input=data, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout, cwd=cwd)
        return RunResult(proc.returncode, _decode(proc.stdout), _decode(proc.stderr),
                         time.time() - started)
    except subprocess.TimeoutExpired as exc:
        return RunResult(-1, _decode(getattr(exc, "stdout", None)), "运行超时",
                         time.time() - started, timed_out=True)
    except OSError as exc:
        return RunResult(-1, "", "无法运行程序: %s" % exc, time.time() - started)


# ---------------------------------------------------------------------------
# 评测报告
# ---------------------------------------------------------------------------
class CaseResult:
    def __init__(self, index: int, ok: bool, expected: str = "", actual: str = "",
                 line: int = 0, exp_line: str = "", act_line: str = "",
                 seconds: float = 0.0, verdict: str = "AC", detail: str = "") -> None:
        self.index = index
        self.ok = ok
        self.expected = expected
        self.actual = actual
        self.line = line
        self.exp_line = exp_line
        self.act_line = act_line
        self.seconds = seconds
        self.verdict = verdict
        self.detail = detail


class JudgeReport:
    def __init__(self) -> None:
        self.toolchain_label = ""
        self.compiled = False
        self.compile_log = ""
        self.compile_seconds = 0.0
        self.cases: List[CaseResult] = []
        self.seconds = 0.0
        self.source_path = ""
        self.checks: List[CheckResult] = []      # 静态检查结果(教材类题目)
        self.static_only = False                 # True: 未真编译, 只看静态检查
        self.static_reason = ""                  # "" | "mfc_missing" | "needs_resource"

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.cases if c.ok)

    @property
    def checks_passed(self) -> bool:
        required = [c for c in self.checks if c.required]
        return bool(required) and all(c.ok for c in required)

    @property
    def verdict(self) -> str:
        if self.static_only:
            return "STATIC" if self.checks_passed else "CHECK_FAIL"
        if not self.compiled:
            return "CE"
        if not self.cases:
            # 编译验证型(GUI/MFC 题): 编译通过; 有 checks 时它们决定成败
            return "COMPILED" if (not self.checks or self.checks_passed) else "CHECK_FAIL"
        for case in self.cases:
            if case.verdict != "AC":
                return case.verdict
        return "AC"

    @property
    def all_passed(self) -> bool:
        if self.static_only:
            return self.checks_passed
        if not (self.compiled and bool(self.cases) and self.passed == self.total):
            return False
        return not self.checks or self.checks_passed

    def failures(self) -> List[CaseResult]:
        return [c for c in self.cases if not c.ok]


def judge(problem: Dict[str, Any], source_path: str, toolchain: Optional[Toolchain] = None,
          timeout: float = DEFAULT_TIMEOUT, build_dir: Optional[str] = None) -> JudgeReport:
    """编译学生代码并跑完题库里全部用例; MFC 题在没有 MFC 组件时降级为静态检查。"""
    report = JudgeReport()
    report.source_path = os.path.abspath(source_path)
    started = time.time()

    source_text = ""
    try:
        with open(report.source_path, encoding="utf-8", errors="replace") as fh:
            source_text = fh.read()
    except OSError:
        source_text = ""
    report.checks = run_checks(source_text, problem.get("checks"))

    framework = str(problem.get("framework") or "console").lower()
    needs_resource = bool(problem.get("needs_resource"))
    if framework == "mfc" and (needs_resource or detect_mfc() is None):
        # 两种情况都改为「要点检查」:
        #   1) needs_resource 的题(如对话框)需要 .rc 资源工程, 纯 main.cpp 编不过;
        #   2) 没装 MFC 组件, 编译不了。
        report.static_only = True
        report.static_reason = "needs_resource" if needs_resource else "mfc_missing"
        report.toolchain_label = ("未编译(需要 .rc 资源工程)" if needs_resource
                                  else "未编译(缺 MFC 组件)")
        report.seconds = time.time() - started
        return report

    chain = toolchain or find_toolchain()
    if chain is None:
        report.compile_log = "没有找到可用的 C++ 编译器"
        report.seconds = time.time() - started
        return report
    report.toolchain_label = chain.label

    target_build = build_dir or os.path.join(os.path.dirname(report.source_path), "build")
    compiled = compile_file(chain, report.source_path, target_build,
                            timeout=COMPILE_TIMEOUT, problem=problem)
    report.compiled = compiled.ok
    report.compile_log = compiled.log
    report.compile_seconds = compiled.seconds
    report.seconds = time.time() - started
    if not compiled.ok:
        return report

    tests = problem.get("tests") or []
    if not tests:
        # 编译验证型(MFC / 窗口程序没有控制台用例): 编译通过即完成, checks 决定成败
        return report
    for index, test in enumerate(tests, start=1):
        expected = test.get("out", "")
        run = run_binary(compiled.exe, test.get("in", ""), timeout=timeout,
                         cwd=target_build)
        if run.timed_out:
            report.cases.append(CaseResult(index, False, expected, run.stdout,
                                           seconds=run.seconds, verdict="TLE",
                                           detail="超过 %.1f 秒仍未结束" % timeout))
            continue
        if run.code != 0:
            detail = exit_code_text(run.code)
            hint = crash_hint(run.code) if run.code > 255 else ""
            if hint:
                detail += " | " + hint
            if run.stderr.strip():
                detail += " | stderr: " + run.stderr.strip().splitlines()[-1][:160]
            report.cases.append(CaseResult(index, False, expected, run.stdout,
                                           seconds=run.seconds, verdict="RE", detail=detail))
            continue
        ok = oc.normalize_output(expected) == oc.normalize_output(run.stdout)
        line, exp_line, act_line = (0, "", "") if ok else oc.first_difference(expected, run.stdout)
        report.cases.append(CaseResult(index, ok, expected, run.stdout, line,
                                       exp_line, act_line, run.seconds,
                                       "AC" if ok else "WA"))
    report.seconds = time.time() - started
    return report


def verify_solution(problem: Dict[str, Any], toolchain: Optional[Toolchain] = None,
                    work_dir: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT) -> JudgeReport:
    """用题目自带的参考解跑一遍用例 —— 题库自检(selftest)靠它。"""
    import tempfile
    report = JudgeReport()
    chain = toolchain or find_toolchain()
    if chain is None:
        report.compile_log = "没有找到可用的 C++ 编译器"
        return report
    report.toolchain_label = chain.label

    tmp = work_dir or tempfile.mkdtemp(prefix="oop_selftest_")
    solution = problem.get("solution") or ""
    if not solution.strip():
        report.compile_log = "本题没有参考解"
        return report
    # MFC 题: 没装 MFC 组件、或题目需要 .rc 资源工程时无法真编译, 明确跳过
    # (selftest 汇总里单独统计); 但参考解仍要过一遍 checks —— 规则写错了要当场发现。
    framework = str(problem.get("framework") or "console").lower()
    needs_resource = bool(problem.get("needs_resource"))
    if framework == "mfc" and (needs_resource or detect_mfc() is None):
        report.static_only = True
        report.static_reason = "needs_resource" if needs_resource else "mfc_missing"
        report.checks = run_checks(solution, problem.get("checks"))
        report.compile_log = ("跳过: 本题需要 .rc 资源工程(在 VS 里用资源编辑器建)"
                              if needs_resource else
                              "跳过: 未安装 MFC 组件——" + MFC_INSTALL_HINT)
        return report
    compiled = compile_text(chain, solution, tmp, problem=problem)
    report.compiled = compiled.ok
    report.compile_log = compiled.log
    report.compile_seconds = compiled.seconds
    if not compiled.ok:
        return report

    for index, test in enumerate(problem.get("tests") or [], start=1):
        expected = test.get("out", "")
        run = run_binary(compiled.exe, test.get("in", ""), timeout=timeout, cwd=tmp)
        if run.timed_out:
            report.cases.append(CaseResult(index, False, expected, run.stdout,
                                           verdict="TLE", seconds=run.seconds))
            continue
        if run.code != 0:
            detail = exit_code_text(run.code)
            hint = crash_hint(run.code) if run.code > 255 else ""
            report.cases.append(CaseResult(index, False, expected, run.stdout,
                                           verdict="RE", seconds=run.seconds,
                                           detail=(detail + " | " + hint) if hint else detail))
            continue
        ok = oc.normalize_output(expected) == oc.normalize_output(run.stdout)
        line, exp_line, act_line = (0, "", "") if ok else oc.first_difference(expected, run.stdout)
        report.cases.append(CaseResult(index, ok, expected, run.stdout, line,
                                       exp_line, act_line, run.seconds,
                                       "AC" if ok else "WA"))
    return report


# ---------------------------------------------------------------------------
# 报告渲染
# ---------------------------------------------------------------------------
def verdict_badge(verdict: str) -> str:
    text, color = VERDICT_TEXT.get(verdict, ("未知", "grey"))
    return oc.color("[%s] %s" % (verdict, text), color)


def render_report(report: JudgeReport, max_diff: int = 3,
                  show_output: bool = False) -> List[str]:
    """把评测报告渲染成可直接打印的行列表。"""
    lines: List[str] = []
    lines.append("编译器: %s" % (report.toolchain_label or "无"))
    lines.append("编译耗时: %s" % oc.human_duration(report.compile_seconds))

    if report.static_only:
        lines.append("")
        if report.static_reason == "needs_resource":
            lines.append(oc.color(
                "本题需要 .rc 资源工程(VS 里用资源编辑器建对话框/控件资源), "
                "纯 main.cpp 跳过编译 —— 只做要点检查。", "yellow"))
        else:
            lines.append(oc.color("未安装 MFC 组件, 本次跳过编译 —— 只做要点检查。", "yellow"))
            lines.append("     · 安装后可真编译: " + MFC_INSTALL_HINT)
        if report.checks:
            lines.extend(render_checks(report.checks))
        else:
            lines.append("     · 本题没有检查规则, 请对照题目要求自己核对。")
        return lines

    if not report.compiled:
        lines.append("")
        lines.append(oc.color("编译失败(CE)", "red") + " —— 先修好编译错误再提交:")
        lines.append(oc.hr("-", 72))
        for row in (report.compile_log or "(编译器没有输出)").splitlines()[:40]:
            lines.append("  " + row)
        lines.append(oc.hr("-", 72))
        lines.extend(render_checks(report.checks))
        return lines

    if not report.cases:
        lines.append("")
        if report.checks:
            lines.append(oc.color("编译通过。本题没有控制台用例, 以下是要点检查:", "yellow"))
            lines.extend(render_checks(report.checks))
        else:
            lines.append(oc.color("编译通过。本题没有自动评测用例, 请按题目要求自行验证。", "yellow"))
        return lines

    lines.append("")
    for case in report.cases:
        head = "%s 用例 %d/%d" % (verdict_badge(case.verdict).ljust(28), case.index, report.total)
        if case.ok:
            lines.append(head + oc.color("  %.0f ms" % (case.seconds * 1000), "grey"))
            if show_output:
                for row in oc.normalize_output(case.actual).splitlines()[:20]:
                    lines.append("      " + row)
        else:
            lines.append(head + "  " + oc.color(case.detail or "输出不一致", "grey"))
    lines.append("")
    summary = "通过 %d/%d 个用例, 总耗时 %s" % (
        report.passed, report.total, oc.human_duration(report.seconds))
    lines.append(summary)

    shown = 0
    for case in report.failures():
        if shown >= max_diff:
            rest = len(report.failures()) - shown
            if rest > 0:
                lines.append(oc.color("  ... 还有 %d 个用例没通过" % rest, "grey"))
            break
        shown += 1
        if case.verdict == "WA":
            lines.append("")
            lines.append(oc.color("用例 %d 的差异(第 %d 行):" % (case.index, case.line), "yellow"))
            lines.append("  期望: " + repr(case.exp_line))
            lines.append("  实际: " + repr(case.act_line))
        elif case.detail:
            lines.append("")
            lines.append(oc.color("用例 %d: " % case.index, "yellow") + case.detail)
    return lines


def doctor(verbose: bool = True) -> Tuple[bool, List[str]]:
    """环境自检: 是否有编译器 / 版本 / 建议。"""
    lines: List[str] = []
    ok = True

    lines.append(oc.color("== C++ 工具链自检 ==", "bold"))
    chain = find_toolchain()
    if chain is None:
        ok = False
        lines.append("%s 没有找到任何 C++ 编译器" % oc.color("[!!]", "red"))
        lines.append("     · 推荐安装 MinGW-w64 (勾选 posix 线程, 加进 PATH), 或")
        lines.append("     · 安装 Visual Studio 2022/2026 并勾选 “使用 C++ 的桌面开发”")
        lines.append("     · 也可以设置环境变量 OOP_CXX 指向编译器, OOP_VCVARS 指向 vcvars64.bat")
    else:
        lines.append("%s 编译器      %s" % (oc.color("[OK]", "green"), chain.describe()))
        label = chain.label
        for prefer in ("g++", "clang++", "cl"):
            other = find_toolchain(prefer)
            if other and other.kind != chain.kind:
                lines.append("%s 也可用      %s" % (oc.color("[--]", "grey"), other.describe()))
                break
        if chain.is_msvc:
            lines.append("     · MSVC 只能通过 vcvars64.bat 环境使用, 评测脚本已自动处理")

    lines.append("")
    lines.append(oc.color("== 目录 ==", "bold"))
    lines.append("题库目录: %s" % oc.BASE_DIR)
    lines.append("练习工作区: %s" % oc.WORKSPACE_DIR)
    lines.append("进度文件: %s" % oc.PROGRESS_FILE)

    lines.append("")
    lines.append(oc.color("== 编辑器 ==", "bold"))
    code_cli = find_code_cli()
    if code_cli:
        lines.append("%s VSCode code 命令可用: %s" % (oc.color("[OK]", "green"), code_cli))
    else:
        lines.append("%s 没找到 code 命令 —— 不影响做题, 只是没法自动打开工作区"
                     % oc.color("[--]", "grey"))
        lines.append("     · VSCode 里 Ctrl+Shift+P → “Shell 命令: 安装 code 命令”")
    devenv = find_devenv()
    if devenv:
        lines.append("%s Visual Studio 可用: %s" % (oc.color("[OK]", "green"), devenv))
        lines.append("     生成的 VS 工程平台工具集: %s" % detect_platform_toolset())
    else:
        lines.append("%s 没找到 Visual Studio(devenv.exe) —— 只用 VSCode 的话可以忽略"
                     % oc.color("[--]", "grey"))
    lines.append("     练习工作区同时带 VSCode 配置(.vscode)和 VS 解决方案(oop_lab.sln), 两边都能 F5")

    lines.append("")
    lines.append(oc.color("== MFC 可视化支持(教材第 2~8 章) ==", "bold"))
    mfc = detect_mfc()
    if mfc:
        lines.append("%s MFC 可用: %s" % (oc.color("[OK]", "green"), mfc))
        lines.append("     · 第 2~8 章的 MFC 题目可以直接真编译验证")
    else:
        lines.append("%s 未安装 MFC 组件 —— MFC 题目只做要点检查, 不能真编译"
                     % oc.color("[!]", "yellow"))
        lines.append("     · 安装方法: " + MFC_INSTALL_HINT)
        lines.append("     · 装好后重开终端再跑一次 doctor 确认即可")

    return ok, lines


def main(argv: Optional[Sequence[str]] = None) -> int:
    """供直接调用: py oop_judge.py doctor | run <src> [casefile]"""
    oc.setup_logging()
    oc.enable_ansi()
    args = list(argv if argv is not None else sys.argv[1:])
    action = args[0] if args else "doctor"

    if action == "doctor":
        ok, lines = doctor()
        for row in lines:
            print(row)
        return 0 if ok else 1

    if action == "run" and len(args) >= 2:
        chain = find_toolchain()
        if chain is None:
            print("没有找到 C++ 编译器")
            return 1
        src = args[1]
        stdin_text = ""
        if len(args) >= 3 and os.path.isfile(args[2]):
            stdin_text = oc.read_text(args[2])
        built = compile_file(chain, src, os.path.join(os.path.dirname(os.path.abspath(src)), "build"))
        if not built.ok:
            print("编译失败:")
            print(built.log)
            return 1
        run = run_binary(built.exe, stdin_text)
        print(run.stdout, end="")
        if run.stderr.strip():
            print("[stderr] " + run.stderr.strip(), file=sys.stderr)
        return run.code

    print(__doc__)
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
