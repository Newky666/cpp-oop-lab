#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_coach.py - 学习画像 / 自适应选题 / 出错诊断 / 学习日志

这是“老师”那一半: 不只告诉学生“对或错”, 还要回答三个问题 ——

    1. 你现在到底什么水平?          -> LearnerProfile(技能掌握度 + 综合档位)
    2. 下一步该练什么?              -> Planner(按薄弱知识点 + 难度梯度选题)
    3. 这次错在哪、怎么补?          -> Diagnoser(编译器报错/用例差异/审查意见 -> 知识点 -> 讲解)

所有数据落在本机:

    data/profile.json        学习画像(技能掌握度 / 历史记录 / 计数器)
    data/learning_log.md     人类可读的学习日志(可以当学习笔记直接看)
    data/learning_log.jsonl  结构化日志(供程序统计)

设计取舍:
  * 掌握度用“成绩 × 置信度 − 审查扣分 − 遗忘衰减”算, 单一两次满分不会让掌握度暴涨;
  * 选题永远给出**理由**, 让学生知道为什么练这道 —— 这是“教学”和“派发任务”的区别;
  * 在线题(洛谷/dotcpp)拿不到自动评测, 所以单独标记成“拓展题”, 不与过关题混为一谈。
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import oop_bank
import oop_common as oc
import oop_judge
import oop_review
import oop_search
import oop_skills
import oop_web

PROFILE_FILE = os.path.join(oc.DATA_DIR, "profile.json")
LOG_FILE = os.path.join(oc.DATA_DIR, "learning_log.md")
LOG_JSONL = os.path.join(oc.DATA_DIR, "learning_log.jsonl")

LEVEL_NAMES = oc.LEVEL_NAMES          # 与 oop_common 保持同一份(别再各写一份)
MAX_RECORDS = 400

# 知识点 -> 在 OJ 上容易搜到的题目关键词(洛谷/dotcpp 是按题名匹配的, 学术名词搜不到)
SEARCH_TERMS: Dict[str, List[str]] = {
    "K01": ["学生", "成绩统计", "职工"],
    "K02": ["日期", "时间", "矩阵"],
    "K03": ["矩阵", "内存", "动态"],
    "K04": ["字符串", "高精度", "深拷贝"],
    "K05": ["复数", "分数", "向量"],
    "K06": ["计数", "统计", "编号"],
    "K07": ["分数", "复数", "矩阵", "多项式", "高精度"],
    "K08": ["学生", "职员", "继承"],
    "K09": ["图形", "面积", "多态"],
    "K10": ["图形", "面积", "抽象"],
    "K11": ["矩阵", "友元"],
    "K12": ["字符串", "高精度"],
    "K13": ["模板", "排序", "容器"],
    "K14": ["内存", "动态", "指针"],
    "K15": ["模拟", "系统", "设计"],
    "K16": ["继承", "多继承"],
}


# ---------------------------------------------------------------------------
# 学习画像
# ---------------------------------------------------------------------------
def _blank_skill() -> Dict[str, Any]:
    return {"attempts": 0, "full": 0, "partial": 0, "fail": 0,
            "penalty": 0.0, "first_ts": 0.0, "last_ts": 0.0}


