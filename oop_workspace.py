#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_workspace.py - 统一练习工作区(VSCode + Visual Studio 通用)

整个题库只有**一个**工作区, 不再是一题一套配置:

    workspace/                            ← VSCode 打开这一个文件夹就够
    ├── oop_lab.code-workspace            ← 想让 VSCode 双击打开就用它
    ├── oop_lab.sln                       ← Visual Studio 打开这个
    ├── build.bat / run_case.bat          ← 全题库共用(接收参数, 不写死题目)
    ├── .vscode/                          ← 全题库共用的任务与调试配置
    │   ├── tasks.json    构建/运行当前打开的文件
    │   ├── launch.json   调试当前打开的文件
    │   ├── c_cpp_properties.json
    │   ├── settings.json / extensions.json
    └── b01-student-class/                ← 每道题只是一个子文件夹
        ├── knowledge.md                  ← 知识点讲义(先读这个)
        ├── problem.md                    ← 题面(顶部会指向 knowledge.md)
        ├── main.cpp                      ← 你要写的东西
        ├── tests/01.in 01.out ...        ← 评测用例
        └── b01-student-class.vcxproj     ← VS 工程(由 oop_lab.sln 引用)

关键在于**所有配置都是相对当前打开的文件**写的:
VSCode 里切到哪道题的 main.cpp, Ctrl+Shift+B 就编译哪个、F5 就调试哪个;
VS 里在解决方案资源管理器里把任意题目设为启动项目即可。两边的产物路径都是
``<题目目录>/build/main.exe``, 与 ``py oop_lab.py judge`` 完全一致。
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Sequence, Tuple

import oop_common as oc
import oop_judge
import oop_skills

TESTS_DIRNAME = "tests"
BUILD_DIRNAME = "build"
SOURCE_NAME = "main.cpp"
SUBMISSION_NAME = "submission.md"
KNOWLEDGE_NAME = "knowledge.md"
PROBLEM_MD_NAME = "problem.md"
SOLUTION_NAME = "oop_lab.sln"
CODE_WORKSPACE_NAME = "oop_lab.code-workspace"

# 每题最多生成几个「运行用例」任务(避免任务列表太长)
MAX_RUN_TASKS = 4


# ---------------------------------------------------------------------------
# 通用小工具
# ---------------------------------------------------------------------------
def project_guid(name: str) -> str:
    """由题目目录名生成**确定性**的 GUID, 反复生成 sln 不会变来变去。"""
    digest = uuid.uuid5(uuid.NAMESPACE_URL, "cpp-oop-lab/%s" % name).hex.upper()
    return "{%s-%s-%s-%s-%s}" % (digest[0:8], digest[8:12], digest[12:16],
                                 digest[16:20], digest[20:32])


def write_bat(path: str, text: str) -> bool:
    """写 .bat 文件。

    两个必须遵守的点(都是实测踩出来的):

    1. **内容只能是 ASCII**。cmd.exe 按控制台代码页(中文系统是 GBK)逐行解析批处理,
       UTF-8 的中文注释会被解码成乱码, 甚至把一行拆成几条命令去执行 —— 脚本直接报废。
       所以 .bat 里一律写英文, 中文说明放在 README / problem.md 里。
    2. **换行必须是 CRLF**。批处理按字节找行尾, LF-only 在部分场景(标签、括号块)会出错。
    """
    try:
        oc.ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="ascii", errors="replace", newline="") as fh:
            fh.write(text.replace("\r\n", "\n").replace("\n", "\r\n"))
        return True
    except OSError:
        return False


def write_text_crlf(path: str, text: str) -> bool:
    """写 CRLF 文本(用于 .sln / .vcxproj, Visual Studio 只认 Windows 换行)。"""
    try:
        oc.ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text.replace("\r\n", "\n").replace("\n", "\r\n"))
        return True
    except OSError:
        return False


# VS / VSCode 的环境探测统一放在 oop_judge 里 —— oop_workspace 已经依赖它,
# 反向依赖会形成循环导入。这里只是把名字再导出一次, 方便调用与测试。
_vs_root = oop_judge.vs_root
detect_platform_toolset = oop_judge.detect_platform_toolset
find_code_cli = oop_judge.find_code_cli
find_devenv = oop_judge.find_devenv


# ---------------------------------------------------------------------------
# 题面 / 知识点讲义
# ---------------------------------------------------------------------------
def problem_skills(problem: Dict[str, Any]) -> List[str]:
    """这道题涉及哪些知识点(至少一个, 兜底 K01)。"""
    ids = oop_skills.classify(problem.get("topics", []))
    return ids or ["K01"]


