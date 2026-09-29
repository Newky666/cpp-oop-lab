#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oop_lab 回归测试(纯标准库 unittest, 不需要第三方依赖, 也不需要编译器)

运行:
    py -m unittest discover -s tests -t . -v
    py tests\\test_oop_lab.py

编译器相关的用例会自动跳过(找不到编译器时), 所以这套测试在任何机器上都能跑绿。
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import oop_bank  # noqa: E402
import oop_coach  # noqa: E402
import oop_common as oc  # noqa: E402
import oop_judge  # noqa: E402
import oop_review  # noqa: E402
import oop_search  # noqa: E402
import oop_skills  # noqa: E402
import oop_workspace  # noqa: E402


class TestCommonHelpers(unittest.TestCase):
    def setUp(self):
        oc.set_color_enabled(False)

    def test_normalize_output_strips_trailing_whitespace_and_blank_lines(self):
        self.assertEqual(oc.normalize_output("a  \r\nb\t\n\n\n"), "a\nb")
        # 行首空白是有意义的内容, 必须保留(只裁剪行尾与首尾空行)
        self.assertEqual(oc.normalize_output("\n\n  1 0 \n"), "  1 0")
        self.assertEqual(oc.normalize_output(None), "")

    def test_first_difference_reports_line_number(self):
        line, exp, act = oc.first_difference("a\nb\nc\n", "a\nx\nc\n")
        self.assertEqual(line, 2)
        self.assertEqual(exp, "b")
        self.assertEqual(act, "x")
        self.assertEqual(oc.first_difference("a\n", "a\n"), (0, "", ""))

    def test_display_width_counts_cjk_as_two(self):
        self.assertEqual(oc.display_width("abc"), 3)
        self.assertEqual(oc.display_width("中文"), 4)
        self.assertEqual(oc.display_width("a中"), 3)

    def test_pad_end_aligns_by_display_width(self):
        self.assertEqual(oc.pad_end("中文", 6), "中文  ")
        self.assertEqual(oc.pad_end("abcdef", 3), "abcdef")

    def test_truncate_keeps_width_within_limit(self):
        text = oc.truncate("这是一句很长的中文标题需要被截断", 12)
        self.assertLessEqual(oc.display_width(text), 12)
        self.assertTrue(text.endswith("…"))

    def test_wrap_text_never_exceeds_width(self):
        rows = oc.wrap_text("中文 english 混排 " * 8, 30, indent="  ")
        self.assertTrue(rows)
        for row in rows:
            self.assertLessEqual(oc.display_width(row), 30)

    def test_color_disabled_returns_plain_text(self):
        self.assertEqual(oc.color("abc", "red"), "abc")

    def test_format_bar_clamps_percent(self):
        self.assertIn("50.0%", oc.format_bar(50, width=10))
        self.assertEqual(oc.format_bar(-5, width=4), "[....]   0.0%")
        self.assertEqual(oc.format_bar(999, width=4), "[####] 100.0%")

    def test_human_duration(self):
        self.assertIn("ms", oc.human_duration(0.2))
        self.assertIn("秒", oc.human_duration(2.0))
        self.assertIn("分", oc.human_duration(90.0))


class TestProgressStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="oop_store_")
        self.path = os.path.join(self.tmp, "progress.json")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_record_and_reload(self):
        store = oc.ProgressStore(self.path)
        store.record("b01", opened=True, kind="new")
        self.assertEqual(store.status("b01"), "doing")

        store.record("b01", status="passed", passed=3, total=3, seconds=1.5)
        entry = store.get("b01")
        self.assertEqual(entry["status"], "passed")
        self.assertEqual(entry["attempts"], 1)
        self.assertEqual(entry["best"], "3/3")

        reloaded = oc.ProgressStore(self.path)
        self.assertEqual(reloaded.status("b01"), "passed")
        self.assertEqual(reloaded.get("b01")["last_result"], "3/3")

    def test_best_score_is_kept(self):
        store = oc.ProgressStore(self.path)
        store.record("b02", passed=3, total=3)
        store.record("b02", passed=1, total=3)
        self.assertEqual(store.get("b02")["best"], "3/3")

    def test_broken_json_falls_back_to_empty(self):
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write("{ this is not json")
        store = oc.ProgressStore(self.path)
        self.assertEqual(store.stats()["passed"], 0)

    def test_stats_counts_passed(self):
        store = oc.ProgressStore(self.path)
        store.record("b01", status="passed", passed=1, total=1)
        store.record("b02", opened=True)
        stats = store.stats()
        self.assertEqual(stats["passed"], 1)
        self.assertEqual(stats["doing"], 1)


