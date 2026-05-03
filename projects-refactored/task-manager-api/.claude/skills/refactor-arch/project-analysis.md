# Project Analysis Heuristics

Heuristics for Phase 1: detect language, framework, database, and map the current architecture.

---

## Step 1 — Detect Language

| Signal | Language |
|---|---|
| Files ending in `.py` | Python |
| `package.json` present | Node.js / JavaScript |
| Files ending in `.rb` | Ruby |
| Files ending in `.java` | Java |
| Files ending in `.go` | Go |
| Files ending in `.ts` | TypeScript |
| `composer.json` present | PHP |

**How to confirm:** Read the first non-empty file in the project root and identify the syntax.

---

## Step 2 — Detect Framework

### Python
| Signal | Framework |
|---|---|
| `from flask import Flask` or `flask` in `requirements.txt` | Flask |
| `from django.db import models` or `django` in `requirements.txt` | Django |
| `from fastapi import FastAPI` or `fastapi` in `requirements.txt` | FastAPI |

### Node.js
| Signal | Framework |
|---|---|
| `require('express')` or `"express"` in `package.json` dependencies | Express |
| `require('fastify')` or `"fastify"` in `package.json` | Fastify |
| `require('koa')` or `"koa"` in `package.json` | Koa |
| `require('hapi')` | Hapi |

### Generic
| Signal | Framework |
|---|---|
| `app.get(`, `app.post(`, `router.` patterns | Express-style routing |
| `@app.route(`, `Blueprint(` | Flask-style routing |
| `@Controller(`, `@Get(`, `@Injectable(` | NestJS / Spring |

---

## Step 3 — Detect Database

| Signal | Database |
|---|---|
| `import sqlite3` / `require('sqlite3')` | SQLite |
| `sqlite:///` in connection string | SQLite (via ORM) |
| `psycopg2` / `pg` / `postgres://` | PostgreSQL |
| `mysql-connector` / `mysql2` / `mysql://` | MySQL |
| `mongoengine` / `pymongo` / `mongoose` / `mongodb://` | MongoDB |
| `from flask_sqlalchemy import SQLAlchemy` / `sequelize` | ORM abstraction (check dialect) |
| `:memory:` | In-memory SQLite (data lost on restart) |

---

## Step 4 — Map the Current Architecture

For each architecture type, identify which files play each role and what's wrong.

### Monolithic (Single File or 2–3 Files)
**Signals:**
- All routes, DB logic, and business rules in one file (e.g., `app.py`, `server.js`).
- A single `models.py` that contains queries, validation, and business calculations.
- No subdirectories; 1–4 files total.

**Example pattern:**
```
app.py          ← routes + business logic + DB calls
models.py       ← data access + business rules mixed
database.py     ← connection management
```

**MVC gaps:** No separation at all. Everything needs to be split.

---

### Partial MVC (Routes + Models, No Controllers)
**Signals:**
- `routes/` or `blueprints/` directory exists.
- `models/` directory exists with ORM classes.
- Route handlers contain business logic (>30 lines of logic per handler).
- No `controllers/` directory.

**Example pattern:**
```
app.py
models/
  user.py       ← ORM model, may include validation methods
routes/
  user_routes.py  ← handles HTTP + contains business logic + N+1 queries
```

**MVC gaps:** Controllers layer missing; business logic trapped in routes.

---

### God Class (All in One Class)
**Signals:**
- A class that has methods for `initDb()`, `setupRoutes()`, payment processing, and report generation.
- Class file > 150 lines with methods spanning unrelated domains.

**Example pattern:**
```
AppManager.js   ← DB init + route registration + business logic + payment
app.js          ← thin entry point
utils.js        ← config + crypto + cache mixed together
```

**MVC gaps:** Everything needs to be extracted. The class must be dissolved into proper layers.

---

### Files to Analyze for Each Project

1. **Entry point** (usually `app.py`, `app.js`, `server.js`, `index.js`, `main.py`):
   - Does it only start the app, or does it contain routes and logic?

2. **Route definitions** (look for `@app.route`, `app.get/post/put/delete`, `router.`, `Blueprint`):
   - Are routes in dedicated files, or scattered?
   - Are handlers thin (parse → delegate → respond) or fat (logic-heavy)?

3. **Data access** (look for `cursor.execute`, `db.query`, `Model.query`, `db.run`):
   - Is SQL parameterized or concatenated?
   - Are queries inside model functions, or scattered throughout routes/controllers?

4. **Configuration** (look for string literals in config, hardcoded ports, passwords):
   - Are secrets in source code or env vars?

5. **Authentication** (look for token checks, `@login_required`, `requireAuth` middleware):
   - Is auth applied consistently, or missing from some routes?

---

## Phase 1 Output Format

Print this summary before the Phase 2 audit:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <detected language>
Framework:     <detected framework + version if in requirements/package.json>
Database:      <detected DB + driver>
Dependencies:  <key packages from requirements.txt / package.json>
Domain:        <what the application does — e.g., "E-commerce API (products, users, orders)">
Architecture:  <current pattern — Monolithic / Partial MVC / God Class / etc.>
Source files:  <N files analyzed>
DB tables:     <list of tables if detectable from schema/models>
================================
```

---

## Deprecated API Detection

While reading source files, flag uses of:

### Python / Flask
| Deprecated | Since | Replacement |
|---|---|---|
| `@app.before_first_request` | Flask 2.3 | `with app.app_context(): …` in startup |
| `flask.signals.Namespace` | Flask 2.x | `blinker` directly |

### SQLAlchemy
| Deprecated | Since | Replacement |
|---|---|---|
| `Query.get(id)` | SQLAlchemy 2.0 | `db.session.get(Model, id)` |
| `Model.query.filter_by(…).first()` | SQLAlchemy 2.0 | `db.session.execute(select(Model).filter_by(…)).scalar_one_or_none()` |

### Node.js / Express
| Deprecated | Since | Replacement |
|---|---|---|
| `app.del(` | Express 4 | `app.delete(` |
| `req.param(name)` | Express 4 | `req.params.name` / `req.query.name` |
| Callback-style `sqlite3` | still works but async preferred | Promisify or use `better-sqlite3` |

Flag these as `[LOW]` findings in the audit report unless they cause active breakage (then `[MEDIUM]`).
