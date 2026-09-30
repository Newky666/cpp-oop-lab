# C++ Object-Oriented Training Camp · OOP Lab

[中文](README.md) | **English**

> **One command into the menu, one workspace for all problems, learn the knowledge point before you code.**
>
> 40 graded built-in problems (including MFC problems aligned with the textbook *Visual C++ Object-Oriented and Visual Programming, 5th Edition*) +
> online problem fetching from Luogu / dotcpp / Codeforces / GitHub / any website →
> adaptive scheduling → **read the knowledge handout first** → write code in **VSCode or Visual Studio** →
> one-click judging (line-by-line diff) → **teacher-style diagnosis (what's wrong, which concept you missed, how to fix it)** →
> learning profile + learning log.
>
> Pure Python standard library. Zero third-party dependencies.

![deps](https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen) ![platform](https://img.shields.io/badge/platform-Windows%2010%2F11-informational) ![problems](https://img.shields.io/badge/problems-40-blue) ![skills](https://img.shields.io/badge/knowledge%20points-33-orange) ![textbook](https://img.shields.io/badge/textbook-Visual%20C%2B%2B%205th%20Ed-yellowgreen) ![editor](https://img.shields.io/badge/editor-VSCode%20%7C%20Visual%20Studio-success)

---

## Table of Contents

- [1. What problem does it solve](#1-what-problem-does-it-solve)
- [2. Quick start](#2-quick-start)
- [3. One menu for everything](#3-one-menu-for-everything)
- [4. Learn first, practice later](#4-learn-first-practice-later)
- [5. One unified workspace (VSCode + Visual Studio)](#5-one-unified-workspace-vscode--visual-studio)
- [6. Teacher mode](#6-teacher-mode)
- [7. Problem overview (40 problems)](#7-problem-overview-40-problems)
- [8. Command reference](#8-command-reference)
- [9. Auto-correction: judging + review + diagnosis](#9-auto-correction-judging--review--diagnosis)
- [10. Learning profile & log](#10-learning-profile--log)
- [11. Multi-source problem fetching](#11-multi-source-problem-fetching)
- [12. Environment self-check](#12-environment-self-check)
- [13. File layout](#13-file-layout)
- [14. Implementation design](#14-implementation-design)
- [15. Adding your own problems](#15-adding-your-own-problems)
- [16. GUI and the exe](#16-gui-and-the-exe)
- [17. Known limitations](#17-known-limitations)

---

## 1. What problem does it solve

After the "classes and objects" chapter, textbook examples all make sense, but writing your own code turns into a mess:

- Can't abstract a class, everything crammed into one `main`;
- Data members all `public`, encapsulation in name only;
- Wrote a destructor but forgot the copy constructor, occasional crashes;
- Uses `if-else` to test types where a virtual function belongs;
- No way to know if the code is right, and nobody to point it out immediately;
- Switching editors means reconfiguring build and debug from scratch.

How this project responds:

| Pain point | Mechanism |
| --- | --- |
| Don't know what to do | **One menu**: scheduling / study / practice / judge / profile / fetch / self-check |
| Practice before understanding | **Learn first, practice later**: every problem ships a `knowledge.md` handout |
| Environment won't set up | **One unified workspace**: one config + `oop_lab.sln`, F5 works in both VSCode and VS |
| Don't know what to practice | **Adaptive scheduling**: picks 3 problems by weak skills + difficulty, with reasons |
| Too easy / too hard | Two wins in a row raise half a tier, two losses lower half a tier |
| Don't know if it's correct | `judge` compiles + runs all cases, **shows line-by-line diffs** |
| Don't know what's wrong | `diagnose` translates compiler errors / crash codes / diffs into **concept + explanation** |
| Nobody reviews | `submit` produces a **review request with full context** |

---

## 2. Quick start

> **Don't want the command line?** Jump to [16. GUI and the exe](#16-gui-and-the-exe):
> double-click `OOPLab.exe`, a window opens — pick a problem, read the handout, write code, judge, all inside.

**Prerequisites**

- Windows 10/11
- Python 3.8+ (if `python` points to the Microsoft Store stub, use **`py`**)
- A C++ compiler (`doctor` tells you what you have):
  - **MSVC**: install Visual Studio, check "Desktop development with C++"
  - **MinGW-w64**: install and add `g++` to `PATH`
- Editor: VSCode (with the C/C++ extension) or Visual Studio

**Just two commands**

```bat
cd d:\code\cpp-oop-lab
py oop_lab.py doctor     :: one-time check of compiler / editor / problem bank
py oop_lab.py            :: enter the interactive main menu
```

No command line? **Double-click `oop_lab.bat`** — same menu, pauses on exit.

**To walk through once in order**

```bat
py oop_lab.py plan              :: coach schedules: which problems, why
py oop_lab.py study b04         :: learn first: this problem's knowledge handout
py oop_lab.py new b04           :: generate the problem folder and open the workspace
:: ... write main.cpp in VSCode / VS ...
py oop_lab.py judge b04         :: judge + teacher diagnosis + update profile
py oop_lab.py submit b04        :: produce a submission package for AI/teacher review
```

---

## 3. One menu for everything

```
========================================================================
  C++ Object-Oriented Training Camp · OOP Lab   from classes to MFC
========================================================================
  Progress 3/22   [######..........]  14.3%   Tier 1 · Basics   MSVC (cl.exe)
  Workspace: D:\code\cpp-oop-lab\workspace
------------------------------------------------------------------------
  1)  Coach schedules today's problems
  2)  Study knowledge points (learn first)
  3)  Problem list
  4)  View a problem (statement)
  5)  Start a problem (generate project and open editor)
  6)  Judge the current problem (compile + cases + diagnosis)
  7)  Code review (12 OOP rules)
  8)  My learning profile (33 knowledge points)
  9)  Learning log
  10) Fetch / import problems online
  11) View a problem's reference solution
  12) Open the VSCode workspace
  13) Open Visual Studio
  14) Environment self-check
  15) Bank self-test (compile all 40 reference solutions)
  0)  Quit

Choose [0-15]:
```

Notes:

- Menu items that need a problem id **ask for it**; press Enter to use the coach's pick;
- Each step returns to the menu automatically — no need to retype commands;
- When output is redirected (scripts, CI) it won't hang in the menu — it falls back to the overview panel,
  so `py oop_lab.py > out.txt` is safe.

---

## 4. Learn first, practice later

In each problem folder, **the first thing is not code — it's `knowledge.md`**:

```
b01-student-class/
├── knowledge.md     ← read first: key points / common pitfalls / correct examples / self-questions
├── problem.md       ← read next: the statement (top reminds you to read the handout first)
├── main.cpp         ← write last
├── tests/01.in 01.out ...
└── b01-student-class.vcxproj
```

Handouts come from a unified graph of 33 knowledge points (17 C++ OOP + 16 MFC/Windows points from textbook ch.2–8). For example `b01` carries:

```
## K01 Class & Encapsulation    <sub>Tier 1</sub>

Bundle "data" and "functions that operate on data" into one type, and hide the data,
exposing only the necessary interface.

### Key points
1. class defaults to private, struct to public — prefer class + explicit public:.
2. Data members are always private; expose what's needed via getters, not public members.
...
### Common pitfalls
- Making data members public kills encapsulation;
- A getter/setter for every member turns private into decoration — expose meaningful operations.
...
### Correct example
    class Account {
    private:
        double balance_;
    public:
        explicit Account(double init) : balance_(init) {}
        void deposit(double amount);
        double balance() const;
    };

### Self-questions before coding
> Can the outside change this class's data freely? Are all mutation paths validated?
```

Don't want to leave the terminal:

```bat
py oop_lab.py study b04        :: print every knowledge handout for b04
py oop_lab.py study K12        :: view a single knowledge point
py oop_lab.py skills           :: list all 33 knowledge points
```

---

## 5. One unified workspace (VSCode + Visual Studio)

There is one workspace; all config lives at the **top level**, each problem is just a subfolder:

```
workspace/
├── oop_lab.code-workspace        ← double-click this to open VSCode
├── oop_lab.sln                   ← open this in Visual Studio
├── build.bat / run_case.bat      ← shared by the whole bank (take parameters)
├── .vscode/
│   ├── tasks.json               build/run "the currently open file"
│   ├── launch.json              debug "the currently open file"
│   ├── c_cpp_properties.json / settings.json / extensions.json
├── b01-student-class/
│   ├── knowledge.md  problem.md  main.cpp
│   ├── tests/01.in 01.out ...
│   └── b01-student-class.vcxproj
├── b04-deep-copy-array/ ...
└── i01-mystring-rule-of-three/ ...
```

### VSCode (recommended)

1. `File → Open Folder` → pick `workspace` (**once only**, not once per problem)
2. Open any problem on the left, edit its `main.cpp`
3. `Ctrl+Shift+B` builds — it compiles **the file you currently have open**, output is always
   `<problem folder>/build/main.exe`
4. `F5` debugs (builds first, runs in a separate console where you can type input)
5. Run a specific case: `Terminal → Run Task → Run current problem · case N` (1–4)

The key is "the currently open file": switching problems is just switching files — zero config changes.

### Visual Studio

1. Open `workspace\oop_lab.sln`
2. In Solution Explorer, right-click the problem you want → **Set as Startup Project**
3. `F5` debug / `Ctrl+F5` run

The generated `.vcxproj` has a few deliberate settings:

| Setting | Why |
| --- | --- |
| `PlatformToolset` inferred from the installed MSVC version | Otherwise MSBuild treats it as VS2010 and errors `MSB8020`; override with `OOP_PLATFORM_TOOLSET` |
| `TargetName = main` | Output is `build\main.exe`, identical to `judge` and VSCode |
| `/utf-8` | Chinese comments/strings in source don't garble |
| `stdcpp17` + `Console` subsystem | Matches the bank's compile flags |
| `Debug|x64` and `Release|x64` | Debug for practice, Release when you want speed |

> Each problem is a separate VS project; `oop_lab.sln` is regenerated from the actual workspace contents
> (GUIDs are derived deterministically from folder names, so they don't change).

### Output is identical everywhere

| Entry point | Output |
| --- | --- |
| VSCode `Ctrl+Shift+B` | `<problem folder>/build/main.exe` |
| Visual Studio `F5` | `<problem folder>/build/main.exe` |
| `build.bat <cpp>` | `<problem folder>/build/main.exe` |
| `py oop_lab.py judge b04` | `<problem folder>/build/main.exe` |

---

## 6. Teacher mode

### 6.1 Knowledge graph (33 points)

| Tier | Knowledge points |
| --- | --- |
| Basics | `K01` Class & encapsulation · `K02` Constructors & init lists · `K03` Destructors & lifetime · `K04` Copy & deep copy · `K05` const correctness & this · `K06` static members & factories · `K07` Operator overloading |
| Intermediate | `K08` Inheritance & derivation · `K09` Virtual functions & polymorphism · `K10` Abstract classes & virtual destructors · `K11` Friends · `K12` Copy control & Rule of Three · `K17` Composition & aggregation (has-a) |
| Advanced | `K13` Class templates & specialization · `K14` RAII & smart pointers · `K15` Design patterns · `K16` Multiple & virtual inheritance |
| Visual · MFC | `K18` Windows basics & message mechanism · `K19` Device context & GDI · `K20` Mapping modes & coordinates · `K21` Fonts & text · `K22` Keyboard · `K23` Mouse · `K24` Menus & accelerators · `K25` Dialogs & DDX · `K26` Bitmaps & icons · `K27` Basic controls · `K28` List & combo boxes · `K29` Scrollbars & common controls · `K30` Document/view & serialization · `K31` Command routing & context menus/toolbars · `K32` Multimedia · `K33` Message maps & MFC skeleton |

Problem tags are mapped to knowledge points by "longest keyword hit"; problems imported from Luogu/dotcpp/CF have their
concepts guessed from statement and title, and still participate in profile and scheduling.

### 6.2 Adaptive scheduling

```bat
py oop_lab.py plan
```

```
Today's problems
------------------------------------------------------------------------------
Current tier: Tier 1 · Basics    Target difficulty: Tier 1

1. b04  Deep copy: array class with a pointer
   [gate problem] ★☆☆ destructors & lifetime, copy & deep copy
   · covers your weak points: destructors & lifetime / copy & deep copy
   Start: py oop_lab.py new b04

3. lg:P1109  Student grouping
   [extension problem] ★☆☆ class & encapsulation
   · extension problem from Luogu (no auto judge, verify yourself)
```

Scoring: `0.45×concept gain + 0.25×difficulty fit + 0.20×freshness + 0.10×source credibility`.
Hard rules: passed problems are never re-assigned; problems whose related concepts are all mastered ≥ 0.8 are excluded
("never too easy"); difficulty spans at most one tier; no three in a row on the same concept;
two wins in a row +half tier, two losses −half tier.

### 6.3 Judging correctness

```
[RE] Runtime error   case 1/4  exit code 3221226356 (0xC0000374) | heap corruption: almost surely double free or out-of-bounds write (missing deep copy?)

Teacher comment · RE
------------------------------------------------------------------------------
The program crashed — this kind of issue is almost always memory or bounds.

【Runtime error diagnosis】
Check in order of likelihood:
  · Array out-of-bounds / null dereference — most common in index loops and pointer members.
  · Double free — usually a missing deep copy, two objects share one block.
  · Divide/mod by zero.
  · Stack overflow from too-deep recursion.
```

Three kinds of input are translated into "concept + why + how to fix":

| Input | How it's used |
| --- | --- |
| Compiler errors | Regex-matched to knowledge points (covers GCC / clang / MSVC, Chinese & English), explained one by one |
| Runtime failure | Windows crash codes translated to plain language (`0xC0000374` heap corruption / `0xC0000005` access violation / `0xC00000FD` stack overflow …) with a check order |
| Case diffs | Expected vs actual shown line by line, with different checklists for "none pass / partial / all pass" |

### 6.4 Recording

See [section 10](#10-learning-profile--log).

---

## 7. Problem overview (40 problems)

> **Textbook alignment**: tier 4 `v01~v18` aligns with Huang Weitong & Tong Junbo,
> *Visual C++ Object-Oriented and Visual Programming (5th Edition)* (Higher Education Press), **full coverage of chapters 1–8**:
> `v01~v03` ch.1 C++ details (console, auto-judge);
> `v04~v14` ch.2–6 (GDI / pens & brushes / mapping modes / fonts & text / mouse & keyboard /
> menus / dialogs / bitmaps / buttons & edit boxes / list boxes / progress bars);
> `v15~v18` ch.7–8 (document/view serialization / context menus / toolbars & status bars / multimedia).
> MFC problems need VS's MFC component (see [12. Environment self-check](#12-environment-self-check)); without it,
> judging degrades to "checkpoint check" (verifies correct use of CDC / CPen / message maps), install it and they really compile.

### Tier 1 · Basics ★☆☆ — a class from scratch

| ID | Problem | Concepts |
| --- | --- | --- |
| `b01` | Student class: encapsulation & const member functions | class definition / access control / constructors / `const` member functions |
| `b02` | Date class: constructor init list & leap year | init lists / member encapsulation / logic encapsulation |
| `b03` | Lifecycle trilogy: constructor / copy / destructor | object lifetime (class-definition fill-in) |
| `b04` | Deep copy: array class with a pointer | copy constructor / deep copy / `new[]` & `delete[]` |
| `b05` | const member functions & value semantics: Point | `const` correctness / `this` / return by value |
| `b06` | static members: invoice serial-number factory | `static` data members / static factory / copy pitfalls |
| `b07` | Operator overloading intro: Complex | `operator+ - == << >>` / friends |

### Tier 2 · Intermediate ★★☆ — inheritance & polymorphism

| ID | Problem | Concepts |
| --- | --- | --- |
| `i01` | Rule of Three: implement your own string class | copy assignment / self-assignment / Rule of Three |
| `i02` | Inheritance: employee & manager | derived construction / `protected` / member overriding |
| `i03` | Construction & destruction order | ctor/dtor order along an inheritance chain |
| `i04` | Virtual functions & runtime polymorphism: draw shapes via base pointer | virtual / base-pointer container / template method |
| `i05` | Abstract class & virtual destructor | pure virtual / abstract / **why virtual destructors matter** |
| `i06` | Friends: `operator*` and a helper class | friend function / friend class / encapsulation boundary |
| `i07` | Advanced operator overloading: Fraction | overloading / invariant maintenance / Euclid's algorithm |
| `i08` | Composition (has-a): order & discount | composition vs inheritance / member lifetime / reference returns / const correctness |

### Tier 3 · Advanced ★★★ — design in code

| ID | Problem | Concepts |
| --- | --- | --- |
| `a01` | Class template: implement `MyVector<T>` | class templates / dynamic growth / `operator[]` / deep copy |
| `a02` | Template specialization for `bool` and `double` | full specialization |
| `a03` | RAII: implement a unique smart pointer | RAII / `= delete` / resource management |
| `a04` | Design pattern: singleton Logger | singleton / static local / no-copy |
| `a05` | Design pattern: factory method + `unique_ptr` | factory / smart pointers / error handling |
| `a06` | Design pattern: observer (pub-sub) | observer / interface + polymorphism |
| `a07` | Multiple & virtual inheritance: diamond | multiple inheritance / `virtual` base / construction order |

### Tier 4 · Visual · MFC ◆◆◆◆ — textbook 5th ed.

| ID | Problem | Concepts | Textbook |
| --- | --- | --- | --- |
| `v01` | Nested class: student report card | nested classes / member objects | 1.2.2 |
| `v02` | Inline methods: two ways | in-class (implicit) / `inline` out-of-class (explicit) | 1.2.3 |
| `v03` | Class pointers & this: chained calls | `new`/`delete` / `p->` / return `*this` | 1.6 |
| `v04` | CDC drawing: line / rectangle / ellipse | `CPaintDC` / `MoveTo`+`LineTo` / `Rectangle` / `Ellipse` | 2.5~2.6 |
| `v05` | Pens, brushes & colors | `CPen` / `CBrush` / `RGB` / restore old objects after `SelectObject` | 2.4 |
| `v06` | Mouse & keyboard | `ON_WM_LBUTTONDOWN` / `OnKeyDown` / `CPoint` / `VK_ESCAPE` | ch.4 |
| `v07` | Fonts & text output | `CFont` / `CreatePointFont` / `SetTextColor` / `SetBkMode` / centered `DrawText` | ch.3 |
| `v08` | Mapping mode: draw in millimeters | `SetMapMode(MM_LOMETRIC)` / 0.1mm logical units / y-axis up | 2.3 |
| `v09` | Menus & command response | dynamic `CMenu` / `ON_COMMAND` / command ID | 5.1 |
| `v10` | Modal dialog & DDX | `DoModal` / `DDX_Text` / `UpdateData` / `OnInitDialog` (needs .rc) | 5.3 |
| `v11` | Bitmaps & BitBlt | `CBitmap` / `CreateCompatibleDC` / `SelectObject` / `BitBlt` | 5.2 |
| `v12` | Buttons & edit boxes | programmatic `CButton` / `ON_BN_CLICKED` / `Get/SetDlgItemText` | 6.2 · 6.5 |
| `v13` | List boxes & selection | `CListBox` / `AddString` / `GetCurSel` checks `LB_ERR` / `ON_LBN_SELCHANGE` | 6.6 |
| `v14` | Progress bars & timers | `CProgressCtrl` / `SetRange32` / `SetPos` / `SetTimer` + `OnTimer` | 6.8 |
| `v15` | Document/view & serialization | `CDocument` / `CView` / `Serialize` / `CArchive` / `CSingleDocTemplate` (needs .rc) | 7.1~7.2 |
| `v16` | Context menus & command routing | `ON_WM_CONTEXTMENU` / `CreatePopupMenu` / `TrackPopupMenu` | 7.3~7.4 |
| `v17` | Multimedia: play sound | `PlaySound` / `SND_ASYNC` / `SND_PURGE` / `winmm.lib` / MCI | ch.8 |
| `v18` | Toolbars & status bars | `CToolBar` / `LoadToolBar` / `CStatusBar` / `SetIndicators` (needs .rc) | 7.5 |

Every problem ships: `knowledge.md` handout + statement + itemized requirements + samples + hints + **pre-submit checklist** +
a skeleton with `TODO` (**headers are NOT written out — they're hinted so you fill in `#include` yourself**, `using namespace std;` is pre-filled) + auto-judge cases
(checkpoint check for MFC problems) + reference solution (unlocked after passing).

---

## 8. Command reference

```bat
:: ——— daily (really only the first one matters) ———
py oop_lab.py                     interactive main menu (double-click oop_lab.bat)
py oop_lab.py menu                enter the menu explicitly
py oop_lab.py open                open the unified workspace in VSCode
py oop_lab.py open-vs             open oop_lab.sln in Visual Studio

:: ——— teacher mode ———
py oop_lab.py plan                schedule today's problems (with reasons)
py oop_lab.py plan -n 5           more problems; --local-only uses only the local bank
py oop_lab.py study b04           learn first: this problem's handout
py oop_lab.py study K12           view one knowledge point
py oop_lab.py diagnose b04        teacher diagnosis: what's wrong / which concept / how to fix
py oop_lab.py profile             learning profile: 33 concept scores + overall tier
py oop_lab.py log -n 10           learning log

:: ——— fetch / practice ———
py oop_lab.py list                problem list (-l 2 intermediate only, -t <tag> by concept)
py oop_lab.py show b01            view statement
py oop_lab.py new b01             generate/complete this problem and open the workspace
py oop_lab.py new b01 --force     overwrite main.cpp too (default keeps your code!)

:: ——— verify ———
py oop_lab.py judge b01           compile + run cases + diagnose + update profile & log
py oop_lab.py run b01 --case 2    compile and run case 2
py oop_lab.py review b01          OOP code review (12 rules) + style score

:: ——— wrap up ———
py oop_lab.py submit b01          produce a submission package for AI/teacher review
py oop_lab.py submit b01 -m "not sure if I need a virtual destructor"
py oop_lab.py solution b01        view the reference solution (unlocked after pass, --force to peek)

:: ——— bank / online ———
py oop_lab.py progress            progress & stats (XP / time / submissions)
py oop_lab.py search segment-tree multi-source search (source list is editable)
py oop_lab.py pull P1001          import a Luogu problem (1049=dotcpp, CF4A=Codeforces)
py oop_lab.py pull <any-url>      import from any website's problem page
py oop_lab.py sources             manage problem sources (add/remove/enable/disable)

:: ——— self-check ———
py oop_lab.py doctor              environment self-check (compiler / editor / bank health)
py oop_lab.py selftest            compile every reference solution once
py -m unittest discover -s tests -t .     regression tests (167: 103 CLI/bank + 64 GUI)
```

Global flags: `--no-color` (disable color), `-v` (debug log + show actual case output).

---

## 9. Auto-correction: judging + review + diagnosis

### `judge`

```
[WA] Wrong answer   case 1/3   output mismatch

Case 1 diff (line 1):
  expected: '1001 Tom 88'
  actual:   '1001 88 Tom'
```

Comparison rules: **normalize newlines → strip trailing whitespace per line → strip leading/trailing blank lines**, then strict line-by-line
compare (leading whitespace is kept — it's meaningful). Compile errors are printed verbatim, first 40 lines.

### `review`: 12 OOP heuristic rules

| Rule | Level | Checks |
| --- | --- | --- |
| `R00` | error | Problem requires a class but there's no `class` / `struct` |
| `R01` | warn | Has a destructor but no copy ctor / copy assignment (Rule of Three broken) |
| `R02` | warn | Has virtual functions but the destructor isn't `virtual` |
| `R03` | warn | `operator=` doesn't handle self-assignment |
| `R04` | warn | Mismatched `new`/`delete`, or `new[]` paired with `delete` |
| `R05` | warn | Member takes `const X&` but isn't marked `const` itself |
| `R06` | warn | `class A : B` — default **private inheritance** |
| `R07` | warn | Leftover `TODO` |
| `R08` | hint | `using namespace std;` |
| `R09` | hint | `printf` / `scanf` / `strcpy` and other C-style or unsafe functions |
| `R10` | hint | Overriding a virtual function without `override` |
| `R11` | hint | `<bits/stdc++.h>` is non-portable |
| `R12` | hint | Lots of `std::endl` |

Every rule is bound to a knowledge point, so review results feed directly into that point's penalty in the profile.
Review is a heuristic that **prefers false negatives over false positives**; the style score is just a reference.

---

## 10. Learning profile & log

```bat
py oop_lab.py profile
```

```
Overall tier: Tier 1 · Basics   (1 pass streak / 0 fail streak)
Practice count: judged 3 · reviewed 1 · submitted 0 · studied 1 day
Total judging time: 12.4 s

Tier 1 · Basics
  K01 class & encapsulation  █████······· proficient
  K02 constructors & init    █████······· proficient
  K03 destructors & lifetime ············ not practiced
  K04 copy & deep copy       ██████······ getting there  2 tries (1 pass)
```

**How mastery is computed**:

```
good       = full-pass count + 0.55 × partial-pass count
raw        = good / attempts
confidence = min(1, attempts / 3)          ← one attempt never gets full marks
score      = raw × (0.55 + 0.45 × confidence) − review penalty (max −0.30)
plus forgetting decay: each day past 7 untouched multiplies by 0.95 (floor 0.6)
```

Overall tier is decided by the "concept coverage" (share of concepts scored ≥ 0.7) across three tiers — it won't jump
because of one lucky pass.

**Learning log** (two files, both in `data/`):

| File | Purpose |
| --- | --- |
| `learning_log.md` | Human-readable markdown; appends a section on every new/judge/review/submit/schedule (color codes stripped, usable as notes) |
| `learning_log.jsonl` | Structured event stream, read by `py oop_lab.py log` for display |

---

## 11. Multi-source problem fetching

```bat
py oop_lab.py search segment-tree
py oop_lab.py search score --source dotcpp
py oop_lab.py sources             :: view/edit the source list
```

The source list lives in `data/sources.json`, **freely editable**:

| kind | Description |
| --- | --- |
| `luogu` | Luogu: difficulty + tags, full statement scraping |
| `dotcpp` | C Language Net: titles carry category prefixes like `[编程入门]` |
| `codeforces` | Codeforces: no-auth API for tag + rating, precise difficulty targeting |
| `github` | Recommends curated practice repos (public search API, falls back to a hand-picked list) |
| `bing` | Web fallback |
| `generic` | **Any website**: give a search URL with `{q}` plus one item regex |

Add a custom site (Nowcoder, built-in but disabled by default):

```bat
py oop_lab.py sources --add nowcoder --kind generic --label Nowcoder ^
   --hosts nowcoder.com ^
   --search-url "https://ac.nowcoder.com/acm/problem/list?keyword={q}" ^
   --item-regex "href=\"(https://ac\.nowcoder\.com/acm/problem/\d+)\"[^>]*>\s*([^<]{4,90}?)\s*<"
py oop_lab.py sources --enable nowcoder
```

### Import any problem

```bat
py oop_lab.py pull P3373          :: Luogu
py oop_lab.py pull 1049           :: dotcpp
py oop_lab.py pull CF4A           :: Codeforces
py oop_lab.py pull https://noi.openjudge.cn/ch0101/01/     :: any site
```

Known domains use **dedicated parsers** (more accurate); unknown URLs use **generic extraction**:

1. Score blocks by "lots of text, few links" to find the body container (nav/sidebar excluded);
2. Convert HTML to text, split into sections by Chinese/English subheadings like "description / input / output / sample / hint";
3. Prefer "sample input/output" markers, otherwise pair `<pre>` blocks;
4. Run both container-based and full-page extraction, keep whichever looks more like a statement.

Verified sites: Luogu, dotcpp, Codeforces, OpenJudge, Nowcoder.
On import it guesses the difficulty tier (difficulty tag first, otherwise title keywords — dotcpp's
`[编程入门]` prefix correctly maps to tier 1) and guesses concepts from the statement.

> Imported problems **have no built-in cases**, so `judge` reports "no auto cases" and scheduling marks them
> **extension problems**, separate from gated problems. Add data under `tests/` yourself, or verify on the original site.
>
> JS-rendered sites (e.g. 51Nod) can't be scraped; the command prints a link for you to view —
> network failures never affect the local bank or judging.

---

## 12. Environment self-check

```bat
py oop_lab.py doctor
```

```
== C++ toolchain check ==
[OK] compiler      MSVC (cl.exe + vcvars64)  [C:\Program Files\...\vcvars64.bat]
     · MSVC only works through the vcvars64.bat environment; the judging script handles it
== directories ==
problem bank: D:\code\cpp-oop-lab
workspace:    D:\code\cpp-oop-lab\workspace
== editor ==
[OK] VSCode code command available: C:\Users\...\bin\code.CMD
[OK] Visual Studio available (open oop_lab.sln and F5)
     generated VS platform toolset: v145
== MFC support (textbook ch.2–8) ==
[OK] MFC available: ...\atlmfc\include\afxwin.h          ← this line when installed
[!] MFC component not installed — MFC problems only do checkpoint checks   ← this line when missing
     · install: VS Installer → Modify → Individual components →
       check "C++ MFC for latest v143 build tools (x86 & x64)", then reopen the terminal
== bank health ==
  [OK] 40 problems pass structural check
  imported problems: 0
```

> **MFC is optional but strongly recommended**: textbook ch.2–8 problems need it when practicing in Visual Studio
> (the VS project already sets `UseOfMfc`); without it you can still read handouts, write code and run checkpoint checks,
> but `judge` won't really compile — the verdict becomes "checkpoint check".

---

## 13. File layout

```
cpp-oop-lab/
├── oop_lab.py            unified CLI entry + interactive main menu
├── oop_lab.bat           double-click into the menu
├── oop_app.py            GUI entry (this is what's packaged into OOPLab.exe)
├── oop_app.bat           double-click to open the GUI (dev-time)
├── oop_gui_app.py        GUI main window: 3-pane layout / toolbar / status bar / wiring
├── oop_gui_editor.py     code editor widget (line numbers + C++ highlight + auto-indent + Ctrl+S)
├── oop_gui_tasks.py      background task runner (compiles/network without freezing the UI)
├── build_exe.py          one command to build the single-file exe
├── build_exe.bat         double-click to build
├── oop_common.py         utilities (terminal width/color / atomic JSON / output normalization / progress)
├── oop_html.py           low-level web tools (HTTP / encoding / HTML-to-text / whitespace normalization)
├── oop_web.py            generic statement extraction + configurable source registry
├── oop_bank_visual.py    tier-4 bank (18 problems, textbook 5th ed: 3 console + 15 MFC)
├── oop_lab_icon.py       icon data (64×64 PNG base64, generated by tools/make_ico.py)
├── tools/make_ico.py     icon generator (stdlib hand-drawn → multi-size oop_lab.ico)
├── oop_lab.ico           exe file icon (for PyInstaller --icon)
├── oop_skills.py         knowledge graph: 33 points + handouts + error/review rule maps
├── oop_coach.py          coach engine: profile / adaptive scheduling / diagnosis / log
├── oop_bank.py           bank aggregator (built-in + online, find/filter/structural check)
├── oop_bank_basic.py     tier-1 bank (7 problems, with reference solutions & cases)
├── oop_bank_adv.py       tier-2 bank (8 problems)
├── oop_bank_pro.py       tier-3 bank (7 problems)
├── oop_judge.py          compile & judging engine (MSVC / MinGW dual backend)
├── oop_review.py         OOP static review (12 rules)
├── oop_search.py         multi-source search (Luogu / dotcpp / Codeforces / GitHub / Bing / any site)
├── oop_workspace.py      unified workspace (VSCode config + VS solution + handouts + submissions)
├── tests/test_oop_lab.py CLI / bank regression tests (97, stdlib unittest)
├── tests/test_gui.py     GUI tests (54: highlight/indent/task queue/window/real-mainloop smoke)
├── data/                 runtime-generated: progress.json / profile.json / sources.json /
│                         user_problems.json / learning_log.md / learning_log.jsonl
└── workspace/            runtime-generated: unified practice workspace (see section 5)
```

Runtime files are in `.gitignore` (build artifacts, logs, profile); your `main.cpp` is tracked normally.

---

## 14. Implementation design

### Dual compiler backend

| Backend | How it's invoked |
| --- | --- |
| `g++` / `clang++` | Found directly on `PATH`, `-std=c++17 -O0 -g -Wall -Wextra` |
| MSVC `cl.exe` | `vswhere` locates the install (falls back to scanning common dirs) → a temp `.bat` calls `vcvars64.bat` then compiles |

Both backends set `set VSLANG=1033` to make MSVC speak English — Chinese error wording differs per machine,
making stable diagnosis impossible (the diagnosis table still keeps Chinese fallback rules).

Before judging, `SetErrorMode(SEM_NOGPFAULTERRORBOX)` disables Windows' "program has stopped working" popup:
without it, every crashing case on a wild pointer waits for the dialog timeout — 4 cases could drag to 21 s
(measured 3.4 s after).

### Three batch-file pitfalls (all hit)

1. **Encoding**: Chinese in a `.bat` is parsed by cmd using the console code page (GBK on Chinese systems); UTF-8
   bytes decode to garbage and can even split one line into several commands. → generated batches are **pure ASCII**
   (English prompts), Chinese goes in markdown; written with `encoding="ascii"`.
2. **Newlines**: must be CRLF; LF-only breaks labels and parenthesized blocks.
   → unified `write_bat()` / `write_text_crlf()` handle conversion.
3. **Trailing backslash in `/I"path\"`**: `%~dpI` naturally ends with `\`; writing it into `/I"...\"` **escapes the
   quote**, so MSVC thinks there's no source file (`error D8003`). → strip the trailing backslash after getting the dir.

Also, `rem` lines can't contain `<` `>` — cmd treats them as redirection.

### VS project & solution

- `PlatformToolset` must be written explicitly: otherwise it's treated as VS2010 and errors `MSB8020`.
  Inferred from `VC\Tools\MSVC\<version>`: `14.5x → v145` (VS18) / `14.3~14.4x → v143` (VS2022) /
  `14.2x → v142` (VS2019) / `14.1x → v141` (VS2017); override with `OOP_PLATFORM_TOOLSET`.
- Project GUIDs use `uuid5(problem folder name)`, deterministic — regenerating `.sln` doesn't change them.
- `TargetName=main` keeps VS output path identical to `judge` and VSCode.
- `.sln` / `.vcxproj` are written with CRLF so Visual Studio doesn't complain.

### Generic statement extraction

`oop_web.extract_problem()` **tries several ranges and keeps the best**: a specified container (e.g. Codeforces'
`div.ttypography`) → auto-detected body container → full-page fallback. Each is scored by
"reasonable description length + has input/output/hint + has samples − UI noise", keeping the highest.

Container detection is a slimmed-down readability: each block scores
`text length − 3 × link-text length`, then the deepest candidate near the top score wins.
Top bars and sidebars are link-dense and get excluded.

### Output comparison trade-offs

`normalize_output()` does exactly three things: normalize newlines, strip **trailing** whitespace, strip **leading/trailing**
blank lines. Deliberately avoided: ignoring case, collapsing inner spaces, ignoring leading whitespace — such "leniency"
would let genuine format errors slip through.

### Storage

Progress, profile, source config and imported problems all use "temp file in the same dir + `os.replace`" atomic writes;
a corrupted file falls back to empty rather than crashing the whole program.

---

## 15. Adding your own problems

Append a dict to `PROBLEMS` in any `oop_bank_*.py`:

```python
_p(
    id="b08",
    slug="my-problem",               # short English name, folder workspace/b08-my-problem
    title="My Problem",
    topics=["inheritance"],          # auto-mapped to knowledge points, drives the handout
    desc="statement background…",
    require=["requirement one", "requirement two"],
    io="input…output…",
    samples=[{"in": "1\n", "out": "1\n"}],
    hints=["hint"],
    checklist=["self-check point"],
    skeleton="// TODO: fill in headers (<iostream> etc)\nusing namespace std;\n// TODO: ...\nint main() { return 0; }\n",
    solution="…full compilable reference solution…",
    tests=[{"in": "1\n", "out": "1\n"}],
)
```

Then:

```bat
py oop_lab.py doctor --no-color     :: structural check, points out missing fields
py oop_lab.py selftest --id b08     :: compile the reference solution once, verify the answer
py oop_lab.py study b08             :: check topics landed on knowledge points
py oop_lab.py new b08               :: generate the problem folder + handout + VS project
```

To tweak teaching strategy:

| What to change | Where |
| --- | --- |
| Knowledge points, handout content, error/review rule maps | `oop_skills.py` |
| Mastery formula, scheduling weights, diagnosis wording | `oop_coach.py` |
| Difficulty tiers, keyword→tier, import flow | `oop_search.py` |
| Workspace file contents (tasks/launch/vcxproj/sln/handout templates) | `oop_workspace.py` |
| Generic extraction rules, source registry | `oop_web.py` |

---

## 16. GUI and the exe

Don't want the command line? **Double-click `OOPLab.exe`**. It shares the same bank, the same workspace and the same
progress/profile with the CLI — it just replaces "typing commands" with "clicking buttons".

```
┌────────────────────────────────────────────────────────────────────────────┐
│ OOP Lab — C++ Object-Oriented Training Camp                                │
│ [Plan][Study][Save][Judge F5][Review][Profile][Fetch][Open VSCode][Open VS][Check]│
├──────────────┬─────────────────────────────────────────────────────────────┤
│ ★☆☆ Basics   │ ┌ Handout ── Statement ── [My Code] ── Result ─────────────┐│
│  ● b01 Stud… │ │   1 │ // TODO: fill in headers                            ││
│  ○ b02 Date… │ │   2 │ using namespace std;                               ││
│ ★★☆ Inter…  │ │   4 │ class Student {                                    ││
│  ○ i01 Rul… │ │   5 │     // TODO                                        ││
├──────────────┴─────────────────────────────────────────────────────────────┤
│ compiler: MSVC (cl.exe) │ current b01 not started │ mastery: min 0% │ ready │
└────────────────────────────────────────────────────────────────────────────┘
```

- **Left**: problem tree grouped by tier, `0/7` is pass progress for that tier; ● passed / ◐ in progress / ○ not started.
  Click to switch problems — it generates or reads back that problem's project and your code.
- **Middle four tabs** in usage order: read the "Handout" → "Statement" → write in "My Code" → judge jumps to "Result".
- Shortcuts: **F5** judge, **Ctrl+S** save; a `*` in the title bar means unsaved.
- In the "Plan" and "Fetch" dialogs you can **double-click a row** to jump straight to that problem.

### Icon

The icon is **drawn by code** (`tools/make_ico.py`, pure stdlib: hand-drawn render → supersampled antialias →
PNG-in-ICO packed into 256/128/64/48/32/16 sizes):

```bat
py tools\make_ico.py         :: regenerate oop_lab.ico and oop_lab_icon.py
```

The design is a "class inheritance diagram": one parent block above, two child blocks below connected by lines
(dark-blue→purple gradient). `build_exe.py` passes `oop_lab.ico` to PyInstaller (file icon); the window's top-left uses
the embedded 64×64 PNG (`oop_lab_icon.py`) with no external file — it shows even in a single-file exe.

### Building from source

```bat
py build_exe.py              :: -> dist\OOPLab.exe   single file, ~9.7 MB (with icon)
py build_exe.py --onedir     :: -> dist\OOPLab\      folder version, faster startup
```

PyInstaller is a **build-time** tool; at runtime there are still zero third-party dependencies (the built exe already
bundles the Python interpreter and tkinter).

### Where the exe and its data live

The exe can sit in **any directory**; on first run it creates, **next to itself**:

```
D:\OOPLab\
├── OOPLab.exe
├── data\          ← progress / profile / learning log / imported problems
├── workspace\     ← practice workspace (same structure as the CLI)
└── oop_lab.log    ← startup & error log
```

So the recommended flow: make an empty folder → drop the exe in → double-click. To move machines, copy the whole folder —
progress goes with it.

### Startup failure?

The exe has no console, so you can't see errors. All startup info and exceptions go into **`oop_lab.log` next to the exe**;
on startup failure it also pops a message box with the stack trace.

### GUI vs CLI

| | GUI | CLI |
| --- | --- | --- |
| Entry | `OOPLab.exe` / `oop_app.bat` | `py oop_lab.py` / `oop_lab.bat` |
| Can do | plan / study / write / judge / review / profile / fetch / self-check | **everything** (incl. `submit` packages, `pull` imports, `sources` management) |

The CLI is fully kept; the two can be mixed (e.g. practice in the GUI, then `py oop_lab.py submit` to send to a teacher).

### How the UI stays responsive

A compile takes 2–5 s, network fetch up to 10 s, bank self-test tens of seconds — run those on the UI thread and the
window becomes "not responding". They're all delegated to `oop_gui_tasks.TaskRunner`: background thread runs, results go
into a queue, the main thread polls via `root.after()` every 50 ms. The slow buttons grey out while running, so no
state corruption from rapid clicking.

---

## 17. Known limitations

- Windows 10/11 only (batch files, `vcvars` detection, crash-code explanation, VS projects are all Windows-specific).
- Single-file problems only (`main.cpp`). For multi-file compilation, edit the generated project file.
- `review` and diagnosis are textual heuristics, not compiler-level semantic analysis: complex templates, macros, and
  multiple-inheritance edge cases may be missed. It's "post-coding self-check & guidance", not a grading tool.
- Mastery is a **heuristic relative value**, not an absolute level measure; its value is "compare with yourself and decide
  what to practice next".
- Online fetching parses each site's public pages/APIs; when they redesign, `oop_search.py` / `oop_web.py` may need syncing.
  Parsers are pure functions with fixed sample strings in tests — run the tests after editing to know if you broke anything.
- Imported problems have no built-in cases, so they can't be auto-judged — they're **extension problems** only.
- JS-rendered (pure front-end) sites can't be scraped; import will suggest viewing the link instead.
- **GUI known issues**:
  - The single-file exe extracts on first launch, ~**2–4 s** blank screen; afterwards it's normal (use `--onedir` for faster).
  - PyInstaller output is ~10 MB; some antivirus may false-positive — whitelist it.
  - The GUI **intentionally has no multi-file project**: it only knows each problem's `main.cpp`, consistent with the CLI.
  - The built-in editor is for "quick two-line edits" — no autocomplete, refactoring or go-to-definition;
    for heavy editing, click "Open VSCode" in the toolbar.

---

## License

MIT
