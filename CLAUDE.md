# audit-and-architectural-refactoring-skills

## Goal

Build and validate `/refactor-arch` — a **technology-agnostic** Claude Code skill that:
1. Detects the language, framework, and architecture of any backend project (Phase 1)
2. Audits the code against a catalog of anti-patterns and security issues (Phase 2)
3. Refactors it to a clean MVC structure, fixing every finding (Phase 3)

The skill must produce correct results regardless of stack. The three test projects deliberately cover different languages and levels of organization to validate this.

## Project Layout

```
projects-original/          ← Input projects with intentional problems — NEVER MODIFY
  code-smells-project/      ← Python/Flask — E-commerce API (flat monolith)
  ecommerce-api-legacy/     ← Node.js/Express — LMS API (God Class)
  task-manager-api/         ← Python/Flask — Task Manager (partial MVC, broken auth)

projects-refactored/        ← Refactored outputs go here
  code-smells-project/      ← ✅ Done
  ecommerce-api-legacy/     ← ⬜ Pending
  task-manager-api/         ← ⬜ Pending

reports/                    ← Phase 2 audit reports
  audit-project-1.md        ← ✅ code-smells-project
  audit-project-2.md        ← ⬜ ecommerce-api-legacy
  audit-project-3.md        ← ⬜ task-manager-api

README.md                   ← Manual Analysis section must be filled for all 3 projects

.claude/skills/refactor-arch/   ← The skill being built
  SKILL.md                      ← Main skill instructions (phases, validation)
  catalog-of-anti-patterns.md   ← Detection signals + severity (CRITICAL→LOW)
  architecture-guidelines.md    ← Target MVC layer rules + directory structure
  report-template.md            ← Exact audit report format
  refactoring-playbook.md       ← 10 before/after transformation patterns
  project-analysis.md           ← Language/framework/DB detection heuristics
```

## Running the Skill

```bash
cd projects-refactored/<project-name>
/refactor-arch
```

The skill reads from `projects-original/<project-name>` as its source, and writes refactored files into the current directory (`projects-refactored/<project-name>`).

## Hard Rules

- **Never modify files in `projects-original/`** — they are the read-only input
- Refactored code goes to `projects-refactored/<project-name>/`
- Audit reports go to `reports/audit-project-<N>.md`
- The Manual Analysis section of `README.md` must document findings for all 3 projects
- Minimum per project: 5 findings total, 1+ CRITICAL or HIGH, 2+ MEDIUM, 2+ LOW

## Technology-Agnostic Design

The skill's reference files cover detection and transformation patterns for:
- **Python** (Flask, Django, FastAPI, raw sqlite3, SQLAlchemy)
- **Node.js** (Express, Fastify, Koa, callback-style and async/await)
- **Generic** (language-neutral architecture rules, severity scale, report format)

When running the skill, the language and framework are detected automatically in Phase 1. The same MVC layer boundaries (Config → Model → Controller → Route → Middleware) apply to every stack — only the syntax and import mechanism differ.

## Severity Scale (from README.md)

- **CRITICAL**: Security failures, hardcoded credentials, SQL Injection, God Class
- **HIGH**: Strong MVC/SOLID violations, missing auth, weak hashing, global mutable state
- **MEDIUM**: N+1 queries, duplicated logic, callback hell, missing validation
- **LOW**: Magic numbers, debug prints, unused imports, bare `except:` clauses