class TestBank(unittest.TestCase):
    def test_validate_all_is_clean(self):
        self.assertEqual(oop_bank.validate_all(), [])

    def test_every_level_has_problems(self):
        counts = oop_bank.level_counts()
        for level in (1, 2, 3):
            self.assertGreaterEqual(counts.get(level, 0), 6, "第 %d 档题目太少" % level)

    def test_ids_are_unique_and_ordered(self):
        ids = [p["id"] for p in oop_bank.BUILTIN]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 22)

    def test_every_builtin_problem_has_tests_and_solution(self):
        for problem in oop_bank.BUILTIN:
            self.assertTrue(problem["tests"], "%s 没有自动用例" % problem["id"])
            self.assertTrue(problem["solution"].strip(), "%s 没有参考解" % problem["id"])
            self.assertIn("int main", problem["solution"])
            self.assertIn("TODO", problem["skeleton"])

    def test_find_accepts_loose_ids(self):
        for key in ("b01", "B01", "b1", "student-class"):
            found = oop_bank.find(key)
            self.assertIsNotNone(found, "找不到 %s" % key)
            self.assertEqual(found["id"], "b01")

    def test_find_returns_none_for_unknown(self):
        self.assertIsNone(oop_bank.find("zzz999"))

    def test_filter_by_level_and_tag(self):
        level2 = oop_bank.filter_problems(level=2, include_user=False)
        self.assertTrue(all(p["level"] == 2 for p in level2))
        virtual = oop_bank.filter_problems(tag="虚函数", include_user=False)
        self.assertTrue(virtual)
        self.assertIn("i04", [p["id"] for p in virtual])

    def test_skeleton_and_solution_compile_ready(self):
        """骨架必须能编译(只有 TODO 注释, 不含语法错误)。"""
        for problem in oop_bank.BUILTIN:
            self.assertIn("#include", problem["skeleton"], problem["id"])

    def test_validate_detects_missing_fields(self):
        errors = oop_bank.validate({"id": "x01", "level": 1})
        self.assertTrue(errors)


class TestReview(unittest.TestCase):
    def setUp(self):
        oc.set_color_enabled(False)

    def rules(self, code):
        return {f.rule for f in oop_review.review_source(code)}

    def test_rule_of_three_missing_copy_ctor(self):
        code = """
        #include <iostream>
        class Buf {
            int* data_;
        public:
            Buf() { data_ = new int[4]; }
            ~Buf() { delete[] data_; }
        };
        int main() { Buf b; return 0; }
        """
        found = self.rules(code)
        self.assertIn("R01", found)

    def test_virtual_destructor_missing(self):
        code = """
        class Base {
        public:
            virtual void run() {}
            ~Base() {}
        };
        class Derived : public Base { public: ~Derived() {} };
        int main() { return 0; }
        """
        self.assertIn("R02", self.rules(code))

    def test_self_assignment_not_checked(self):
        code = """
        class MyString {
            char* d_;
        public:
            MyString(const MyString& o) { d_ = 0; }
            ~MyString() { delete[] d_; }
            MyString& operator=(const MyString& o) {
                delete[] d_;
                d_ = 0;
                return *this;
            }
        };
        int main() { return 0; }
        """
        self.assertIn("R03", self.rules(code))

    def test_new_delete_mismatch(self):
        code = """
        int main() {
            int* p = new int(3);
            return *p;
        }
        """
        found = {f.rule for f in oop_review.review_source(code)}
        self.assertIn("R04", found)

    def test_using_namespace_std_and_todo_are_reported(self):
        code = "using namespace std;\n// TODO: finish\nint main() { return 0; }\n"
        found = self.rules(code)
        self.assertIn("R08", found)
        self.assertIn("R07", found)

    def test_private_inheritance_is_reported(self):
        code = """
        class Base { public: virtual ~Base() {} };
        class Derived : Base { };
        int main() { return 0; }
        """
        self.assertIn("R06", self.rules(code))

    def test_public_inheritance_is_not_reported(self):
        code = """
        class Base { public: virtual ~Base() {} };
        class Derived : public Base { };
        int main() { return 0; }
        """
        self.assertNotIn("R06", self.rules(code))

    def test_block_comment_and_string_do_not_trigger_code_rules(self):
        code = """
        int main() {
            /* using namespace std; */
            const char* s = "new delete";
            return 0;
        }
        """
        found = self.rules(code)
        self.assertNotIn("R08", found)
        self.assertNotIn("R04", found)

    def test_clean_oop_code_scores_full_marks(self):
        code = """
        #include <string>
        class Student {
        private:
            std::string name_;
        public:
            explicit Student(const std::string& name) : name_(name) {}
            const std::string& name() const { return name_; }
        };
        int main() { Student s("a"); return 0; }
        """
        findings = oop_review.review_source(code)
        self.assertEqual(oop_review.score(findings), 100)
        self.assertEqual(findings, [])

    def test_score_penalises_errors(self):
        self.assertLess(oop_review.score([oop_review.Finding("R00", "error", "x")]), 100)
        self.assertEqual(oop_review.score([]), 100)


