---
name: refactor-arch
description: >
  Audits any backend project for architectural problems, security vulnerabilities, and code smells,
  then refactors it to the MVC (Model-View-Controller) pattern. Use this skill whenever the user wants
  to analyze or audit a codebase, find SQL Injection, hardcoded credentials, or broken authentication,
  detect anti-patterns like God Classes, N+1 queries, or callback hell, map the current architecture,
  or reorganize a project (Python/Flask, Node.js/Express, or any other stack) to a clean layered structure.
  Trigger even when the user simply says "audit this project", "find the problems in this code",
  "refactor this to MVC", "analyze this legacy app", or "clean up this codebase" — this skill owns
  the full pipeline from analysis through refactoring and validation.
user-invocable: true
---

# Refactor to MVC

This skill runs a three-phase pipeline on a target project: analyze the stack and current structure, audit the code against a catalog of anti-patterns, then refactor everything to a clean MVC layout. It is technology-agnostic and applies the same phases regardless of language or framework.

The goal is not just to reorganize directories — it is to eliminate real security and architectural problems found in the audit, and leave the application in a state where it still works correctly after the changes.

---

## Reference Files — When to Load Each One

Load reference files only when you need them, not all at once. Loading everything upfront wastes context.

| Phase | Load this file | Why |
|---|---|---|
| Phase 1 start | `project-analysis.md` | Language/framework detection heuristics and Phase 1 output format |
| Phase 2 start | `catalog-of-anti-patterns.md` | Detection signals and severity for each anti-pattern |
| Phase 2 (writing report) | `report-template.md` | Exact format the report must follow |
| Phase 3 start | `architecture-guidelines.md` | MVC layer responsibilities and target directory structure |
| Phase 3 (each fix) | `refactoring-playbook.md` | Before/after code patterns for each anti-pattern being fixed |

All reference files live at `.claude/skills/refactor-arch/`.

---

## Phase 1 — Analysis

**Goal:** Understand the target project's stack and current architecture before touching anything.

**Steps:**

1. Read `project-analysis.md` to load detection heuristics.

2. Scan the target project's files:
   - Identify language from file extensions and imports.
   - Identify framework from `requirements.txt`, `package.json`, or import statements.
   - Identify database driver and ORM (or lack of one).
   - Count source files and estimate lines of code.
   - Identify what the application does (its domain: e-commerce, LMS, task manager, etc.).
   - Identify the current architectural pattern (monolith, partial MVC, God Class, etc.).

3. Print the Phase 1 summary using the format defined in `project-analysis.md`.

**What good output looks like:**
```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.x
Database:      SQLite (sqlite3 driver, no ORM)
Dependencies:  flask, flask-cors
Domain:        E-commerce API (products, users, orders)
Architecture:  Monolithic — all in 4 files, no separation of layers
Source files:  4 files analyzed | ~450 lines of code
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

**Before moving to Phase 2:** Confirm the summary is accurate. If something is ambiguous (e.g., framework version, table names), note it explicitly rather than guessing.

---

## Phase 2 — Audit

**Goal:** Find real problems in the code — not hypothetical ones. Every finding must cite the exact file and line where the problem lives.

**Steps:**

1. Read `catalog-of-anti-patterns.md` to load detection signals and severity levels.

2. Read every source file in the project. For each file, check it against the anti-pattern catalog:
   - Look for SQL string concatenation (SQL Injection).
   - Look for hardcoded secrets in source code.
   - Look for unauthenticated admin/dangerous endpoints.
   - Look for plaintext passwords or broken hashing.
   - Look for business logic in route handlers.
   - Look for nested loops that issue DB queries (N+1).
   - Look for duplicated validation or logic blocks.
   - Look for bare `except:` clauses, debug prints, magic numbers.
   - Check for deprecated framework APIs (per `project-analysis.md`).

3. Read `report-template.md` and write the audit report following its exact format:
   - Order findings CRITICAL → HIGH → MEDIUM → LOW.
   - Each finding: title, file+line, relevant code snippet, description, impact, recommendation.
   - Minimum: 1 CRITICAL or HIGH, 2 MEDIUM, 2 LOW, 5 total.

4. Save the report to `reports/audit-<project-folder-name>.md`.

5. Print the report summary to the terminal.

6. **STOP. Ask for confirmation before Phase 3:**
   > "Phase 2 complete — audit saved to reports/audit-<name>.md.
   > Found: CRITICAL: N | HIGH: N | MEDIUM: N | LOW: N
   > Shall I proceed with Phase 3 (refactoring)? [y/n]"

   Wait for the user's answer. If they say no, stop here and explain which findings they might want to address manually.

**Why the pause matters:** Phase 3 creates new files and restructures the project. The user should review what will change before it happens. The audit report is also useful on its own — don't assume they always want to refactor.

---

## Phase 3 — Refactoring

**Goal:** Reorganize the project to a clean MVC structure, fixing every finding from the audit. The application must still work after the refactoring.

**Output path:** Write all refactored files to `projects-refactored/<project-folder-name>/`. Never modify files in `projects-original/`.

**Steps:**

1. Read `architecture-guidelines.md` to load the target MVC structure and per-layer rules.

2. Plan the new directory structure before writing any file. Print the planned layout:
   ```
   projects-refactored/<name>/
   ├── config/settings.py
   ├── models/product_model.py
   ├── controllers/product_controller.py
   ├── routes/product_routes.py
   ├── middlewares/auth.py
   └── app.py
   ```

3. For each CRITICAL/HIGH finding, read `refactoring-playbook.md` and apply the matching transformation pattern:
   - SQL Injection → Pattern 1 (parameterized queries)
   - Hardcoded secrets → Pattern 2 (env vars + config module)
   - Weak/broken hashing → Pattern 3 (bcrypt)
   - Missing auth → Pattern 4 (auth middleware)
   - N+1 queries → Pattern 5 (JOINs or eager loading)
   - Business logic in routes → Pattern 6 (extract to controller)
   - Duplicated logic → Pattern 7 (deduplicate via model/helper)
   - Callback hell → Pattern 8 (async/await)
   - Dangerous admin endpoints → Pattern 9 (remove or secure)
   - Bare except / error scattering → Pattern 10 (centralized error handler)

4. Also fix MEDIUM and LOW findings during the refactoring:
   - Replace magic numbers with named constants.
   - Remove unused imports.
   - Extract duplicated validation to a shared helper.

5. Create a `.env.example` file listing all required environment variables (without values).

6. **Create a virtual environment and install dependencies** inside the refactored project directory:

   **Python projects:**
   ```bash
   cd projects-refactored/<name>
   python -m venv .venv

   # Activate — Windows
   .venv\Scripts\activate
   # Activate — macOS / Linux / Git Bash
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

   **Node.js projects:**
   ```bash
   cd projects-refactored/<name>
   npm install
   ```

   If the install fails, diagnose and fix `requirements.txt` / `package.json` before continuing — a failed install means the app cannot start and validation cannot proceed.