class LearnerProfile:
    """记录并计算“本机这位学生”的技能掌握度与综合档位。"""

    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or PROFILE_FILE
        payload = oc.load_json(self.path, default=None)
        if not isinstance(payload, dict):
            payload = {}
        payload.setdefault("version", 1)
        payload.setdefault("created", time.time())
        payload.setdefault("skills", {})
        payload.setdefault("records", [])
        payload.setdefault("counters", {})
        if not isinstance(payload["skills"], dict):
            payload["skills"] = {}
        if not isinstance(payload["records"], list):
            payload["records"] = []
        if not isinstance(payload["counters"], dict):
            payload["counters"] = {}
        self.data: Dict[str, Any] = payload

    # -- 基础读写 -----------------------------------------------------------
    def save(self) -> bool:
        self.data["updated"] = time.time()
        return oc.save_json(self.path, self.data)

    def _entry(self, skill_id: str) -> Dict[str, Any]:
        entry = self.data["skills"].get(skill_id)
        if not isinstance(entry, dict):
            entry = _blank_skill()
            self.data["skills"][skill_id] = entry
        for key, value in _blank_skill().items():
            entry.setdefault(key, value)
        return entry

    @property
    def records(self) -> List[Dict[str, Any]]:
        return self.data["records"]

    def count(self, kind: str) -> int:
        return int(self.data["counters"].get(kind, 0))

    def bump(self, kind: str, amount: int = 1) -> None:
        self.data["counters"][kind] = self.count(kind) + amount

    # -- 掌握度 -------------------------------------------------------------
    def mastery(self, skill_id: str) -> float:
        entry = self.data["skills"].get(skill_id)
        if not isinstance(entry, dict) or int(entry.get("attempts", 0)) <= 0:
            return 0.0
        attempts = int(entry.get("attempts", 0))
        good = float(entry.get("full", 0)) + 0.55 * float(entry.get("partial", 0))
        raw = good / float(attempts)
        confidence = min(1.0, attempts / 3.0)          # 只做过一两次, 打折
        penalty = min(0.30, float(entry.get("penalty", 0.0)))
        score = max(0.0, raw * (0.55 + 0.45 * confidence) - penalty)
        last = float(entry.get("last_ts", 0.0) or 0.0)
        if last > 0:
            days = max(0.0, (time.time() - last) / 86400.0)
            if days > 7:                                # 遗忘曲线: 超过一周没碰, 轻微衰减
                score *= max(0.6, 1.0 - 0.05 * (days - 7))
        return round(min(1.0, max(0.0, score)), 3)

    def evidence(self, skill_id: str) -> Dict[str, Any]:
        return dict(self.data["skills"].get(skill_id) or _blank_skill())

    def practised(self) -> List[str]:
        return [sid for sid in oop_skills.path_order()
                if self.evidence(sid).get("attempts", 0) > 0]

    def _coverage(self, level: int, threshold: float = 0.7) -> float:
        ids = [s["id"] for s in oop_skills.skills_by_level(level)]
        if not ids:
            return 1.0
        hit = sum(1 for sid in ids if self.mastery(sid) >= threshold)
        return hit / float(len(ids))

    def level(self) -> int:
        """综合档位 1/2/3, 与题库的三档对齐。"""
        if not self.practised():
            return 1
        c1, c2, c3 = self._coverage(1), self._coverage(2), self._coverage(3)
        if c3 >= 0.5:
            return 3
        if c2 >= 0.6 or c3 >= 0.25:
            return 2
        if c1 >= 0.6:
            return 2
        return 1

    def level_label(self) -> str:
        level = self.level()
        return "第 %d 档 · %s" % (level, LEVEL_NAMES.get(level, ""))

    def streak(self) -> Tuple[int, int]:
        """(连续通过次数, 连续失败次数) —— 用来决定“加码”还是“退一步”。"""
        wins = losses = 0
        for record in reversed(self.records):
            passed = bool(record.get("all_passed"))
            if passed and losses == 0:
                wins += 1
            elif not passed and wins == 0:
                losses += 1
            else:
                break
        return wins, losses

    def weakest(self, count: int = 5) -> List[Tuple[str, float]]:
        """最需要补的知识点: 先看掌握度低的, 同分时优先“练得少的”。"""
        order = oop_skills.path_order()
        items: List[Tuple[str, float, int]] = [
            (sid, self.mastery(sid), int(self.evidence(sid).get("attempts", 0)))
            for sid in order
        ]
        weak = [item for item in items if item[1] < 0.6]
        weak.sort(key=lambda item: (item[1], item[2], order.index(item[0])))
        if not weak:                                   # 全都掌握得很好, 就挑最靠后的
            items.sort(key=lambda item: (item[1], -order.index(item[0])))
            weak = items[:count]
        return [(sid, score) for sid, score, _ in weak[:count]]

    def strongest(self, count: int = 3) -> List[Tuple[str, float]]:
        items = [(sid, self.mastery(sid)) for sid in oop_skills.path_order()]
        items.sort(key=lambda item: (-item[1], oop_skills.path_order().index(item[0])))
        return [item for item in items[:count] if item[1] > 0]

    # -- 记录 ---------------------------------------------------------------
    def record_attempt(self, problem: Dict[str, Any], report: oop_judge.JudgeReport,
                       findings: Sequence[oop_review.Finding] = (),
                       review_score: Optional[int] = None,
                       source_text: str = "") -> Dict[str, Any]:
        """一次评测后更新画像。"""
        skill_ids = oop_skills.classify(problem.get("topics", [])) or ["K01"]
        all_passed = report.all_passed
        partial = report.compiled and report.total > 0 and 0 < report.passed < report.total
        # 通过率也参与“部分掌握”的判定: 3/4 比 1/4 明显更接近掌握
        ratio = (report.passed / float(report.total)) if report.total else 0.0
        if not report.compiled:
            ratio = 0.0

        now = time.time()
        for sid in skill_ids:
            entry = self._entry(sid)
            entry["attempts"] = int(entry["attempts"]) + 1
            if all_passed:
                entry["full"] = int(entry["full"]) + 1
            elif partial or ratio >= 0.5:
                entry["partial"] = int(entry["partial"]) + 1
            else:
                entry["fail"] = int(entry["fail"]) + 1
            if not entry["first_ts"]:
                entry["first_ts"] = now
            entry["last_ts"] = now

        # 静态审查里指向同一知识点的意见, 折算成掌握度惩罚
        for finding in findings or []:
            sid = oop_skills.map_review_rule(finding.rule)
            if sid and sid in skill_ids:
                entry = self._entry(sid)
                entry["penalty"] = min(0.30, float(entry["penalty"]) + 0.08)

        record = {
            "ts": round(now, 3),
            "pid": problem["id"],
            "title": problem.get("title", ""),
            "level": int(problem.get("level", 1)),
            "skills": skill_ids,
            "verdict": report.verdict,
            "passed": report.passed,
            "total": report.total,
            "all_passed": all_passed,
            "compiled": report.compiled,
            "seconds": round(float(report.seconds or 0.0), 3),
            "review_score": review_score,
            "findings": [f.rule for f in (findings or [])],
            "source": problem.get("source", "builtin"),
        }
        self.records.append(record)
        if len(self.records) > MAX_RECORDS:
            self.data["records"] = self.records[-MAX_RECORDS:]
        self.bump("judge")
        self.data.setdefault("days", [])
        today = time.strftime("%Y-%m-%d")
        if today not in self.data["days"]:
            self.data["days"].append(today)
        self.save()
        return record

    def note_review(self, problem: Dict[str, Any],
                    findings: Sequence[oop_review.Finding],
                    score: Optional[int] = None) -> List[str]:
        """只做写法审查时也更新画像: 问题折算成对应知识点的惩罚分。"""
        skill_ids = oop_skills.classify(problem.get("topics", [])) or ["K01"]
        now = time.time()
        for finding in findings or []:
            sid = oop_skills.map_review_rule(finding.rule)
            if sid and sid in skill_ids:
                entry = self._entry(sid)
                entry["penalty"] = min(0.30, float(entry["penalty"]) + 0.08)
                if not entry["first_ts"]:
                    entry["first_ts"] = now
                entry["last_ts"] = now
        self.bump("review")
        self.save()
        return skill_ids

    def last_attempt(self, pid: Optional[str] = None) -> Optional[Dict[str, Any]]:
        for record in reversed(self.records):
            if pid is None or record.get("pid") == pid:
                return record
        return None

    def practised_ids(self) -> List[str]:
        return list(dict.fromkeys(record.get("pid", "") for record in self.records))

    # -- 渲染 ---------------------------------------------------------------
    def bar(self, value: float, width: int = 12) -> str:
        filled = int(round(max(0.0, min(1.0, value)) * width))
        return "%s%s" % ("█" * filled, "·" * (width - filled))

    def render(self, width: int = 78) -> List[str]:
        lines: List[str] = []
        level = self.level()
        wins, losses = self.streak()
        lines.append(oc.color("学习画像", "bold"))
        lines.append(oc.hr("-", width))
        lines.append("综合档位: %s   %s" % (
            oc.color(self.level_label(), "yellow"),
            oc.color("(连续通过 %d 次 / 连续未过 %d 次)" % (wins, losses), "grey")))
        lines.append("练习次数: 评测 %d 次 · 审查 %d 次 · 生成提交包 %d 次 · 学习 %d 天" % (
            self.count("judge"), self.count("review"), self.count("submit"),
            len(self.data.get("days", []))))
        total_seconds = sum(float(r.get("seconds", 0) or 0) for r in self.records)
        lines.append("累计评测耗时: %s" % oc.human_duration(total_seconds))
        lines.append("")

        practised = set(self.practised())
        for skill_level in sorted(oc.LEVEL_NAMES):
            lines.append(oc.color("第 %d 档 · %s" % (
                skill_level, LEVEL_NAMES.get(skill_level, "")), "cyan"))
            for item in oop_skills.skills_by_level(skill_level):
                sid = item["id"]
                value = self.mastery(sid)
                ev = self.evidence(sid)
                if sid not in practised:
                    tag = oc.color("未练过", "grey")
                elif value >= 0.8:
                    tag = oc.color("熟练", "green")
                elif value >= 0.55:
                    tag = oc.color("基本掌握", "green")
                elif value >= 0.3:
                    tag = oc.color("半懂", "yellow")
                else:
                    tag = oc.color("薄弱", "red")
                detail = ""
                if ev.get("attempts"):
                    detail = "  %d 次(过 %d)" % (ev["attempts"], ev.get("full", 0))
                lines.append("  %s %s %s %s%s" % (
                    sid, oc.pad_end(item["name"], 20), self.bar(value),
                    tag, oc.color(detail, "grey")))
            lines.append("")

        weakest = self.weakest(3)
        if weakest and self.practised():
            lines.append(oc.color("当前最该补的三个点", "yellow"))
            for sid, value in weakest:
                lines.append("  · %s %s(掌握度 %.0f%%)" % (
                    sid, oop_skills.skill_name(sid), value * 100))
            lines.append("")
        return lines