def knowledge_markdown(problem: Dict[str, Any]) -> str:
    """做题之前先看的那份知识点讲义。"""
    ids = problem_skills(problem)
    names = "、".join("%s %s" % (sid, oop_skills.skill_name(sid)) for sid in ids)
    lines = [
        "# 先学后练 · %s %s" % (problem["id"].upper(), problem["title"]),
        "",
        "> 建议先花 5~10 分钟把这一页读完, 再打开 `main.cpp` 动手。",
        "> 卡住的时候回到这里对照「要点」和「常见坑」。",
        "",
        "| 项目 | 内容 |",
        "| --- | --- |",
        "| 本题知识点 | %s |" % names,
        "| 难度 | %s %s |" % (
            oc.LEVEL_STARS.get(int(problem.get("level", 1)), "???"),
            oc.LEVEL_NAMES.get(int(problem.get("level", 1)), "")),
        "",
        "---",
        "",
        oop_skills.teach_markdown(ids),
        "",
        "## 学完了?",
        "",
        "回到 [problem.md](problem.md) 看题目要求, 然后编辑 `main.cpp`。",
        "",
        "- VSCode: `Ctrl+Shift+B` 构建, `F5` 调试(会自动先构建)",
        "- Visual Studio: 把本工程设为启动项目, `F5` 调试",
        "- 命令行评测: `py oop_lab.py judge %s`" % problem["id"],
        "",
    ]
    return "\n".join(lines)


def problem_markdown(problem: Dict[str, Any]) -> str:
    level = int(problem.get("level", 3))
    ids = problem_skills(problem)
    lines: List[str] = []
    lines.append("# %s %s" % (problem["id"].upper(), problem["title"]))
    lines.append("")
    lines.append("> **先学后练**：本页只讲题目。动手之前请先读 "
                 "[knowledge.md](knowledge.md) —— 里面是本题涉及的 "
                 "%s 共 %d 个知识点的完整讲解、示例与常见坑。"
                 % ("、".join(ids), len(ids)))
    lines.append("")
    lines.append("| 项目 | 内容 |")
    lines.append("| --- | --- |")
    lines.append("| 难度 | %s %s |" % (oc.LEVEL_STARS.get(level, "???"),
                                        oc.LEVEL_NAMES.get(level, "")))
    lines.append("| 知识点 | %s |" % (" / ".join(problem.get("topics", [])) or "—"))
    lines.append("| 自动用例 | %d 组 |" % len(problem.get("tests", [])))
    if problem.get("url"):
        lines.append("| 来源 | %s |" % problem["url"])
    lines.append("")

    if problem.get("desc"):
        lines.append("## 题目描述")
        lines.append("")
        lines.append(problem["desc"])
        lines.append("")

    if problem.get("require"):
        lines.append("## 具体要求")
        lines.append("")
        for index, item in enumerate(problem["require"], start=1):
            lines.append("%d. %s" % (index, item))
        lines.append("")

    if problem.get("io"):
        lines.append("## 输入输出")
        lines.append("")
        lines.append(problem["io"])
        lines.append("")

    samples = problem.get("samples") or problem.get("tests") or []
    if samples:
        lines.append("## 样例")
        lines.append("")
        for index, sample in enumerate(samples[:3], start=1):
            lines.append("### 样例 %d" % index)
            lines.append("")
            lines.append("输入")
            lines.append("```text")
            lines.append((sample.get("in") or "").rstrip("\n") or "(无输入)")
            lines.append("```")
            lines.append("输出")
            lines.append("```text")
            lines.append((sample.get("out") or "").rstrip("\n"))
            lines.append("```")
            lines.append("")

    if problem.get("hints"):
        lines.append("## 提示")
        lines.append("")
        for item in problem["hints"]:
            lines.append("- %s" % item)
        lines.append("")

    if problem.get("checklist"):
        lines.append("## 完成前自查(面向对象要点)")
        lines.append("")
        for item in problem["checklist"]:
            lines.append("- [ ] %s" % item)
        lines.append("")

    lines.append("## 怎么练")
    lines.append("")
    lines.append("1. 先读 [knowledge.md](knowledge.md) 里的知识点讲解。")
    lines.append("2. 编辑 `main.cpp`, 把 `TODO` 那一段补完(题目给的 `main` 不要改)。")
    lines.append("3. VSCode: `Ctrl+Shift+B` 构建 → `F5` 调试; "
                 "想跑某一组用例: `终端 → 运行任务 → 运行当前题 · 用例 N`。")
    lines.append("4. Visual Studio: 打开工作区里的 `oop_lab.sln`, "
                 "把本工程设为启动项目后 `F5`。")
    lines.append("5. 命令行一步到位:")
    lines.append("")
    lines.append("```bat")
    lines.append("py oop_lab.py judge %s        :: 评测 + 老师式诊断" % problem["id"])
    lines.append("py oop_lab.py review %s       :: 写法审查" % problem["id"])
    lines.append("py oop_lab.py study %s        :: 再看一遍知识点讲义" % problem["id"])
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 统一构建脚本(放在工作区根, 全题库共用)
# ---------------------------------------------------------------------------
def build_bat_msvc(vcvars: str, std: str = oop_judge.DEFAULT_STD) -> str:
    """共用构建脚本(MSVC): 参数是要编译的 .cpp。内容必须是纯 ASCII, 见 write_bat()。

    用 .format() 而不是 % 格式化 —— 批处理里满是 %~dp0 / %ERRORLEVEL%,
    用 % 格式化会直接抛 ValueError(实测踩过一次)。
    """
    return (
        "@echo off\n"
        "rem oop_lab unified build script (shared by all problems)\n"
        "rem usage: build.bat [source.cpp]  -- VSCode task passes the opened file\n"
        "rem note: do NOT put < or > in rem lines, cmd treats them as redirection\n"
        "setlocal\n"
        "rem English compiler messages: same wording as `py oop_lab.py judge`\n"
        "set VSLANG=1033\n"
        'if "%~1"=="" (\n'
        "  echo [build] usage: build.bat ^<source.cpp^>\n"
        "  exit /b 2\n"
        ")\n"
        'set "SRC=%~f1"\n'
        'for %%I in ("%SRC%") do (set "SRCDIR=%%~dpI" & set "NAME=%%~nI")\n'
        "rem %%~dpI always ends with a backslash; strip it -- otherwise /I\"...\\\"\n"
        "rem would escape the closing quote and cl would see no source file at all\n"
        'if "%SRCDIR:~-1%"=="\\" set "SRCDIR=%SRCDIR:~0,-1%"\n'
        'if not exist "%SRCDIR%\\' + BUILD_DIRNAME + '" mkdir "%SRCDIR%\\' + BUILD_DIRNAME + '"\n'
        "rem MFC problems (textbook ch.2-8): if the source includes afx headers,\n"
        "rem add the MFC flags automatically (same as py oop_lab.py judge)\n"
        'set "MFC_OPTS="\n'
        'set "MFC_LINK="\n'
        'findstr /c:"<afx" "%SRC%" >nul 2>&1\n'
        "if not errorlevel 1 (\n"
        '  set "MFC_OPTS=/D_AFXDLL /MD /D_WINDOWS"\n'
        '  set "MFC_LINK=/link /SUBSYSTEM:WINDOWS user32.lib gdi32.lib"\n'
        ")\n"
        'call "{vcvars}" >nul 2>&1\n'
        "if errorlevel 1 (\n"
        '  echo [build] failed to call vcvars64.bat: {vcvars}\n'
        "  exit /b 1\n"
        ")\n"
        'cd /d "%SRCDIR%\\' + BUILD_DIRNAME + '"\n'
        'cl /nologo /utf-8 /EHsc /std:{std} /W3 /I"%SRCDIR%" %MFC_OPTS% /Fe:"%NAME%.exe" "%SRC%" %MFC_LINK%\n'
        "exit /b %ERRORLEVEL%\n"
    ).format(vcvars=vcvars, std=std)


