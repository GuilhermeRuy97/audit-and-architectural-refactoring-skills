# audit-and-architectural-refactoring-skills

Developing an AI skill that automates the analyzing, auditing, and refactoring any project to the MVC pattern, regardless of the technology.

> Skill Author: GuilhermeRuy97

## The Skill is capable of

* Analyzing a codebase, detecting the current language, framework, and architecture.
* Identifying anti-patterns and code smells, classifying them by severity with exact file and line information.
* Generating a structured audit report with all findings.
* Refactoring the project to the MVC (Model-View-Controller) pattern, eliminating the problems found.
* Validating the result, ensuring that the application continues to function after the changes.

## Classification Scales

### Definition of Severities

The project follows the following classification scale based on MVC and SOLID problems:

- CRITICAL: Critical architecture or security failures that prevent proper functioning, expose sensitive data (e.g. hardcoded credentials, SQL Injection) or violate completely the separation of responsibilities (e.g. "God Class" containing database, complex business logic and routing in the same file).
- HIGH: Strong violations of the MVC pattern or SOLID principles that make maintenance and testing very difficult (e.g. heavy business logic trapped inside Controllers, strong coupling without Dependency Injection, or global mutable state used throughout the application).
- MEDIUM: Problems of standardization, code duplication or moderate performance bottlenecks (e.g. N+1 queries in the database, inappropriate use of middlewares, missing validations in routes).
- LOW: Improvements in readability, bad variable naming, or "magic numbers" scattered throughout the code.

## Use Cases

In this project, we will use 3 projects as a testbed for refactoring.
1. code-smells-project/ (Python/Flask — API de E-commerce)
2. ecommerce-api-legacy/ (Node.js/Express — LMS API com fluxo de checkout)
3. task-manager-api/ (Python/Flask — API de Task Manager)

## Usage Examples on CLI (Command Line Interface)