# ---------------------------------------------------------------------------
# 自适应选题
# ---------------------------------------------------------------------------
class Assignment:
    def __init__(self, problem: Dict[str, Any], score: float, reasons: List[str],
                 skills: List[str], kind: str = "过关题") -> None:
        self.problem = problem
        self.score = score
        self.reasons = reasons
        self.skills = skills
        self.kind = kind


def _problem_difficulty(problem: Dict[str, Any]) -> int:
    return max(1, min(3, int(problem.get("level", 1))))


def _target_level(profile: LearnerProfile) -> int:
    """根据最近表现决定“目标难度”: 连赢就加码, 连败就退一步。"""
    wins, losses = profile.streak()
    level = profile.level()
    if wins >= 2 and level < 3:
        return level + 1
    if losses >= 2 and level > 1:
        return level - 1
    return level


def _candidate_pool(include_user: bool = True) -> List[Dict[str, Any]]:
    return oop_bank.all_problems(include_user=include_user)


def _score_candidate(problem: Dict[str, Any], profile: LearnerProfile,
                     target_level: int, recent_ids: Sequence[str]) -> Optional[Assignment]:
    difficulty = _problem_difficulty(problem)
    if difficulty > target_level + 1:
        return None                                    # 跨两档太难, 先别碰
    skills = oop_skills.classify(problem.get("topics", []))
    if not skills:
        skills = ["K01"]
    reasons: List[str] = []

    # 1. 知识点收益: 越薄弱收益越高
    gains = [1.0 - profile.mastery(sid) for sid in skills]
    skill_gain = sum(gains) / len(gains)
    if skill_gain <= 0.08:
        return None                                    # 全都熟练了 -> 太简单, 不安排
    weak_names = [oop_skills.skill_name(sid) for sid, g in zip(skills, gains) if g >= 0.5][:2]
    if weak_names:
        reasons.append("覆盖你目前的薄弱点: " + " / ".join(weak_names))

    # 2. 难度贴合度
    fit = 1.0 - abs(difficulty - target_level) / 2.0
    if difficulty > profile.level():
        reasons.append("难度第 %d 档, 比你当前档位高半档 —— 有点挑战但够得着" % difficulty)

    # 3. 新鲜度
    if profile.last_attempt(problem["id"]):
        last = profile.last_attempt(problem["id"])
        if last.get("all_passed"):
            return None                                # 已经做通过的题不再安排
        novelty = 0.35
        reasons.append("上次没做完(通过 %d/%d), 先把这道收尾" % (
            last.get("passed", 0), last.get("total", 0)))
    else:
        novelty = 1.0

    # 4. 冷却: 最近刚动过的不重复推
    if problem["id"] in recent_ids:
        novelty *= 0.5

    # 5. 来源可信度: 内建题有自动用例, 最可信
    source_bonus = {"builtin": 1.0, "user": 0.85}.get(problem.get("source", "builtin"), 0.9)

    score = 0.45 * skill_gain + 0.25 * fit + 0.20 * novelty + 0.10 * source_bonus
    return Assignment(problem, round(score, 4), reasons, skills)