def build_bat_gcc(compiler: str, std: str = oop_judge.DEFAULT_STD) -> str:
    """共用构建脚本(MinGW / clang 版)。"""
    return (
        "@echo off\n"
        "rem oop_lab unified build script (shared by all problems)\n"
        "rem usage: build.bat [source.cpp]\n"
        "setlocal\n"
        'if "%~1"=="" (\n'
        "  echo [build] usage: build.bat ^<source.cpp^>\n"
        "  exit /b 2\n"
        ")\n"
        'set "SRC=%~f1"\n'
        'for %%I in ("%SRC%") do (set "SRCDIR=%%~dpI" & set "NAME=%%~nI")\n'
        "rem %%~dpI always ends with a backslash; strip it for consistent quoting\n"
        'if "%SRCDIR:~-1%"=="\\" set "SRCDIR=%SRCDIR:~0,-1%"\n'
        'if not exist "%SRCDIR%\\' + BUILD_DIRNAME + '" mkdir "%SRCDIR%\\' + BUILD_DIRNAME + '"\n'
        '"{compiler}" -std={std} -O0 -g -Wall -Wextra '
        '-o "%SRCDIR%\\' + BUILD_DIRNAME + '\\%NAME%.exe" "%SRC%"\n'
        "exit /b %ERRORLEVEL%\n"
    ).format(compiler=compiler, std=std)