class TestJudgeHelpers(unittest.TestCase):
    def setUp(self):
        oc.set_color_enabled(False)
        self.tmp = tempfile.mkdtemp(prefix="oop_judge_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_compile_missing_source_returns_failure_not_exception(self):
        chain = oop_judge.find_toolchain() or oop_judge.Toolchain("g++", "g++")
        result = oop_judge.compile_file(chain, os.path.join(self.tmp, "nope.cpp"),
                                        os.path.join(self.tmp, "build"))
        self.assertFalse(result.ok)
        self.assertIn("找不到源文件", result.log)

    def test_run_missing_binary_returns_error(self):
        result = oop_judge.run_binary(os.path.join(self.tmp, "nope.exe"), "")
        self.assertEqual(result.code, -1)
        self.assertFalse(result.ok)

    def test_bad_toolchain_reports_error(self):
        chain = oop_judge.Toolchain("g++", os.path.join(self.tmp, "no-such-compiler"))
        source = os.path.join(self.tmp, "a.cpp")
        with open(source, "w", encoding="utf-8") as fh:
            fh.write("int main() { return 0; }\n")
        result = oop_judge.compile_file(chain, source, os.path.join(self.tmp, "build"))
        self.assertFalse(result.ok)
        self.assertTrue(result.log)

    def test_report_verdict_logic(self):
        report = oop_judge.JudgeReport()
        report.compiled = False
        self.assertEqual(report.verdict, "CE")

        report.compiled = True
        self.assertEqual(report.verdict, "SKIP")

        report.cases = [oop_judge.CaseResult(1, True), oop_judge.CaseResult(2, False, verdict="WA")]
        self.assertEqual(report.verdict, "WA")
        self.assertEqual(report.passed, 1)
        self.assertEqual(len(report.failures()), 1)

    def test_render_report_without_compiler_does_not_crash(self):
        report = oop_judge.JudgeReport()
        rows = oop_judge.render_report(report)
        self.assertTrue(rows)

    def test_doctor_returns_lines(self):
        ok, rows = oop_judge.doctor()
        self.assertIsInstance(ok, bool)
        self.assertTrue(rows)


class TestWorkspace(unittest.TestCase):
    def setUp(self):
        oc.set_color_enabled(False)
        self.tmp = tempfile.mkdtemp(prefix="oop_ws_")
        self.problem = oop_bank.find("b01")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_problem_folder_contents(self):
        info = oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        self.assertTrue(os.path.isfile(info["main"]))
        self.assertTrue(os.path.isfile(info["problem_md"]))
        self.assertTrue(os.path.isfile(info["knowledge_md"]))
        name = os.path.basename(info["dir"])
        self.assertTrue(os.path.isfile(os.path.join(info["dir"], "%s.vcxproj" % name)))
        for index in range(1, len(self.problem["tests"]) + 1):
            self.assertTrue(os.path.isfile(os.path.join(info["tests_dir"], "%02d.in" % index)))
            self.assertTrue(os.path.isfile(os.path.join(info["tests_dir"], "%02d.out" % index)))

    def test_shared_workspace_skeleton(self):
        """配置全部集中在工作区根: 一套 .vscode + 共用脚本 + 解决方案。"""
        info = oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        base = info["workspace"]
        for name in ("build.bat", "run_case.bat", oop_workspace.CODE_WORKSPACE_NAME,
                     ".gitignore", oop_workspace.SOLUTION_NAME):
            self.assertTrue(os.path.isfile(os.path.join(base, name)),
                            "缺少工作区文件 %s" % name)
        for name in ("tasks.json", "launch.json", "c_cpp_properties.json",
                     "settings.json", "extensions.json"):
            self.assertTrue(os.path.isfile(os.path.join(base, ".vscode", name)),
                            "缺少 .vscode/%s" % name)
        # 每道题里不再各自放一份 .vscode
        self.assertFalse(os.path.isdir(os.path.join(info["dir"], ".vscode")))

    def test_batch_files_are_ascii_with_crlf(self):
        """批处理必须是纯 ASCII + CRLF, 否则 cmd 会按本地代码页解析出错。"""
        info = oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        for name in ("build.bat", "run_case.bat"):
            with open(os.path.join(info["workspace"], name), "rb") as fh:
                raw = fh.read()
            self.assertTrue(all(byte < 128 for byte in raw), "%s 含非 ASCII 字节" % name)
            self.assertIn(b"\r\n", raw, "%s 不是 CRLF 换行" % name)

    def test_vscode_config_targets_current_file(self):
        info = oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        tasks = json.loads(oc.read_text(os.path.join(info["workspace"], ".vscode", "tasks.json")))
        build = tasks["tasks"][0]
        self.assertIn("${file}", build["args"])
        launch = json.loads(oc.read_text(
            os.path.join(info["workspace"], ".vscode", "launch.json")))
        self.assertIn("${fileDirname}", launch["configurations"][0]["program"])

    def test_solution_lists_all_projects(self):
        info = oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        sln_path = os.path.join(info["workspace"], oop_workspace.SOLUTION_NAME)
        text = oc.read_text(sln_path)
        self.assertIn(os.path.basename(info["dir"]), text)
        self.assertIn(oop_workspace.project_guid(os.path.basename(info["dir"])), text)

        other = oop_bank.find("b02")
        oop_workspace.ensure_workspace(other, root=self.tmp)
        text2 = oc.read_text(sln_path)
        self.assertIn(os.path.basename(oc.resolve_problem_dir(other, self.tmp)), text2)

    def test_project_guid_is_deterministic(self):
        first = oop_workspace.project_guid("b01-student-class")
        self.assertEqual(first, oop_workspace.project_guid("b01-student-class"))
        self.assertNotEqual(first, oop_workspace.project_guid("b02-other"))
        self.assertRegex(first, r"^\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}$")

    def test_vcxproj_is_usable(self):
        info = oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        name = os.path.basename(info["dir"])
        text = oc.read_text(os.path.join(info["dir"], "%s.vcxproj" % name))
        self.assertIn("<PlatformToolset>", text)      # 不写会被 MSBuild 当成 VS2010
        self.assertIn("<PlatformToolset>%s</PlatformToolset>"
                      % oop_workspace.detect_platform_toolset(), text)
        self.assertIn("<TargetName>main</TargetName>", text)   # 产物与 judge 一致
        self.assertIn("<LanguageStandard>stdcpp17</LanguageStandard>", text)

    def test_existing_main_is_not_overwritten(self):
        info = oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        with open(info["main"], "w", encoding="utf-8") as fh:
            fh.write("// 学生写的代码\nint main() { return 0; }\n")
        oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        self.assertIn("学生写的代码", oc.read_text(info["main"]))

    def test_force_overwrites(self):
        info = oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        with open(info["main"], "w", encoding="utf-8") as fh:
            fh.write("// 学生写的代码\n")
        oop_workspace.ensure_workspace(self.problem, root=self.tmp, force=True)
        self.assertNotIn("学生写的代码", oc.read_text(info["main"]))

    def test_vscode_json_files_are_valid(self):
        info = oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        for name in ("tasks.json", "launch.json", "c_cpp_properties.json", "settings.json"):
            path = os.path.join(info["workspace"], ".vscode", name)
            with open(path, "r", encoding="utf-8") as fh:
                json.load(fh)

    def test_knowledge_markdown_teaches_every_skill(self):
        """先学后练: 讲义必须覆盖本题涉及的每个知识点, 且有要点/坑/示例。"""
        info = oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        text = oc.read_text(info["knowledge_md"])
        for skill_id in oop_workspace.problem_skills(self.problem):
            self.assertIn("## %s " % skill_id, text)
        for token in ("### 要点", "### 常见坑", "### 正确写法示例", "### 动手前自问"):
            self.assertIn(token, text)

    def test_problem_markdown_points_to_knowledge(self):
        text = oop_workspace.problem_markdown(self.problem)
        for token in ("# B01", "knowledge.md", "## 具体要求", "## 样例", "## 完成前自查"):
            self.assertIn(token, text)

    def test_submission_markdown_contains_code_and_checklist(self):
        info = oop_workspace.ensure_workspace(self.problem, root=self.tmp)
        report = oop_judge.JudgeReport()
        report.compiled = True
        report.cases = [oop_judge.CaseResult(1, True)]
        text = oop_workspace.submission_markdown(self.problem, info["main"], report, [])
        self.assertIn("```cpp", text)
        self.assertIn("## 自动评测结果", text)
        self.assertIn("知识点编号", text)
        self.assertIn("请点评这几点", text)

    def test_write_submission_reports_missing_workspace(self):
        problem = oop_bank.find("b02")
        path, error = oop_workspace.write_submission(problem, root=self.tmp)
        self.assertIsNone(path)
        self.assertIn("先运行", error)


class TestSearchHelpers(unittest.TestCase):
    def setUp(self):
        oc.set_color_enabled(False)

    def test_html_to_text_strips_tags_and_entities(self):
        text = oop_search.html_to_text("<p>Hello&nbsp;<b>world</b></p><br>next")
        self.assertIn("Hello", text)
        self.assertIn("world", text)
        self.assertNotIn("<", text)

    def test_html_to_text_drops_scripts(self):
        self.assertEqual(oop_search.html_to_text("<script>bad()</script>ok"), "ok")

    def test_extract_pid_from_various_inputs(self):
        self.assertEqual(oop_search.extract_pid("P1001"), "P1001")
        self.assertEqual(oop_search.extract_pid("https://www.luogu.com.cn/problem/P3373"), "P3373")
        self.assertEqual(oop_search.extract_pid("CF1A"), "CF1A")
        self.assertEqual(oop_search.extract_pid(""), "")

    def test_suggest_links_always_available(self):
        links = oop_search.suggest_links("运算符重载")
        self.assertTrue(links)
        self.assertTrue(all(len(item) == 2 for item in links))

    def test_search_all_degrades_without_network(self):
        """把 http_get 打桩成失败, 验证搜索不会抛异常且给出兜底链接。"""
        original = oop_search.http_get
        try:
            oop_search.http_get = lambda *a, **k: oop_search.HttpResult(False, error="模拟断网")
            result = oop_search.search_all("继承", limit=2)
        finally:
            oop_search.http_get = original
        self.assertEqual(result["luogu"], [])
        self.assertEqual(result["dotcpp"], [])
        self.assertEqual(result["bing"], [])
        # 断网时 GitHub 会回退到精选清单, 所以这里不该是空的
        self.assertTrue(result["github"])
        self.assertTrue(result["links"])
        self.assertTrue(result["errors"])
        self.assertTrue(oop_search.render_search(result))

    def test_search_all_can_limit_sources(self):
        original = oop_search.http_get
        try:
            oop_search.http_get = lambda *a, **k: oop_search.HttpResult(False, error="模拟断网")
            result = oop_search.search_all("继承", sources=("luogu",))
        finally:
            oop_search.http_get = original
        self.assertNotIn("github", result)          # 只查洛谷时, 其它来源根本不会被访问
        self.assertEqual(result["order"], ["luogu"])
        self.assertEqual(len(result["errors"]), 1)

    def test_guess_level_from_difficulty(self):
        self.assertEqual(oop_search.guess_level([], "入门"), 1)
        self.assertEqual(oop_search.guess_level([], "普及/提高-"), 2)
        self.assertEqual(oop_search.guess_level([], "省选/NOI-"), 3)

    def test_guess_level_falls_back_to_title_keywords(self):
        # dotcpp 的题名自带分类前缀, 没有难度标签时应该能靠它定档
        self.assertEqual(oop_search.guess_level([], "—", "[编程入门]结构体之时间设计"), 1)
        self.assertEqual(oop_search.guess_level([], "—", "线段树区间求和"), 3)
        self.assertEqual(oop_search.guess_level([], "—", "完全没见过的题目"), 2)

    def test_decode_body_prefers_declared_charset(self):
        gbk_bytes = "必应：C++ 练习题".encode("gbk")
        self.assertEqual(oop_search.decode_body(gbk_bytes, "text/xml; charset=gbk"),
                         "必应：C++ 练习题")
        self.assertEqual(oop_search.decode_body("中文".encode("utf-8")), "中文")

    def test_parse_luogu_list(self):
        html = """
        <html><body><ul>
          <li><h3><a href="/problem/P1001">A+B Problem</a></h3>
              <p><small><a href="/problem/list?tag=1">模拟</a> ｜
              <a href="/problem/list?tag=2">字符串</a></small></p></li>
          <li><h3><a href="/problem/P1932">A+B A-B A*B A/B A%B Problem</a></h3>
              <p><small><a href="/problem/list?tag=3">高精度</a></small></p></li>
        </ul></body></html>
        """
        items = oop_search.parse_luogu_list(html, limit=5)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["pid"], "P1001")
        self.assertEqual(items[0]["title"], "A+B Problem")
        self.assertEqual(items[0]["tags"], ["模拟", "字符串"])
        self.assertEqual(items[1]["pid"], "P1932")
        self.assertEqual(oop_search.parse_luogu_list(html, limit=1), items[:1])

    def test_parse_luogu_problem_sections(self):
        html = """
        <html><body>
        <h1>P1001 A+B Problem</h1>
        <section><h2>题目描述</h2><div>输入两个整数 a, b, 输出它们的和。</div></section>
        <section><h2>输入格式</h2><div>一行两个整数。</div></section>
        <section><h2>输出格式</h2><div>一个整数。</div></section>
        <section><h2>说明/提示</h2><div>注意数据范围。</div></section>
        <a href="/problem/list?tag=1">模拟</a>
        </body></html>
        """
        info = oop_search.parse_luogu_problem(html, pid="P1001")
        self.assertEqual(info["title"], "P1001 A+B Problem")
        self.assertIn("两个整数", info["description"])
        self.assertIn("两个整数", info["inputFormat"])
        self.assertEqual(info["outputFormat"], "一个整数。")
        self.assertIn("数据范围", info["hint"])
        self.assertEqual(info["tags"], ["模拟"])

    def test_parse_lentille_json_list(self):
        payload = json.dumps({
            "template": "problem.list",
            "data": {"problems": {"result": [
                {"pid": "P1001", "name": "A+B Problem", "difficulty": 1, "tags": [1]},
                {"pid": "P3373", "name": "线段树 2", "difficulty": 5, "tags": [1, 42]},
            ]}},
        }, ensure_ascii=False)
        html = (
            '<a href="/problem/list?tag=1">模拟</a>'
            '<a href="/problem/list?tag=42">线段树</a>'
            '<script id="lentille-context" type="application/json">%s</script>' % payload
        )
        items = oop_search.parse_luogu_list(html, limit=5)
        self.assertEqual([i["pid"] for i in items], ["P1001", "P3373"])
        self.assertEqual(items[0]["difficulty"], "入门")
        self.assertEqual(items[1]["tags"], ["模拟", "线段树"])

    def test_parse_lentille_json_problem(self):
        payload = json.dumps({
            "template": "problem.show",
            "data": {"problem": {
                "pid": "P1001", "name": "A+B Problem", "difficulty": 1, "tags": [1],
                "samples": [["1 2", "3"]],
                "contenu": {"background": "背景", "description": "求 a+b",
                            "formatI": "两个整数", "formatO": "一个整数", "hint": "注意范围"},
            }},
        }, ensure_ascii=False)
        html = ('<a href="/problem/list?tag=1">模拟</a>'
                '<script id="lentille-context" type="application/json">%s</script>' % payload)
        info = oop_search.parse_luogu_problem(html, pid="P1001")
        self.assertEqual(info["title"], "A+B Problem")
        self.assertEqual(info["difficulty"], "入门")
        self.assertEqual(info["tags"], ["模拟"])
        self.assertEqual(info["description"], "求 a+b")
        self.assertEqual(info["inputFormat"], "两个整数")
        self.assertEqual(info["samples"], [{"in": "1 2", "out": "3"}])
        self.assertTrue(info["url"].endswith("/problem/P1001"))

    def test_parse_lentille_ignores_broken_json(self):
        html = '<script id="lentille-context" type="application/json">{ bad json </script>'
        self.assertIsNone(oop_search.parse_lentille(html))
        self.assertEqual(oop_search.parse_luogu_list(html), [])

    def test_normalize_samples_accepts_both_shapes(self):
        self.assertEqual(oop_search.normalize_samples([["1", "2"]]),
                         [{"in": "1", "out": "2"}])
        self.assertEqual(oop_search.normalize_samples([{"input": "3", "output": "4"}]),
                         [{"in": "3", "out": "4"}])
        self.assertEqual(oop_search.normalize_samples(None), [])

    def test_parse_bing_rss(self):
        xml = """
        <rss><channel>
          <item><title>C++ 类与对象 - 教程</title>
                <link>https://example.com/oop</link>
                <description>面向对象入门</description></item>
          <item><title>继承与多态</title><link>https://example.com/inherit</link></item>
        </channel></rss>
        """
        items = oop_search.parse_bing_rss(xml, limit=5)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["url"], "https://example.com/oop")
        self.assertEqual(items[1]["title"], "继承与多态")

    def test_parse_dotcpp_list(self):
        html = """
        <table><tbody>
        <tr class='evenrow'><td><span class=none> </span></td>
            <td class='problem-number'><span class='center'>1000</span></td>
            <td class='problem-title'><span class='left'>
                <a target='_blank' href='/oj/problem1000.html' title='[编程入门]简单的a+b'>
                <h3 class='h_inherit'>[编程入门]简单的a+b</h3></a></span></td>
            <td><a class='center btn hard_label hard_label_2 btn-success 'href='/oj/problemset.php?difficulty=0''target='_blank'>入门</a></td>
            <td class='problem-stats'><span class='center'>159814/323930</span></td></tr>
        <tr class='oddrow'><td><span class=none> </span></td>
            <td class='problem-number'><span class='center'>1051</span></td>
            <td class='problem-title'><span class='left'>
                <a target='_blank' href='/oj/problem1051.html' title='[编程入门]结构体之成绩统计'>
                <h3 class='h_inherit'>[编程入门]结构体之成绩统计</h3></a></span></td>
            <td><a class='center btn hard_label hard_label_4 'href='/oj/problemset.php?difficulty=2''target='_blank'>中等</a></td>
            <td class='problem-stats'><span class='center'>100/200</span></td></tr>
        </tbody></table>
        """
        items = oop_search.parse_dotcpp_list(html, limit=10)
        self.assertEqual([i["pid"] for i in items], ["1000", "1051"])
        self.assertEqual(items[0]["title"], "[编程入门]简单的a+b")
        self.assertEqual(items[0]["difficulty"], "入门")
        self.assertEqual(items[1]["difficulty"], "中等")
        self.assertEqual(items[0]["source"], "dotcpp")
        filtered = oop_search.parse_dotcpp_list(html, limit=10, keyword="成绩")
        self.assertEqual([i["pid"] for i in filtered], ["1051"])

    def test_parse_dotcpp_problem(self):
        html = """
        <html><head><title>[编程入门]简单的a+b - C语言网</title></head><body>
        <div class="panel_prob"><div class="panel_prob_head"><h2 class="h_inherit">题目描述</h2></div>
            <div class="panel_prob_body">输入两个整数 a, b, 输出它们的和。</div></div>
        <div class="panel_prob"><div class="panel_prob_head"><h2 class="h_inherit">输入格式</h2></div>
            <div class="panel_prob_body">一行两个整数。</div></div>
        <div class="panel_prob"><div class="panel_prob_head"><h2 class="h_inherit">输出格式</h2></div>
            <div class="panel_prob_body">一个整数。</div></div>
        <div class="panel_prob"><div class="panel_prob_head"><h2 class="h_inherit">样例输入</h2>
            <button class="btn">复制</button></div><div class="panel_prob_body">1 2</div></div>
        <div class="panel_prob"><div class="panel_prob_head"><h2 class="h_inherit">样例输出</h2>
            <button class="btn">复制</button></div><div class="panel_prob_body">3</div></div>
        </body></html>
        """
        info = oop_search.parse_dotcpp_problem(html, pid="1000")
        self.assertEqual(info["title"], "[编程入门]简单的a+b")
        self.assertIn("输出它们的和", info["description"])
        self.assertEqual(info["inputFormat"], "一行两个整数。")
        self.assertEqual(info["outputFormat"], "一个整数。")
        self.assertEqual(info["samples"], [{"in": "1 2", "out": "3"}])
        self.assertEqual(info["source"], "dotcpp")

    def test_detect_source(self):
        self.assertEqual(oop_search.detect_source("P1001"), "luogu")
        self.assertEqual(oop_search.detect_source("1049"), "dotcpp")
        self.assertEqual(oop_search.detect_source("CF1A"), "codeforces")
        self.assertEqual(oop_search.detect_source("4A"), "codeforces")
        self.assertEqual(oop_search.detect_source("https://www.dotcpp.com/oj/problem1051.html"),
                         "dotcpp")
        self.assertEqual(oop_search.detect_source("https://www.luogu.com.cn/problem/P3373"),
                         "luogu")
        # 认不出来的域名走通用抽取
        self.assertEqual(oop_search.detect_source("http://noi.openjudge.cn/ch0101/01/"), "web")

    def test_extract_dotcpp_id(self):
        self.assertEqual(oop_search.extract_dotcpp_id("1049"), "1049")
        self.assertEqual(oop_search.extract_dotcpp_id(
            "https://www.dotcpp.com/oj/problem1051.html"), "1051")

    def test_build_imported_problem_shape(self):
        info = {
            "pid": "P1001", "title": "A+B Problem", "difficulty": "入门",
            "tags": ["模拟"], "background": "背景", "description": "求两个数之和",
            "inputFormat": "两个整数", "outputFormat": "一个整数",
            "hint": "", "samples": [{"in": "1 2\n", "out": "3\n"}],
            "url": "https://www.luogu.com.cn/problem/P1001",
        }
        problem = oop_search.build_imported_problem(info)
        self.assertTrue(problem["id"].startswith("u"))
        self.assertEqual(problem["source"], "user")
        self.assertEqual(problem["tests"], [])
        self.assertEqual(problem["level"], 1)
        self.assertIn("TODO", problem["skeleton"])
        self.assertIn("两个整数", problem["io"])
        self.assertIn("求两个数之和", problem["desc"])
        self.assertEqual(oop_bank.validate(problem), [])