def local_plan(profile: LearnerProfile, count: int = 3) -> List[Assignment]:
    """从本地题库(内建 + 已导入)里挑题。"""
    target_level = _target_level(profile)
    recent = [r.get("pid") for r in profile.records[-6:]]
    scored: List[Assignment] = []
    for problem in _candidate_pool():
        item = _score_candidate(problem, profile, target_level, recent)
        if item is not None:
            scored.append(item)
    # 同一知识点不要连出三题
    scored.sort(key=lambda a: -a.score)
    picked: List[Assignment] = []
    used_skills: Dict[str, int] = {}
    for item in scored:
        primary = item.skills[0]
        if used_skills.get(primary, 0) >= 1 and len(picked) < count - 1:
            continue
        used_skills[primary] = used_skills.get(primary, 0) + 1
        picked.append(item)
        if len(picked) >= count:
            break
    if len(picked) < count:
        for item in scored:
            if item not in picked:
                picked.append(item)
            if len(picked) >= count:
                break
    return picked


def _problem_sources() -> List[Dict[str, Any]]:
    """能产出“题目”的来源(排除只给仓库/网页的 github、bing)。"""
    kinds = ("luogu", "dotcpp", "codeforces", "generic")
    return [entry for entry in oop_web.enabled_sources()
            if str(entry.get("kind")) in kinds]


def online_candidates(profile: LearnerProfile, count: int = 1,
                      timeout: float = oop_search.DEFAULT_TIMEOUT
                      ) -> Tuple[List[Assignment], List[str]]:
    """按已启用的来源找几道“无自动评测”的拓展题。"""
    notes: List[str] = []
    assignments: List[Assignment] = []
    entries = _problem_sources()
    if not entries:
        return [], ["data/sources.json 里没有可用的题目来源"]

    target_level = _target_level(profile)
    weak = [sid for sid, _ in profile.weakest(3)] or ["K07"]
    for sid in weak:
        if len(assignments) >= count:
            break
        terms = SEARCH_TERMS.get(sid) or [oop_skills.skill_name(sid)]
        keyword = terms[0]
        for entry in entries:
            if len(assignments) >= count:
                break
            label = entry.get("label") or entry.get("name")
            try:
                items, error = oop_search.run_provider(
                    str(entry.get("kind")), entry, keyword, 4, target_level, timeout)
            except Exception as exc:                       # 单个来源坏掉不能拖垮排课
                notes.append("%s: %s" % (label, exc))
                continue
            if error:
                notes.append("%s: %s" % (label, error))
                continue
            for raw in items:
                if _already_imported(raw):
                    continue
                assignments.append(Assignment(
                    _online_problem(raw, entry, sid),
                    0.5,
                    ["来自 %s 的拓展题(没有自动评测, 需要你自己对拍验证)" % label,
                     "关键词 “%s” 对应你的薄弱点 %s" % (keyword, oop_skills.skill_name(sid))],
                    [sid], kind="拓展题"))
                if len(assignments) >= count:
                    break
            if assignments:
                break                                      # 这一轮已经拿到题, 别再换来源
    return assignments, notes