def run_case_bat() -> str:
    """跑某道题的某一组用例: run_case.bat <problem-dir> <case-no>"""
    return (
        "@echo off\n"
        "rem oop_lab: run one test case\n"
        "rem usage: run_case.bat [problem-dir] [case-no]\n"
        "setlocal\n"
        'set "DIR=%~f1"\n'
        'set "N=%~2"\n'
        'if "%DIR%"=="" (\n'
        "  echo [run] usage: run_case.bat ^<problem-dir^> ^<case-no^>\n"
        "  exit /b 2\n"
        ")\n"
        'if "%N%"=="" set "N=1"\n'
        'set "PAD=0%N%"\n'
        "if %N% GEQ 10 set \"PAD=%N%\"\n"
        'set "IN=%DIR%\\' + TESTS_DIRNAME + '\\%PAD%.in"\n'
        'if not exist "%IN%" (\n'
        "  echo [run] no such test case: %IN%\n"
        "  exit /b 2\n"
        ")\n"
        'if not exist "%DIR%\\' + BUILD_DIRNAME + '\\main.exe" (\n'
        '  call "%~dp0build.bat" "%DIR%\\' + SOURCE_NAME + '"\n'
        "  if errorlevel 1 exit /b 1\n"
        ")\n"
        "echo [run] input file: %IN%\n"
        '"%DIR%\\' + BUILD_DIRNAME + '\\main.exe" < "%IN%"\n'
        "exit /b %ERRORLEVEL%\n"
    )


# ---------------------------------------------------------------------------
# 工作区配置
# ---------------------------------------------------------------------------
def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def _build_task_label() -> str:
    return "构建当前文件"


def _run_task_label(index: int) -> str:
    return "运行当前题 · 用例 %d" % index


def tasks_json(toolchain: Optional[oop_judge.Toolchain]) -> str:
    """全题库共用: 所有命令都以「当前打开的文件」为参数。"""
    matcher = ["$msCompile"] if (toolchain and toolchain.is_msvc) else ["$gcc"]
    tasks: List[Dict[str, Any]] = [{
        "label": _build_task_label(),
        "type": "shell",
        "command": "${workspaceFolder}\\build.bat",
        "args": ["${file}"],
        "options": {"cwd": "${workspaceFolder}"},
        "group": {"kind": "build", "isDefault": True},
        "problemMatcher": matcher,
        "presentation": {"reveal": "always", "panel": "shared", "clear": True},
        "detail": "编译当前打开的 .cpp 到 <题目目录>/build/<名字>.exe",
    }]
    for index in range(1, MAX_RUN_TASKS + 1):
        tasks.append({
            "label": _run_task_label(index),
            "type": "shell",
            "command": "${workspaceFolder}\\run_case.bat",
            "args": ["${fileDirname}", str(index)],
            "dependsOn": _build_task_label(),
            "options": {"cwd": "${workspaceFolder}"},
            "group": "test",
            "problemMatcher": [],
            "presentation": {"reveal": "always", "panel": "shared", "clear": True},
            "detail": "用 tests/%02d.in 作为输入运行当前题目" % index,
        })
    return _json({"version": "2.0.0", "tasks": tasks})


def launch_json(toolchain: Optional[oop_judge.Toolchain]) -> str:
    program = "${fileDirname}/%s/${fileBasenameNoExtension}.exe" % BUILD_DIRNAME
    if toolchain and toolchain.is_msvc:
        config = {
            "name": "调试当前文件 (MSVC)",
            "type": "cppvsdbg",
            "request": "launch",
            "program": program,
            "args": [],
            "stopAtEntry": False,
            "cwd": "${fileDirname}/%s" % BUILD_DIRNAME,
            "environment": [],
            "console": "externalTerminal",
            "preLaunchTask": _build_task_label(),
        }
    else:
        config = {
            "name": "调试当前文件 (gdb)",
            "type": "cppdbg",
            "request": "launch",
            "program": program,
            "args": [],
            "stopAtEntry": False,
            "cwd": "${fileDirname}/%s" % BUILD_DIRNAME,
            "environment": [],
            "externalConsole": True,
            "MIMode": "gdb",
            "miDebuggerPath": "gdb.exe",
            "setupCommands": [{
                "description": "为 gdb 启用整齐打印",
                "text": "-enable-pretty-printing",
                "ignoreFailures": True,
            }],
            "preLaunchTask": _build_task_label(),
        }
    return _json({"version": "0.2.0", "configurations": [config]})


def c_cpp_properties_json(toolchain: Optional[oop_judge.Toolchain]) -> str:
    if toolchain and toolchain.is_msvc:
        config = {
            "name": "Win32",
            "includePath": ["${workspaceFolder}/**"],
            "defines": ["_DEBUG", "UNICODE", "_UNICODE"],
            "compilerPath": "",
            "cStandard": "c17",
            "cppStandard": "c++17",
            "intelliSenseMode": "windows-msvc-x64",
            "compilerArgs": ["/utf-8"],
        }
    elif toolchain:
        config = {
            "name": "Win32",
            "includePath": ["${workspaceFolder}/**"],
            "defines": [],
            "compilerPath": toolchain.compiler,
            "cStandard": "c17",
            "cppStandard": "c++17",
            "intelliSenseMode": "windows-gcc-x64",
        }
    else:
        config = {
            "name": "Win32",
            "includePath": ["${workspaceFolder}/**"],
            "defines": [],
            "compilerPath": "",
            "cStandard": "c17",
            "cppStandard": "c++17",
            "intelliSenseMode": "windows-msvc-x64",
        }
    return _json({"version": 4, "configurations": [config]})