class TestSkills(unittest.TestCase):
    """知识点图谱与归类规则。"""

    def setUp(self):
        oc.set_color_enabled(False)

    def test_skill_ids_unique_and_ordered(self):
        ids = oop_skills.all_skill_ids()
        self.assertEqual(len(ids), 17)
        self.assertEqual(len(set(ids)), 17)
        self.assertEqual(oop_skills.path_order()[0], "K01")
        for skill_id in ids:
            item = oop_skills.skill(skill_id)
            self.assertTrue(item["keywords"], skill_id)
            self.assertTrue(item["points"], skill_id)
            self.assertTrue(item["pitfalls"], skill_id)
            self.assertTrue(item["example"], skill_id)

    def test_every_builtin_problem_maps_to_a_skill(self):
        for problem in oop_bank.BUILTIN:
            skills = oop_skills.classify(problem.get("topics", []))
            self.assertTrue(skills, "%s 没有归类到任何知识点" % problem["id"])

    def test_longest_keyword_wins(self):
        # “拷贝构造函数”不能同时命中 K02(构造函数) 与 K04(拷贝构造函数)
        self.assertEqual(oop_skills.classify(["拷贝构造函数"]), ["K04"])
        self.assertEqual(oop_skills.classify(["构造函数"]), ["K02"])
        self.assertEqual(oop_skills.classify(["虚析构函数"]), ["K10"])
        self.assertEqual(oop_skills.classify(["纯虚函数"]), ["K10"])

    def test_composition_skill_and_classification(self):
        self.assertIn("K17", oop_skills.all_skill_ids())
        self.assertEqual(oop_skills.classify(["组合关系"]), ["K17"])
        # “成员对象生命周期”必须命中更具体的 K17, 而不是 K03 的“生命周期”
        self.assertEqual(oop_skills.classify(["成员对象生命周期"]), ["K17"])
        self.assertEqual(oop_skills.classify(["has-a 与 is-a"]), ["K17"])
        # 组合相关题目要能归到 K17
        composition = oop_bank.find("i08")
        self.assertIn("K17", oop_skills.classify(composition.get("topics", [])))
        # K17 属于进阶档
        self.assertEqual(int(oop_skills.skill("K17")["level"]), 2)

    def test_classify_is_sorted_by_learning_path(self):
        skills = oop_skills.classify(["虚函数", "拷贝构造函数"])
        self.assertEqual(skills, ["K04", "K09"])
        self.assertEqual(oop_skills.classify([]), [])
        self.assertEqual(oop_skills.classify(["完全不相关的词"]), [])

    def test_classify_text_from_problem_statement(self):
        text = ("定义两个类 Point 和 Rectangle, 要求使用拷贝构造函数完成深拷贝, "
                "并把析构函数写成 virtual")
        skills = oop_skills.classify_text(text)
        self.assertIn("K04", skills)
        self.assertEqual(oop_skills.classify_text(""), [])
        self.assertEqual(oop_skills.classify_text("今天天气不错"), [])

    def test_teach_lines_contain_key_sections(self):
        text = "\n".join(oop_skills.teach_lines("K12"))
        self.assertIn("K12", text)
        self.assertIn("要点", text)
        self.assertIn("常见坑", text)
        self.assertIn("自查", text)

    def test_map_compiler_error(self):
        log = "main.cpp(12): error C2065: 'total': undeclared identifier"
        mapped = oop_skills.map_compiler_error(log)
        self.assertTrue(mapped)
        self.assertEqual(mapped[0]["skill"], "K01")
        self.assertTrue(mapped[0]["how"])

    def test_map_compiler_error_for_const_and_private(self):
        gcc = "error: passing 'const Student' as 'this' argument discards qualifiers"
        clang = ("error: no matching member function for call to 'show'\n"
                 "note: candidate function not viable: 'this' argument has type "
                 "'const Student', but method is not marked const")
        self.assertEqual(oop_skills.map_compiler_error(gcc)[0]["skill"], "K05")
        self.assertEqual(oop_skills.map_compiler_error(clang)[0]["skill"], "K05")
        self.assertEqual(
            oop_skills.map_compiler_error("error: 'int Student::id' is private within this context")[0]["skill"],
            "K01")
        self.assertEqual(oop_skills.map_compiler_error("all good"), [])

    def test_map_review_rule(self):
        self.assertEqual(oop_skills.map_review_rule("R01"), "K12")
        self.assertEqual(oop_skills.map_review_rule("R02"), "K10")
        self.assertIsNone(oop_skills.map_review_rule("R99"))