```
# Execute the skill on the project with problems
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (products, users, orders, order_items)
Architecture:  Monolithic — all in 4 files, no separation of layers
Source files:  4 files analyzed
DB tables:     products, users, orders, order_items
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Single file contains all business logic, SQL queries, validation and formatting for 4 different domains.
Impact: Impossible to test in isolation, any change affects everything.
Recommendation: Separate into models and controllers by domain.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded as 'my-super-secret-key-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refactoring executed ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── product_model.py
│   └── user_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── product_controller.py
│   └── order_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Manual Analysis

Each project was read file-by-file and evaluated against the anti-pattern catalog. Findings are ordered CRITICAL → HIGH → MEDIUM → LOW. Full reports with exact file paths, code snippets, impact, and recommendations are linked below.

---

### Code Smells Project — Python/Flask E-commerce API

**[Full report](reports/audit-project-1.md)** · 4 files · ~782 lines · CRITICAL: 3 | HIGH: 3 | MEDIUM: 2 | LOW: 2 · **Total: 10**

| Severity | Finding | Why it matters |
|---|---|---|
| CRITICAL | SQL Injection throughout `models.py` | Every query is built by string concatenation — login can be bypassed with `' OR '1'='1`, and the search endpoint allows full data exfiltration |
| CRITICAL | Unauthenticated `/admin/query` endpoint | Accepts arbitrary SQL from the HTTP body with no auth; any caller can `DROP TABLE` or read all data with one request |
| CRITICAL | Hardcoded `SECRET_KEY` returned in `/health` response | The signing key is committed to git _and_ actively broadcast to every caller of the health-check endpoint |
| HIGH | Passwords stored and returned in plaintext | No hashing anywhere; `GET /usuarios` returns the `senha` field for every user to anonymous callers |
| HIGH | No authentication on any endpoint | Every route — including user list with passwords and order history — is open to anonymous HTTP requests |
| HIGH | `DEBUG=True` hardcoded in production config | Activates the Werkzeug interactive debugger, giving any uncaught-exception caller an in-browser Python shell |
| MEDIUM | N+1 queries in order listing | Three nested cursors: 1 + N + N×M queries for N orders with M items each |
| MEDIUM | Discount business logic inside the Model layer | Magic-number thresholds hardcoded alongside DB queries; cannot be tested or changed without touching data-access code |
| LOW | `print()` used as a fake notification system | Simulates email/SMS/push in stdout; operators believe notifications are working when they are not |
| LOW | Validation duplicated between create and update handlers | Same field-check block copy-pasted verbatim; rules can drift and produce inconsistent create vs. update behaviour |

---

### Ecommerce API Legacy — Node.js/Express LMS API

**[Full report](reports/audit-project-2.md)** · 3 files · ~180 lines · CRITICAL: 2 | HIGH: 5 | MEDIUM: 3 | LOW: 4 · **Total: 14**

| Severity | Finding | Why it matters |
|---|---|---|
| CRITICAL | Hardcoded production credentials (`dbPass`, `paymentGatewayKey`) | Live payment key and DB password committed to source; any repo reader can drain the payment account and delete all records |
| CRITICAL | No authentication or authorization on any endpoint | Financial report and user-deletion endpoints are fully open to anonymous HTTP requests |
| HIGH | `badCrypto` password hashing | A loop of base64-encode + truncate produces a 10-char output with no salt; the developer explicitly named it `badCrypto` |
| HIGH | Plaintext password in seed data | Seed user inserted with raw `'123'` in the `pass` column — no hash applied at all |
| HIGH | God Class — `AppManager` owns DB init, routing, payment, enrollment, and audit logging | No part of the business logic can be tested without a live Express app and SQLite database |
| HIGH | Module-level mutable state (`globalCache`, `totalRevenue`) shared across requests | Race conditions under concurrent load; cache entries from one request can leak into another |
| HIGH | 50-line business logic block inside the checkout route handler | Payment gateway call, conditional user creation, enrollment, payment, and audit log all inlined in a single route callback |
| MEDIUM | Callback hell — four nested SQLite callback levels in checkout | Inconsistent error handling between levels; enrollment can be committed with no corresponding payment on inner failures |
| MEDIUM | N+1 queries in financial report | 1 + C + C×E×2 queries for C courses × E enrollments; 2,011 queries with 10 courses and 100 enrollments each |
| MEDIUM | Silent account creation with default password `'123456'` | Checkout silently registers users who don't exist, without consent and with a guessable default credential |
| LOW | Credit card number and gateway key logged to stdout on every transaction | PCI-DSS violation; key and card data captured by any log aggregation tool |
| LOW | Magic string `cc.startsWith("4")` as payment approval logic | Undocumented Visa IIN prefix; all non-Visa cards are silently denied |
| LOW | Single-letter variable names (`u`, `e`, `p`, `cid`, `cc`) across 50 lines | High cognitive load; easy to confuse `e` (email) with `enr` (enrollment) |
| LOW | In-memory SQLite — all data lost on every restart | Seed user with password `'123'` is unconditionally recreated on each boot |

---

### Task Manager API — Python/Flask Task Manager

**[Full report](reports/audit-project-3.md)** · 12 files · ~700 lines · CRITICAL: 3 | HIGH: 3 | MEDIUM: 4 | LOW: 3 · **Total: 13**

| Severity | Finding | Why it matters |
|---|---|---|
| CRITICAL | Hardcoded `SECRET_KEY` in `app.py` | Flask signing key committed to source; forged session cookies or JWT tokens can impersonate any user |
| CRITICAL | Hardcoded SMTP credentials in `NotificationService` | Gmail account password (`senha123`) in source; any repo reader can send mail as the application and read incoming messages |
| CRITICAL | Password hash returned in every API response | `User.to_dict()` includes the `password` field; login and GET /users/<id> broadcast the MD5 hash to every caller |
| HIGH | MD5 password hashing with no salt | MD5 is not a key derivation function; rainbow tables and GPU rigs trivially reverse all common passwords in seconds |
| HIGH | Fake JWT token + no authorization middleware | Login returns `fake-jwt-token-<user_id>`; no route validates any token — all endpoints are publicly writable |
| HIGH | Business logic trapped in route handlers | Route handlers up to 89 lines contain validation, DB lookups, data transformation, and stats calculations |
| MEDIUM | N+1 queries in `GET /tasks` | Separate `User.query.get()` and `Category.query.get()` calls per task inside the list loop; 201 queries for 100 tasks |
| MEDIUM | N+1 queries in summary report | One `Task.query.filter_by(user_id=…).all()` per user inside a loop to build productivity statistics |
| MEDIUM | Overdue check logic duplicated in four locations | Identical three-level nested `if` block in `task_routes.py` (×3) and `user_routes.py`; `Task.is_overdue()` exists but is never called |
| MEDIUM | Deprecated SQLAlchemy `Query.get()` API | `Model.query.get(pk)` was deprecated in SQLAlchemy 2.0; used on every single-record lookup across three route files |
| LOW | `print()` as the sole logging mechanism | No log levels, no timestamps, no structured output; errors printed identically to informational messages |
| LOW | Bare `except:` clauses swallowing all exceptions | Catches `SystemExit` and `KeyboardInterrupt`; discards the original exception with no logging |
| LOW | Unused imports in `app.py` and `task_routes.py` | `os`, `sys`, `json`, `time` imported but never referenced in either file |

## Skill Construction

### Design decisions

The skill is split across six files inside `.claude/skills/refactor-arch/`. `SKILL.md` is the orchestrator — it defines the three-phase pipeline and tells the model exactly which reference file to load at each phase. The other five files are loaded on-demand, not all at once, to avoid exhausting the context window:

| File | Loaded in | Purpose |
|---|---|---|
| `project-analysis.md` | Phase 1 | Language/framework/DB detection heuristics and Phase 1 output format |
| `catalog-of-anti-patterns.md` | Phase 2 | Detection signals and severity for each anti-pattern |
| `report-template.md` | Phase 2 (writing) | Exact format every audit report must follow |
| `architecture-guidelines.md` | Phase 3 start | MVC layer responsibilities and target directory structure |
| `refactoring-playbook.md` | Phase 3 (each fix) | Before/after code transformations for every anti-pattern |

A deliberate **confirmation gate** sits between Phase 2 and Phase 3: the skill prints the finding summary and waits for explicit approval before rewriting any file. This prevents destructive changes from happening without review.

### Anti-pattern catalog

The catalog covers 15 anti-patterns across four severity levels. Selection criteria: each entry must be (1) detectable from source code alone, (2) linked to a concrete impact, and (3) paired with a specific fix in the playbook. The catalog deliberately includes both security issues (SQL Injection, hardcoded credentials, broken hashing) and architectural ones (God Class, N+1, business logic in routes) so that a single run catches both dimensions.

### Technology-agnostic design

Technology-agnosticism is enforced at three levels:

1. **Detection** — `project-analysis.md` maps file extensions, dependency files, and import patterns to language/framework pairs. The same heuristic table covers Python, Node.js, Ruby, Go, Java, and PHP.
2. **Architecture** — `architecture-guidelines.md` defines MVC layer rules in terms of *responsibilities* (what each layer may and may not do), not syntax. The same rules apply whether the stack is Flask, Express, Django, or Fastify.
3. **Playbook** — every transformation pattern in `refactoring-playbook.md` shows a Python version and a Node.js version side-by-side, so the model can adapt to whichever stack was detected in Phase 1.

### Challenges and solutions

| Challenge | Solution |
|---|---|
| Context bloat from loading all reference files upfront | Load-on-demand per phase; only the files relevant to the current step are read |
| Skill writing to the wrong directory | Phase 3 opens with an explicit check: all output goes to `projects-refactored/<name>/`, never `projects-original/` |
| Validation requiring a running server | Phase 3 creates a venv, installs dependencies, and uses `curl` / `Invoke-RestMethod` to hit every original endpoint and confirm non-500 responses |
| Deprecated framework APIs going undetected | `project-analysis.md` includes a dedicated deprecated-API table (Flask, SQLAlchemy, Express) that feeds into Phase 2 as `[LOW]` or `[MEDIUM]` findings |

## Results

[screenshots](screenshots)

## How to Execute

### Prerequisites

- [Claude Code](https://claude.ai/code) installed and authenticated (`claude --version` should work)
- Python 3.9+ available on PATH (for Python projects)
- Node.js 18+ available on PATH (for Node.js projects)
- The repository cloned locally

### Running the skill

Navigate to the **refactored output directory** for the target project, then invoke the skill:

```bash
# Project 1 — Python/Flask e-commerce
cd projects-refactored/code-smells-project
/refactor-arch

# Project 2 — Node.js/Express LMS
cd projects-refactored/ecommerce-api-legacy
/refactor-arch

# Project 3 — Python/Flask task manager
cd projects-refactored/task-manager-api
/refactor-arch
```

The skill reads source files from `projects-original/<project-name>/` and writes all output to the current directory (`projects-refactored/<project-name>/`).

### What happens at each phase

1. **Phase 1** — The skill prints a project analysis summary (language, framework, DB, architecture pattern). Review it for accuracy before continuing.
2. **Phase 2** — An audit report is saved to `reports/audit-project-<N>.md` and a finding summary is printed. The skill pauses and asks for confirmation.
3. **Phase 3** — After you type `y`, the skill refactors the project, creates a virtual environment, installs dependencies, starts the server, and runs endpoint checks with `curl` / `Invoke-RestMethod`.

### Validating the result

After Phase 3 completes, check the printed summary for:

```
✓ venv created and dependencies installed
✓ Application starts without errors
✓ All N original endpoints preserved
✓ Zero findings remaining
```