def settings_json() -> str:
    return _json({
        "files.encoding": "utf8",
        "files.eol": "\n",
        "files.trimTrailingWhitespace": True,
        "files.insertFinalNewline": True,
        "files.associations": {"*.md": "markdown"},
        "editor.tabSize": 4,
        "editor.insertSpaces": True,
        "editor.rulers": [100],
        "C_Cpp.default.cppStandard": "c++17",
        "C_Cpp.default.cStandard": "c17",
        "C_Cpp.formatting": "vcFormat",
    })


def extensions_json() -> str:
    return _json({"recommendations": ["ms-vscode.cpptools",
                                      "ms-vscode.cpptools-extension-pack"]})


def code_workspace_json() -> str:
    return _json({
        "folders": [{"name": "C++ 面向对象训练营", "path": "."}],
        "settings": {
            "files.encoding": "utf8",
            "C_Cpp.default.cppStandard": "c++17",
            "editor.tabSize": 4,
        },
    })


def workspace_gitignore() -> str:
    return (
        "# 编译产物(你的 main.cpp / 讲义 / 用例都会被正常跟踪)\n"
        "**/build/\n"
        "*.obj\n"
        "*.exe\n"
        "*.pdb\n"
        "*.ilk\n"
        "*.idb\n"
        ".vs/\n"
        "**/submission.md\n"
    )


# ---------------------------------------------------------------------------
# VS 工程文件
# ---------------------------------------------------------------------------
_VCXPROJ = """<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Debug|x64">
      <Configuration>Debug</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|x64">
      <Configuration>Release</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
  </ItemGroup>
  <PropertyGroup Label="Globals">
    <ProjectGuid>{guid}</ProjectGuid>
    <Keyword>Win32Proj</Keyword>
    <RootNamespace>{namespace}</RootNamespace>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\\Microsoft.Cpp.Default.props" />
  <PropertyGroup Condition="'$(Configuration)'=='Debug'" Label="Configuration">
    <ConfigurationType>Application</ConfigurationType>
    <UseDebugLibraries>true</UseDebugLibraries>
    <PlatformToolset>{toolset}</PlatformToolset>
    <CharacterSet>MultiByte</CharacterSet>
    {use_mfc}</PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)'=='Release'" Label="Configuration">
    <ConfigurationType>Application</ConfigurationType>
    <UseDebugLibraries>false</UseDebugLibraries>
    <PlatformToolset>{toolset}</PlatformToolset>
    <WholeProgramOptimization>false</WholeProgramOptimization>
    <CharacterSet>MultiByte</CharacterSet>
    {use_mfc}</PropertyGroup>
  <Import Project="$(VCTargetsPath)\\Microsoft.Cpp.props" />
  <PropertyGroup>
    <OutDir>$(ProjectDir){build}\\</OutDir>
    <IntDir>$(ProjectDir){build}\\obj\\$(Configuration)\\</IntDir>
    <TargetName>main</TargetName>
    <LocalDebuggerWorkingDirectory>$(ProjectDir){build}</LocalDebuggerWorkingDirectory>
    <DebuggerFlavor>WindowsLocalDebugger</DebuggerFlavor>
  </PropertyGroup>
  <ItemDefinitionGroup>
    <ClCompile>
      <LanguageStandard>stdcpp17</LanguageStandard>
      <AdditionalOptions>/utf-8 %(AdditionalOptions)</AdditionalOptions>
      <WarningLevel>Level3</WarningLevel>
      <PreprocessorDefinitions>{extra_defines}</PreprocessorDefinitions>
      <SDLCheck>false</SDLCheck>
      <ConformanceMode>false</ConformanceMode>
    </ClCompile>
    <Link>
      <SubSystem>{subsystem}</SubSystem>
      <GenerateDebugInformation>true</GenerateDebugInformation>
      <AdditionalDependencies>{extra_libs}</AdditionalDependencies>
    </Link>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)'=='Release'">
    <ClCompile>
      <Optimization>MaxSpeed</Optimization>
    </ClCompile>
  </ItemDefinitionGroup>
  <ItemGroup>
    <ClCompile Include="{source}" />
  </ItemGroup>
  <Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />
</Project>
"""