7. **Validate the result** using `curl` — not a browser (browsers can't send auth headers or JSON bodies):

   ```bash
   # Python: use the venv interpreter
   .venv/Scripts/python -c "import app"   # Windows
   .venv/bin/python -c "import app"       # macOS/Linux
   # Node.js:
   node -e "require('./app')"

   # Health check — always public
   curl http://localhost:5000/health

   # Login to get a token
   curl -X POST http://localhost:5000/login \
     -H "Content-Type: application/json" \
     -d '{"email":"...","senha":"..."}'

   # Protected endpoint — paste token from login
   curl http://localhost:5000/<protected-route> \
     -H "Authorization: Bearer <token>"
   ```

   Expected behavior during testing (these are correct, not errors):
   - `401` on a protected route without a token ✓ auth is working
   - `405` on `GET /login` ✓ login only accepts POST
   - `404` on `/favicon.ico` ✓ normal browser auto-request, ignore it

   Verify every original endpoint returns a non-500 response.
   Verify no finding from the audit report remains unresolved.

8. Print the Phase 3 summary:
   ```
   ================================
   PHASE 3: REFACTORING COMPLETE
   ================================
   Output: projects-refactored/<name>/

   ## New Project Structure
   [directory tree]

   ## Findings Resolved
   ✓ [CRITICAL] SQL Injection — parameterized queries applied
   ✓ [CRITICAL] Hardcoded SECRET_KEY — moved to config/settings.py + .env.example
   ✓ [HIGH] N+1 queries — replaced with JOIN query
   … (one line per finding)

   ## Validation
   ✓ venv created and dependencies installed
   ✓ Application starts without errors
   ✓ All N original endpoints preserved in routes/
   ✓ Zero findings remaining
   ================================
   ```

---

## Validation Checklists

Use these as self-checks before moving to the next phase — not as a post-hoc audit.

### Phase 1 checklist (check before printing summary)
- [ ] Language detected from actual file content, not just folder name
- [ ] Framework detected from import statements or dependency files
- [ ] Domain described in plain language (what the app does, not just its tech)
- [ ] Architecture pattern named and briefly explained

### Phase 2 checklist (check before asking for confirmation)
- [ ] Every finding cites a specific file and line range
- [ ] Every finding includes a 2–5 line code snippet (actual code, not pseudocode)
- [ ] Impact describes concrete harm (not "may cause issues")
- [ ] Recommendation names the specific fix (not "improve validation")
- [ ] Findings are sorted CRITICAL → HIGH → MEDIUM → LOW
- [ ] Deprecated API check was performed
- [ ] Report saved to `reports/audit-<project-name>.md`

### Phase 3 checklist (check before printing the summary)
- [ ] All files written to `projects-refactored/<name>/`, not `projects-original/`
- [ ] Config layer reads from environment variables — no hardcoded secrets
- [ ] All SQL uses parameterized queries — no string concatenation
- [ ] Passwords hashed with bcrypt or equivalent
- [ ] Auth middleware exists and is applied to protected routes
- [ ] Business logic is in controllers, not route handlers
- [ ] At least one model per domain entity
- [ ] `.env.example` created
- [ ] Virtual environment created (`.venv/` for Python, `node_modules/` for Node.js)
- [ ] `pip install -r requirements.txt` / `npm install` completed without errors
- [ ] Every finding from Phase 2 is resolved (cross-check the list)
- [ ] All original endpoints are reachable in the new routing layer