def _online_problem(raw: Dict[str, Any], entry: Dict[str, Any],
                    skill_id: str) -> Dict[str, Any]:
    source = str(entry.get("name", "online"))
    pid = raw.get("pid") or ""
    return {
        "id": "%s:%s" % (source[:4], pid),
        "title": raw.get("title") or pid,
        "level": _online_level(raw, skill_id),
        "topics": ["在线导入", oop_skills.skill_name(skill_id)],
        "url": raw.get("url", ""),
        "source": "online",
        "origin": source,
        "difficulty": raw.get("difficulty", ""),
        "tags": raw.get("tags", []),
    }


def _already_imported(raw: Dict[str, Any]) -> bool:
    url = str(raw.get("url", "")).lower()
    pid = str(raw.get("pid", "")).lower()
    if not url and not pid:
        return False
    for problem in oop_bank.load_user():
        stored_url = str(problem.get("url", "")).lower()
        if url and stored_url == url:
            return True
        if pid and pid in stored_url:
            return True
    return False


def _online_level(raw: Dict[str, Any], skill_id: str) -> int:
    skill = oop_skills.skill(skill_id)
    return int(skill["level"]) if skill else 2


def plan(profile: Optional[LearnerProfile] = None, count: int = 3,
         online: bool = True, local_only: bool = False) -> Dict[str, Any]:
    """今天的练习安排: 本地过关题 + 可选的在线拓展题。"""
    profile = profile or LearnerProfile()
    local_count = count if not online or local_only else max(1, count - 1)
    assignments = local_plan(profile, count=local_count)
    notes: List[str] = []
    if online and not local_only:
        extra, notes = online_candidates(profile, count=max(1, count - len(assignments)))
        assignments.extend(extra)
    return {
        "profile_level": profile.level(),
        "target_level": _target_level(profile),
        "assignments": assignments,
        "notes": notes,
    }


def render_problem(problem: Dict[str, Any], status: str = "",
                   width: int = 78) -> List[str]:
    """把题面渲染成行列表 —— 命令行的 show 与图形界面的题面页共用这一份。

    以前这段代码内联在 oop_lab.cmd_show 里直接 print, 图形界面没法复用,
    两边迟早会写出不一样的题面。status 留空时自动读进度库, 调用方不用自己查。
    """
    if not status:
        try:
            status = oc.ProgressStore().status(problem["id"])
        except Exception:
            status = "todo"
    level = int(problem.get("level", 1))
    lines: List[str] = []
    lines.append(oc.color("%s  %s" % (problem["id"].upper(), problem["title"]), "bold"))
    lines.append("难度 %s %s   状态 %s   自动用例 %d 组" % (
        oc.LEVEL_STARS.get(level, ""),
        oc.LEVEL_NAMES.get(level, ""),
        oc.status_badge(status),
        len(problem.get("tests", []))))
    if problem.get("topics"):
        lines.append("知识点 %s" % " / ".join(problem.get("topics", [])))
    lines.append(oc.hr("-", width))

    for row in oc.wrap_text(problem.get("desc", ""), width):
        lines.append(row)
    lines.append("")

    if problem.get("require"):
        lines.append(oc.color("具体要求", "cyan"))
        for index, item in enumerate(problem["require"], start=1):
            lines.extend(oc.wrap_text("%d. %s" % (index, item), width,
                                      subsequent_indent="   "))
        lines.append("")

    if problem.get("io"):
        lines.append(oc.color("输入输出", "cyan"))
        lines.extend(oc.wrap_text(problem["io"], width))
        lines.append("")

    for index, sample in enumerate((problem.get("samples") or [])[:3], start=1):
        lines.append(oc.color("样例 %d" % index, "cyan"))
        lines.append("  输入:")
        for row in (sample.get("in") or "(无输入)").rstrip("\n").splitlines():
            lines.append("    " + row)
        lines.append("  输出:")
        for row in (sample.get("out") or "").rstrip("\n").splitlines():
            lines.append("    " + row)
        lines.append("")

    if problem.get("hints"):
        lines.append(oc.color("提示", "cyan"))
        for item in problem["hints"]:
            lines.extend(oc.wrap_text("· " + item, width, subsequent_indent="  "))
        lines.append("")

    if problem.get("checklist"):
        lines.append(oc.color("完成前自查(OOP 要点)", "cyan"))
        for item in problem["checklist"]:
            lines.extend(oc.wrap_text("[ ] " + item, width, subsequent_indent="    "))
        lines.append("")
    return lines