_SLN_HEAD = (
    "Microsoft Visual Studio Solution File, Format Version 12.00\r\n"
    "# Visual Studio Version 17\r\n"
    "VisualStudioVersion = 17.0.31903.59\r\n"
    "MinimumVisualStudioVersion = 10.0.40219.1\r\n"
)
_SLN_TYPE_CPP = "{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}"


def write_vcxproj(target_dir: str, toolset: Optional[str] = None,
                  problem: Optional[Dict[str, Any]] = None) -> str:
    """给某道题写一个 VS 工程文件; 返回工程文件名。

    problem 带 framework="mfc" 时写入 MFC 必需的三件套(与 judge 的编译参数一致):
    UseOfMfc=Dynamic / Windows 子系统 / _AFXDLL 宏 —— 否则 VS 里 F5 编不过。
    字符集统一用 MultiByte: 教材示例直接写 "字符串字面量" 就能编, 不强制 _T()。
    """
    name = os.path.basename(target_dir.rstrip("\\/"))
    path = os.path.join(target_dir, "%s.vcxproj" % name)
    problem = problem or {}
    is_mfc = str(problem.get("framework") or "console").lower() == "mfc"
    subsystem = str(problem.get("subsystem")
                    or ("windows" if is_mfc else "console")).title()
    defines = (["_AFXDLL"] if is_mfc else [])
    defines += [str(item) for item in problem.get("defines") or []]
    libs = [str(item) for item in problem.get("libs") or []]
    if is_mfc:
        libs += ["user32.lib", "gdi32.lib"]
    content = _VCXPROJ.format(
        guid=project_guid(name),
        namespace=re.sub(r"[^A-Za-z0-9_]", "_", name),
        toolset=toolset or detect_platform_toolset(),
        build=BUILD_DIRNAME,
        source=SOURCE_NAME,
        use_mfc="<UseOfMfc>Dynamic</UseOfMfc>\n    " if is_mfc else "",
        subsystem=subsystem,
        extra_defines=";".join(defines + ["%(PreprocessorDefinitions)"]),
        extra_libs=";".join(libs + ["%(AdditionalDependencies)"]),
    )
    write_text_crlf(path, content)
    return os.path.basename(path)


def refresh_solution(root: Optional[str] = None) -> Optional[str]:
    """重新扫描工作区里的题目目录, 生成/更新 oop_lab.sln。"""
    base = root or oc.WORKSPACE_DIR
    if not os.path.isdir(base):
        return None
    entries: List[Tuple[str, str]] = []
    for name in sorted(os.listdir(base)):
        folder = os.path.join(base, name)
        vcxproj = os.path.join(folder, "%s.vcxproj" % name)
        if os.path.isdir(folder) and os.path.isfile(vcxproj):
            entries.append((name, vcxproj))
    if not entries:
        return None

    lines = [_SLN_HEAD]
    for name, vcxproj in entries:
        lines.append('Project("%s") = "%s", "%s", "%s"\r\nEndProject\r\n' % (
            _SLN_TYPE_CPP, name, os.path.relpath(vcxproj, base), project_guid(name)))
    lines.append("Global\r\n")
    lines.append("\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\r\n")
    for config in ("Debug|x64", "Release|x64"):
        lines.append("\t\t%s = %s\r\n" % (config, config))
    lines.append("\tEndGlobalSection\r\n")
    lines.append("\tGlobalSection(ProjectConfigurationPlatforms) = postSolution\r\n")
    for name, _ in entries:
        guid = project_guid(name)
        for config in ("Debug|x64", "Release|x64"):
            lines.append("\t\t%s.%s.ActiveCfg = %s\r\n" % (guid, config, config))
            lines.append("\t\t%s.%s.Build.0 = %s\r\n" % (guid, config, config))
    lines.append("\tEndGlobalSection\r\n")
    lines.append("\tGlobalSection(SolutionProperties) = preSolution\r\n")
    lines.append("\t\tHideSolutionNode = FALSE\r\n")
    lines.append("\tEndGlobalSection\r\n")
    lines.append("EndGlobal\r\n")

    target = os.path.join(base, SOLUTION_NAME)
    write_text_crlf(target, "".join(lines))
    # 第一个工程在 VS 里会排在最前, 打开解决方案后设它为启动项目即可 F5
    return target