def _report(passed: int = 0, total: int = 3, compiled: bool = True,
            verdict: str = "AC", compile_log: str = "") -> oop_judge.JudgeReport:
    report = oop_judge.JudgeReport()
    report.compiled = compiled
    report.compile_log = compile_log
    report.cases = [oop_judge.CaseResult(i + 1, i < passed,
                                         verdict="AC" if i < passed else verdict,
                                         line=0 if i < passed else 1,
                                         exp_line="1 2", act_line="2 1")
                    for i in range(total)]
    return report


class TestCoach(unittest.TestCase):
    def setUp(self):
        oc.set_color_enabled(False)
        self.tmp = tempfile.mkdtemp(prefix="oop_coach_")
        self.path = os.path.join(self.tmp, "profile.json")
        self.problem = oop_bank.find("b01")
        # 日志写到临时目录, 不要污染真实 data/
        self._log_file, self._log_jsonl = oop_coach.LOG_FILE, oop_coach.LOG_JSONL
        oop_coach.LOG_FILE = os.path.join(self.tmp, "log.md")
        oop_coach.LOG_JSONL = os.path.join(self.tmp, "log.jsonl")

    def tearDown(self):
        oop_coach.LOG_FILE, oop_coach.LOG_JSONL = self._log_file, self._log_jsonl
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_blank_profile(self):
        profile = oop_coach.LearnerProfile(self.path)
        self.assertEqual(profile.level(), 1)
        self.assertEqual(profile.mastery("K04"), 0.0)
        self.assertEqual(profile.practised(), [])
        self.assertFalse(profile.records)

    def test_record_attempt_updates_mastery(self):
        profile = oop_coach.LearnerProfile(self.path)
        record = profile.record_attempt(self.problem, _report(passed=3, total=3))
        self.assertIn("K01", record["skills"])
        self.assertTrue(record["all_passed"])
        self.assertGreater(profile.mastery("K01"), 0.4)
        self.assertIn("K01", profile.practised())
        self.assertTrue(profile.weakest(1))

    def test_repeated_failures_lower_mastery(self):
        profile = oop_coach.LearnerProfile(self.path)
        for _ in range(4):
            profile.record_attempt(self.problem, _report(passed=0, total=3, verdict="WA"))
        self.assertLess(profile.mastery("K01"), 0.2)
        self.assertEqual(profile.streak(), (0, 4))

    def test_streak_and_level(self):
        profile = oop_coach.LearnerProfile(self.path)
        for pid in ("b01", "b02", "b03", "b04", "b05"):
            profile.record_attempt(oop_bank.find(pid), _report(passed=3, total=3))
        wins, losses = profile.streak()
        self.assertEqual(wins, 5)
        self.assertEqual(losses, 0)
        self.assertIn(profile.level(), (1, 2))
        self.assertTrue(profile.level_label())

    def test_review_penalty_applies_to_related_skill(self):
        profile = oop_coach.LearnerProfile(self.path)
        problem = oop_bank.find("i01")           # K04 / K12
        profile.record_attempt(problem, _report(passed=3, total=3))
        before = profile.mastery("K12")
        findings = [oop_review.Finding("R03", "warn", "自赋值未处理")]
        profile.note_review(problem, findings)
        self.assertLess(profile.mastery("K12"), before)
        self.assertEqual(profile.count("review"), 1)

    def test_local_plan_returns_reasoned_assignments(self):
        profile = oop_coach.LearnerProfile(self.path)
        assignments = oop_coach.local_plan(profile, count=3)
        self.assertTrue(assignments)
        for item in assignments:
            self.assertTrue(item.reasons)
            self.assertTrue(item.skills)
            self.assertLessEqual(item.problem["level"], 2)   # 新手不该被派高级题
        self.assertTrue(oop_coach.render_plan({"profile_level": 1, "target_level": 1,
                                               "assignments": assignments, "notes": []}))

    def test_plan_skips_already_passed_problems(self):
        profile = oop_coach.LearnerProfile(self.path)
        profile.record_attempt(self.problem, _report(passed=3, total=3))
        planned = oop_coach.local_plan(profile, count=5)
        self.assertNotIn("b01", [a.problem["id"] for a in planned])

    def test_plan_offline_is_safe(self):
        profile = oop_coach.LearnerProfile(self.path)
        result = oop_coach.plan(profile, count=2, local_only=True)
        self.assertTrue(result["assignments"])
        self.assertEqual(result["notes"], [])

    def test_diagnose_compile_error(self):
        report = _report(compiled=False, compile_log="a.cpp(3): error C2065: 'x': undeclared identifier")
        diag = oop_coach.diagnose(self.problem, report=report)
        self.assertEqual(diag.verdict, "CE")
        self.assertIn("K01", diag.skills)
        self.assertTrue(oop_coach.render_diagnosis(diag))

    def test_diagnose_wrong_answer_and_pass(self):
        wa = oop_coach.diagnose(self.problem, report=_report(passed=1, total=3, verdict="WA"))
        self.assertEqual(wa.verdict, "WA")
        self.assertIn("主逻辑方向", wa.headline)
        ok = oop_coach.diagnose(self.problem, report=_report(passed=3, total=3))
        self.assertIn("全部用例通过", ok.headline)

    def test_diagnose_without_report(self):
        diag = oop_coach.diagnose(self.problem, report=None)
        self.assertEqual(diag.verdict, "NA")
        self.assertTrue(diag.next_steps)

    def test_diagnose_groups_findings_by_skill(self):
        findings = [oop_review.Finding("R02", "warn", "虚析构缺失", line=3)]
        problem = oop_bank.find("i04")           # 虚函数多态
        diag = oop_coach.diagnose(problem, report=_report(passed=3, total=3), findings=findings)
        self.assertIn("K10", diag.skills)
        self.assertTrue(any("写法问题" in title for title, _ in diag.sections))

    def test_profile_render_and_log_roundtrip(self):
        profile = oop_coach.LearnerProfile(self.path)
        profile.record_attempt(self.problem, _report(passed=3, total=3))
        self.assertTrue(profile.render())

        self.assertTrue(oop_coach.log_event("judge", "测试日志", ["- 一行内容"], pid="b01"))
        recent = oop_coach.log_recent(5)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["pid"], "b01")
        # 颜色转义不能写进日志文件
        self.assertNotIn("\033[", oc.read_text(oop_coach.LOG_FILE))
        self.assertTrue(oop_coach.render_log(5))

    def test_log_recent_on_empty_file(self):
        self.assertEqual(oop_coach.log_recent(3), [])
        self.assertTrue(oop_coach.render_log(3))


if __name__ == "__main__":
    unittest.main(verbosity=2)