def render_plan(result: Dict[str, Any], width: int = 78) -> List[str]:
    lines: List[str] = []
    profile_level = result.get("profile_level", 1)
    lines.append(oc.color("今天练这几道", "bold"))
    lines.append(oc.hr("-", width))
    lines.append("当前档位: 第 %d 档 · %s    本次目标难度: 第 %d 档" % (
        profile_level, LEVEL_NAMES.get(profile_level, ""), result.get("target_level", 1)))
    lines.append("")

    assignments: List[Assignment] = result.get("assignments") or []
    if not assignments:
        lines.append(oc.color("本地题库里已经没有适合你的题了。", "yellow"))
        lines.append("试试 `py oop_lab.py search <关键词>` 去洛谷/dotcpp 找题, 再 `pull` 导入。")
        return lines

    for index, item in enumerate(assignments, start=1):
        problem = item.problem
        level = int(problem.get("level", 1))
        head = "%d. %s  %s" % (index, oc.color(str(problem["id"]), "bold"), problem["title"])
        lines.append(head)
        lines.append("   %s %s %s" % (
            oc.color("[%s]" % item.kind, "green" if item.kind == "过关题" else "yellow"),
            oc.LEVEL_STARS.get(level, "???"),
            oc.color(", ".join(oop_skills.skill_name(s) for s in item.skills), "grey")))
        for reason in item.reasons:
            for row in oc.wrap_text("· " + reason, width - 3, indent="   "):
                lines.append(row)
        if item.kind == "过关题":
            lines.append("   " + oc.color("开局: py oop_lab.py new %s" % problem["id"], "grey"))
        else:
            lines.append("   " + oc.color(
                "在浏览器打开练: %s" % (problem.get("url") or "(见搜索结果)"), "grey"))
        lines.append("")

    notes = result.get("notes") or []
    if notes:
        lines.append(oc.color("联网提示:", "yellow"))
        for note in notes:
            lines.append("  · " + note)
    return lines


# ---------------------------------------------------------------------------
# 出错诊断(老师式讲解)
# ---------------------------------------------------------------------------
class Diagnosis:
    def __init__(self) -> None:
        self.verdict = "NA"
        self.headline = ""
        self.skills: List[str] = []
        self.sections: List[Tuple[str, List[str]]] = []
        self.next_steps: List[str] = []

    def add(self, title: str, rows: Sequence[str]) -> None:
        self.sections.append((title, list(rows)))


def _wa_common_causes() -> List[str]:
    return [
        "对照“期望 / 实际”两行, 差异往往只在一个空格、一个换行, 或者字段顺序 —— 先逐字符看一眼。",
        "检查输入读取顺序是否和题目一致(常见: 题目先给 n 再给 n 个数, 你却先读了数据)。",
        "检查边界: n = 1、空输入、全为负数、相等的情况你的程序会怎样?",
        "浮点输出要求保留几位小数? 有没有用 std::fixed << std::setprecision(k)?",
        "循环变量、数组下标有没有差一位(off-by-one)?",
    ]


def _re_common_causes() -> List[str]:
    return [
        "数组越界 / 访问空指针 —— 最容易出现在下标循环和指针成员上。",
        "对象被重复释放(double free) —— 通常是深拷贝没写, 两个对象共享一块内存。",
        "除零、模零。",
        "递归太深导致栈溢出。",
    ]