# ---------------------------------------------------------------------------
# 工作区骨架
# ---------------------------------------------------------------------------
def ensure_lab(root: Optional[str] = None,
               toolchain: Optional[oop_judge.Toolchain] = None) -> Dict[str, Any]:
    """建立(或补齐)统一工作区骨架。重复调用不会覆盖学生改过的代码。"""
    base = root or oc.WORKSPACE_DIR
    oc.ensure_dir(base)
    vscode_dir = os.path.join(base, ".vscode")
    oc.ensure_dir(vscode_dir)

    chain = toolchain if toolchain is not None else oop_judge.find_toolchain()
    created: List[str] = []

    def put(path: str, text: str, bat: bool = False) -> None:
        ok = write_bat(path, text) if bat else oc.write_text(path, text)
        if ok:
            created.append(os.path.basename(path))

    if chain and chain.is_msvc and chain.vcvars:
        put(os.path.join(base, "build.bat"), build_bat_msvc(chain.vcvars), bat=True)
    else:
        compiler = chain.compiler if chain else "g++"
        put(os.path.join(base, "build.bat"), build_bat_gcc(compiler), bat=True)
    put(os.path.join(base, "run_case.bat"), run_case_bat(), bat=True)
    put(os.path.join(vscode_dir, "tasks.json"), tasks_json(chain))
    put(os.path.join(vscode_dir, "launch.json"), launch_json(chain))
    put(os.path.join(vscode_dir, "c_cpp_properties.json"), c_cpp_properties_json(chain))
    put(os.path.join(vscode_dir, "settings.json"), settings_json())
    put(os.path.join(vscode_dir, "extensions.json"), extensions_json())
    put(os.path.join(base, CODE_WORKSPACE_NAME), code_workspace_json())
    put(os.path.join(base, ".gitignore"), workspace_gitignore())

    return {
        "dir": base,
        "vscode": vscode_dir,
        "toolchain": chain.label if chain else "无",
        "toolset": detect_platform_toolset(),
        "files": created,
    }


def student_source_path(problem: Dict[str, Any], root: Optional[str] = None) -> str:
    return os.path.join(oc.resolve_problem_dir(problem, root), SOURCE_NAME)


def create_problem(problem: Dict[str, Any], root: Optional[str] = None,
                   force: bool = False,
                   toolchain: Optional[oop_judge.Toolchain] = None) -> Dict[str, Any]:
    """在工作区里创建(或补齐)一道题: 讲义 + 题面 + 骨架 + 用例 + VS 工程。

    force=False 时不会覆盖已有的 main.cpp —— 学生写过的东西必须保住。
    """
    base = root or oc.WORKSPACE_DIR
    ensure_lab(base, toolchain)
    target = oc.resolve_problem_dir(problem, base)
    tests_dir = os.path.join(target, TESTS_DIRNAME)
    oc.ensure_dir(tests_dir)
    oc.ensure_dir(os.path.join(target, BUILD_DIRNAME))

    created: List[str] = []

    def put(path: str, text: str, overwrite: bool = True) -> None:
        if not overwrite and os.path.exists(path):
            return
        if oc.write_text(path, text):
            created.append(os.path.relpath(path, base))

    put(os.path.join(target, KNOWLEDGE_NAME), knowledge_markdown(problem))
    put(os.path.join(target, PROBLEM_MD_NAME), problem_markdown(problem))
    put(os.path.join(target, SOURCE_NAME), problem.get("skeleton") or "// TODO\n",
        overwrite=force)
    for index, test in enumerate(problem.get("tests") or [], start=1):
        put(os.path.join(tests_dir, "%02d.in" % index), test.get("in") or "",
            overwrite=force)
        put(os.path.join(tests_dir, "%02d.out" % index), test.get("out") or "",
            overwrite=force)

    write_vcxproj(target, problem=problem)
    solution = refresh_solution(base)

    chain = toolchain if toolchain is not None else oop_judge.find_toolchain()
    return {
        "dir": target,
        "main": os.path.join(target, SOURCE_NAME),
        "problem_md": os.path.join(target, PROBLEM_MD_NAME),
        "knowledge_md": os.path.join(target, KNOWLEDGE_NAME),
        "tests_dir": tests_dir,
        "workspace": base,
        "solution": solution,
        "toolchain": chain.label if chain else "无",
        "skills": problem_skills(problem),
        "files": created,
    }


# 兼容旧名字(其它模块还在用)
def ensure_workspace(problem: Dict[str, Any], root: Optional[str] = None,
                     force: bool = False,
                     toolchain: Optional[oop_judge.Toolchain] = None) -> Dict[str, Any]:
    return create_problem(problem, root=root, force=force, toolchain=toolchain)


def open_in_vscode(path: str) -> bool:
    cli = find_code_cli()
    if not cli:
        return False
    try:
        subprocess.Popen([cli, path], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, shell=False)
        return True
    except OSError:
        return False


def open_in_visual_studio(path: str) -> bool:
    devenv = find_devenv()
    if not devenv:
        return False
    try:
        subprocess.Popen([devenv, path], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, shell=False)
        return True
    except OSError:
        return False


def read_student_code(problem: Dict[str, Any], root: Optional[str] = None) -> Tuple[bool, str]:
    path = student_source_path(problem, root)
    if not os.path.isfile(path):
        return False, ""
    return True, oc.read_text(path)