def diagnose(problem: Dict[str, Any], source_text: str = "",
             report: Optional[oop_judge.JudgeReport] = None,
             findings: Optional[Sequence[oop_review.Finding]] = None,
             profile: Optional[LearnerProfile] = None,
             width: int = 78) -> Diagnosis:
    """把一次评测 + 一次静态审查翻译成“老师会怎么说”。"""
    result = Diagnosis()
    findings = list(findings or [])
    problem_skills = oop_skills.classify(problem.get("topics", [])) or ["K01"]
    result.skills = list(problem_skills)

    if report is None:
        result.verdict = "NA"
        result.headline = "还没有评测过这道题。"
        result.next_steps = ["先跑 `py oop_lab.py judge %s`。" % problem["id"]]
        return result

    result.verdict = report.verdict

    # ---- 编译失败 ---------------------------------------------------------
    if not report.compiled:
        result.headline = "编译没过, 先别管逻辑 —— 编译器已经告诉你哪里不对了。"
        mapped = oop_skills.map_compiler_error(report.compile_log)
        rows: List[str] = []
        rows.append("编译器输出的第一条错误通常最关键, 先解决它再看后面的。")
        rows.append("")
        rows.append(oc.color("报错原文(前 8 行):", "grey"))
        for row in (report.compile_log or "").strip().splitlines()[:8]:
            rows.append("  " + row)
        if mapped:
            rows.append("")
            rows.append(oc.color("老师解读:", "yellow"))
            for item in mapped:
                rows.append("  · 指向知识点: %s %s" % (
                    item["skill"], oop_skills.skill_name(item["skill"])))
                for line in oc.wrap_text(item["why"], width - 6, indent="      "):
                    rows.append(line)
                for line in oc.wrap_text("怎么改: " + item["how"], width - 6, indent="      "):
                    rows.append(line)
            result.skills = list(dict.fromkeys(
                [item["skill"] for item in mapped] + result.skills))[:4]
        result.add("编译错误诊断", rows)
        result.next_steps = [
            "先只修第一条错误, 然后重新编译 —— 很多后续错误会一起消失。",
            "改完再跑 `py oop_lab.py judge %s`。" % problem["id"],
        ]
        return result

    # ---- 运行期错误 -------------------------------------------------------
    if report.verdict in ("RE", "TLE"):
        result.headline = ("程序崩了 —— 这类问题几乎都和内存或边界有关。"
                           if report.verdict == "RE" else
                           "超时了 —— 先想想最坏情况下的操作次数。")
        rows = []
        for case in report.failures()[:2]:
            rows.append("用例 %d: %s" % (case.index, case.detail or report.verdict))
        rows.append("")
        rows.append(oc.color("按可能性从高到低排查:", "yellow"))
        causes = _re_common_causes() if report.verdict == "RE" else [
            "算法复杂度过高(双重循环套到了 10^5 以上);",
            "循环里用了 std::endl 疯狂刷缓冲区;",
            "死循环: 循环变量没有被推进, 或者条件写反了。",
        ]
        rows.extend("  · " + c for c in causes)
        result.add("运行错误诊断", rows)
        focused = [sid for sid in problem_skills if sid in ("K03", "K04", "K12", "K14")]
        result.skills = focused or problem_skills
        result.next_steps = ["加上 -fsanitize=address(MinGW) 或调试器 F5 单步, 定位崩在哪一行。"]
        return result

    # ---- 答案错误 ---------------------------------------------------------
    if report.verdict == "WA":
        passed, total = report.passed, report.total
        if passed == 0:
            result.headline = ("%d 组用例一组都没过。先用第 1 组样例手动跑一遍, "
                               "确认输入读对了、输出格式对了, 再谈算法。" % total)
        elif passed == total:
            result.headline = "全部通过。"
        else:
            result.headline = ("通过了 %d/%d 组用例 —— 主逻辑方向是对的, 差在细节。"
                               % (passed, total))
        rows = []
        for case in report.failures()[:3]:
            rows.append("用例 %d 第 %d 行:" % (case.index, case.line))
            rows.append("    期望: %s" % repr(case.exp_line))
            rows.append("    实际: %s" % repr(case.act_line))
        if passed == 0:
            rows.append("")
            rows.append(oc.color("一组都没过, 优先怀疑:", "yellow"))
            rows.extend("  · " + c for c in _wa_common_causes()[:3])
        else:
            rows.append("")
            rows.append(oc.color("大部分过了、少数不过, 重点查:", "yellow"))
            rows.extend("  · " + c for c in _wa_common_causes()[2:])
        result.add("用例差异诊断", rows)
        result.next_steps = [
            "把失败用例的输入存成文件, 用 F5 单步跟一遍, 看哪个变量先跑偏。",
            "改完跑 `py oop_lab.py judge %s`; 想连续试可以 `py oop_lab.py run %s --case N`。"
            % (problem["id"], problem["id"]),
        ]

    # ---- 全过 -------------------------------------------------------------
    if report.all_passed:
        result.headline = "全部用例通过 —— 这一题的知识点你基本拿下了。"
        rows = ["下一步不是重复刷题, 而是把写法也磨干净。"]
        if findings:
            rows.append("静态审查还发现 %d 条可以改的地方(见下), 顺手改掉。" % len(findings))
        else:
            rows.append("静态审查没有发现明显问题, 可以直接生成提交包给老师看。")
        rows.append("")
        rows.append(oc.color("想再进一步, 可以问自己:", "yellow"))
        for item in problem.get("checklist", [])[:3]:
            rows.append("  · " + item)
        result.add("过关小结", rows)
        result.next_steps = [
            "py oop_lab.py submit %s   （生成提交包, 让老师/AI 从设计角度点评）" % problem["id"],
            "py oop_lab.py plan        （安排下一组题）",
        ]

    # ---- 静态审查 -> 知识点讲解 -------------------------------------------
    if findings:
        grouped: Dict[str, List[oop_review.Finding]] = {}
        for item in findings:
            sid = oop_skills.map_review_rule(item.rule) or (result.skills[0] if result.skills else "K01")
            grouped.setdefault(sid, []).append(item)
        rows = []
        for sid, items in grouped.items():
            rows.append(oc.color("%s %s" % (sid, oop_skills.skill_name(sid)), "yellow"))
            for finding in items:
                rows.append("  [%s] %s（第 %d 行）" % (finding.rule, finding.title, finding.line))
            hints = oop_skills.REVIEW_HINTS.get(items[0].rule)
            if hints:
                for text in hints[1]:
                    for line in oc.wrap_text(text, width - 6, indent="    "):
                        rows.append(line)
            rows.append("")
        result.add("写法问题定位(按知识点归类)", rows)
        result.skills = list(dict.fromkeys(
            [sid for sid in grouped] + result.skills))[:5]

    if profile is not None and result.skills:
        rows = []
        for sid in result.skills[:3]:
            value = profile.mastery(sid)
            rows.append("%s %s —— 掌握度 %.0f%%  %s" % (
                sid, oop_skills.skill_name(sid), value * 100, profile.bar(value)))
        result.add("这些知识点你的当前掌握度", rows)
    return result


def render_diagnosis(diag: Diagnosis, width: int = 78) -> List[str]:
    lines: List[str] = []
    lines.append(oc.color("老师点评 · %s" % diag.verdict, "bold"))
    lines.append(oc.hr("-", width))
    for row in oc.wrap_text(diag.headline, width):
        lines.append(row)
    lines.append("")
    for title, rows in diag.sections:
        lines.append(oc.color("【%s】" % title, "cyan"))
        for row in rows:
            lines.append(row)
        lines.append("")
    if diag.next_steps:
        lines.append(oc.color("【下一步】", "cyan"))
        for step in diag.next_steps:
            lines.append("  → " + step)
    return lines


# ---------------------------------------------------------------------------
# 学习日志
# ---------------------------------------------------------------------------
def record_result(problem: Dict[str, Any], report: oop_judge.JudgeReport,
                  findings: Sequence[oop_review.Finding] = (),
                  profile: Optional["LearnerProfile"] = None,
                  store: Optional[oc.ProgressStore] = None) -> Dict[str, Any]:
    """评测之后的统一收尾: 更新学习画像 + 进度库。

    命令行的 judge 与图形界面的评测按钮**必须**共用这一份 —— 否则哪天只改了一边,
    画像就会悄悄不更新, 自适应排课跟着失准(这个坑在写图形界面时真的踩了)。
    返回 {record, entry, profile, review_score}。
    """
    profile = profile or LearnerProfile()
    store = store or oc.ProgressStore()
    review_score = oop_review.score(findings)
    record = profile.record_attempt(problem, report, findings,
                                    review_score=review_score)
    entry = store.record(
        problem["id"],
        status="passed" if report.all_passed else "doing",
        passed=report.passed if report.compiled and report.cases else None,
        total=report.total,
        seconds=report.seconds,
        kind="judge",
        detail="%s %d/%d" % (report.verdict, report.passed, report.total))
    return {"record": record, "entry": entry, "profile": profile,
            "review_score": review_score}


def log_event(kind: str, title: str, lines: Sequence[str],
              pid: str = "", detail: str = "") -> bool:
    """把一次学习事件写进 markdown 日志与 jsonl 日志。"""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    ok = True
    try:
        oc.ensure_dir(os.path.dirname(LOG_FILE))
        exists = os.path.exists(LOG_FILE)
        with open(LOG_FILE, "a", encoding="utf-8", newline="") as fh:
            if not exists:
                fh.write("# C++ 面向对象练习日志\n\n")
                fh.write("> 由 `oop_lab` 自动生成, 每完成一次评测 / 审查 / 提交都会追加一段。\n\n")
            fh.write("## %s  %s\n\n" % (stamp, title))
            for row in lines:
                fh.write(oc.strip_ansi(row))
                fh.write("\n")
            fh.write("\n")
    except OSError:
        ok = False
    try:
        with open(LOG_JSONL, "a", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps({
                "ts": stamp, "kind": kind, "pid": pid, "title": title,
                "detail": detail, "lines": [_plain(r) for r in lines][:40],
            }, ensure_ascii=False) + "\n")
    except OSError:
        ok = False
    return ok


def _plain(text: str) -> str:
    return oc.strip_ansi(text)


def log_recent(count: int = 8) -> List[Dict[str, Any]]:
    """读取最近的学习日志(从 jsonl 尾部读, 不整文件加载)。"""
    if not os.path.isfile(LOG_JSONL):
        return []
    try:
        with open(LOG_JSONL, "r", encoding="utf-8") as fh:
            rows = fh.readlines()
    except OSError:
        return []
    out: List[Dict[str, Any]] = []
    for line in rows[-count:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def render_log(count: int = 8) -> List[str]:
    rows = log_recent(count)
    lines: List[str] = []
    lines.append(oc.color("最近的学习记录(完整日志: %s)" % LOG_FILE, "bold"))
    lines.append(oc.hr("-", 78))
    if not rows:
        lines.append("还没有记录。先跑一次 `py oop_lab.py judge b01` 吧。")
        return lines
    for item in reversed(rows):
        head = "%s  %s" % (oc.color(item.get("ts", ""), "grey"),
                           item.get("title", ""))
        lines.append(head)
        detail = item.get("detail")
        if detail:
            lines.append("    " + oc.color(detail, "grey"))
        for row in (item.get("lines") or [])[:6]:
            lines.append("    " + oc.truncate(row, 74))
        lines.append("")
    return lines