# ---------------------------------------------------------------------------
# 提交包(交给老师 / AI 点评用)
# ---------------------------------------------------------------------------
def submission_markdown(problem: Dict[str, Any], source_path: str,
                        report: Optional[oop_judge.JudgeReport] = None,
                        findings: Optional[Sequence[Any]] = None,
                        extra_note: str = "") -> str:
    """把“题面 + 代码 + 评测结果 + 审查意见”打包成一份 markdown。"""
    code = oc.read_text(source_path)
    ids = problem_skills(problem)
    lines: List[str] = []
    lines.append("# 提交点评申请：%s %s" % (problem["id"].upper(), problem["title"]))
    lines.append("")
    lines.append("- 难度：%s %s" % (oc.LEVEL_STARS.get(int(problem.get("level", 3)), "???"),
                                    oc.LEVEL_NAMES.get(int(problem.get("level", 3)), "")))
    lines.append("- 知识点：%s" % (" / ".join(problem.get("topics", [])) or "—"))
    lines.append("- 知识点编号：%s" % "、".join(
        "%s %s" % (sid, oop_skills.skill_name(sid)) for sid in ids))
    lines.append("- 提交时间：%s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("")

    if report is not None:
        lines.append("## 自动评测结果")
        lines.append("")
        lines.append("- 结论：%s" % report.verdict)
        lines.append("- 通过：%d / %d 组用例" % (report.passed, report.total))
        lines.append("- 编译器：%s" % (report.toolchain_label or "无"))
        if not report.compiled:
            lines.append("")
            lines.append("### 编译错误")
            lines.append("")
            lines.append("```text")
            lines.append((report.compile_log or "").strip()[:4000])
            lines.append("```")
        else:
            for case in report.failures()[:3]:
                lines.append("")
                lines.append("### 用例 %d 的差异（第 %d 行）" % (case.index, case.line))
                lines.append("")
                lines.append("- 期望：`%s`" % case.exp_line)
                lines.append("- 实际：`%s`" % case.act_line)
                if case.detail:
                    lines.append("- 说明：%s" % case.detail)
        lines.append("")

    if findings:
        lines.append("## 静态审查意见（自动生成）")
        lines.append("")
        for item in findings:
            lines.append("- **%s %s**（第 %d 行）：%s" % (
                item.rule, item.title, item.line, item.detail or ""))
            if item.advice:
                lines.append("  - 建议：%s" % item.advice)
        lines.append("")

    if problem.get("checklist"):
        lines.append("## 我自查过的点")
        lines.append("")
        for item in problem["checklist"]:
            lines.append("- [ ] %s" % item)
        lines.append("")

    lines.append("## 原始代码（main.cpp）")
    lines.append("")
    lines.append("```cpp")
    lines.append(code.rstrip("\n"))
    lines.append("```")
    lines.append("")

    if extra_note:
        lines.append("## 我想问的问题")
        lines.append("")
        lines.append(extra_note)
        lines.append("")

    lines.append("## 请点评这几点")
    lines.append("")
    lines.append("1. 类的职责划分是否合理？有没有把不该放一起的东西塞进一个类？")
    lines.append("2. 封装边界（public / private / protected）有没有破口？")
    lines.append("3. 拷贝控制（构造 / 赋值 / 析构）有没有 Rule of Three 的坑？")
    lines.append("4. 该用虚函数 / 多态的地方，是不是被 if-else 硬编码了？")
    lines.append("5. 如果重写一遍，最该改的三处是什么？")
    lines.append("")
    return "\n".join(lines)


def write_submission(problem: Dict[str, Any], root: Optional[str] = None,
                     report: Optional[oop_judge.JudgeReport] = None,
                     findings: Optional[Sequence[Any]] = None,
                     extra_note: str = "") -> Tuple[Optional[str], str]:
    source = student_source_path(problem, root)
    if not os.path.isfile(source):
        return None, "还没有生成练习工程, 先运行: py oop_lab.py new %s" % problem["id"]
    text = submission_markdown(problem, source, report, findings, extra_note)
    target = os.path.join(os.path.dirname(source), SUBMISSION_NAME)
    if not oc.write_text(target, text):
        return None, "写入 %s 失败" % target
    return target, ""


def summary(problem: Dict[str, Any], root: Optional[str] = None) -> Dict[str, Any]:
    """看一道题当前的状态(工程是否存在 / 是否写过代码)。"""
    target = oc.resolve_problem_dir(problem, root)
    source = os.path.join(target, SOURCE_NAME)
    return {
        "dir": target,
        "exists": os.path.isdir(target),
        "source_exists": os.path.isfile(source),
        "knowledge_exists": os.path.isfile(os.path.join(target, KNOWLEDGE_NAME)),
        "has_submission": os.path.isfile(os.path.join(target, SUBMISSION_NAME)),
    }
