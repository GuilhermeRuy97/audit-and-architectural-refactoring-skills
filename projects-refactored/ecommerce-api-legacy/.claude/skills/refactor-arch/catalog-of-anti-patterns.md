# Catalog of Anti-Patterns

Each entry includes: detection signals, severity, and the primary impact.
Severity levels: CRITICAL > HIGH > MEDIUM > LOW (per definitions in README.md)

---

## CRITICAL

### SQL Injection
**Detection signals:**
- String concatenation of user input into SQL: `"SELECT … WHERE id = " + str(id)`, `f"WHERE email = '{email}'"`, `"VALUES ('" + name + "')"`.
- Template literals or f-strings building queries with variables: `` `SELECT * FROM users WHERE id = ${req.params.id}` ``
- `.execute()`, `.query()`, `.run()` receiving a string assembled from request data.
- Absence of parameterized queries / prepared statements.

**Severity:** CRITICAL
**Impact:** Attackers can bypass authentication, exfiltrate all data, or destroy the database with a crafted input.

---

### Hardcoded Credentials in Source Code
**Detection signals:**
- String literals containing passwords, tokens, or keys assigned to variables or config: `SECRET_KEY = "abc123"`, `"pk_live_…"`, `"smtp_password": "pass"`.
- Credentials visible in committed files (`.py`, `.js`, `.env` checked into VCS).
- `config` objects in source files containing `dbPass`, `apiKey`, `paymentGatewayKey`.

**Severity:** CRITICAL
**Impact:** Anyone with repository access has production credentials; secrets live permanently in git history.

---

### Unauthenticated Administrative / Dangerous Endpoints
**Detection signals:**
- Routes with names like `/admin/`, `/reset-db`, `/query`, `/exec`, `/debug` that have no auth check before executing.
- Endpoint accepts arbitrary SQL, shell commands, or destructive operations from HTTP body.
- No middleware or guard checking a session/token before reaching sensitive logic.

**Severity:** CRITICAL
**Impact:** Remote code execution, full database wipe or exfiltration, accessible from the internet.

---

### Sensitive Data Exposed in API Responses
**Detection signals:**
- Serialization methods (`.to_dict()`, `JSON.stringify`) that include `password`, `secret_key`, `token`, `api_key` fields.
- Health check, debug, or metadata endpoints returning config values or internal paths.
- User list endpoints returning plaintext or hashed passwords in the response body.

**Severity:** CRITICAL
**Impact:** Credential leakage through normal API calls; password hashes enable offline cracking.

---

## HIGH

### Plaintext Password Storage
**Detection signals:**
- User record stored with `senha = senha`, `pass = req.body.pwd` (no hash call).
- No `hashlib`, `bcrypt`, `argon2`, `scrypt`, or equivalent import near password write path.
- Password comparison done with `==` against the stored value directly.

**Severity:** HIGH (escalates to CRITICAL if combined with exposed endpoints)
**Impact:** Any database leak immediately reveals every user's real password.

---

### Broken / Weak Password Hashing
**Detection signals:**
- Use of MD5 or SHA-1 for passwords: `hashlib.md5(pwd.encode()).hexdigest()`.
- Homemade "crypto": base64 loops, XOR, rot13, character substitution.
- No salt applied: identical passwords produce identical hashes.
- Function explicitly named `badCrypto`, `weakHash`, etc. — the developer knows.

**Severity:** HIGH
**Impact:** Rainbow tables and GPU cracking trivially reverse MD5/SHA-1 hashes; saltless hashes allow precomputation.

---

### God Class / God File
**Detection signals:**
- A single class or file that: initializes the database, registers HTTP routes, implements business logic, and handles responses — all together.
- Class with more than ~5 unrelated public methods spanning different domains (auth + payment + reporting + routing).
- Single file > 300 lines containing multiple domain concerns.

**Severity:** HIGH
**Impact:** Impossible to test any part in isolation; any change in one domain risks breaking unrelated features.

---

### Business Logic Trapped in Controllers / Routes
**Detection signals:**
- Route handler functions longer than ~40 lines containing non-HTTP logic (calculations, loops over DB results, discount formulas, state machines).
- Pricing, discount, or workflow decisions made inside `@app.route` or `app.get(…)` callbacks.
- Route handler calling multiple model functions in sequence and combining their results with if/else branches.

**Severity:** HIGH
**Impact:** Logic cannot be reused, unit-tested, or changed without modifying HTTP-layer code.

---

### Fake / Missing Authentication Token
**Detection signals:**
- Login endpoint returns a predictable string: `"token": "fake-jwt-token-" + str(user_id)`, `"token": "abc123"`.
- No middleware anywhere validates a token on protected routes.
- Token format is guessable from user data alone (e.g., `"admin-" + email`).

**Severity:** HIGH
**Impact:** Any client can forge tokens and impersonate any user; authentication is cosmetic.

---

### Global Mutable State
**Detection signals:**
- Module-level `let globalCache = {}`, `db_connection = None`, `total = 0` used across requests.
- Singleton connection objects with `check_same_thread=False` and no locking.
- Exported mutable objects shared across the entire application without synchronization.

**Severity:** HIGH
**Impact:** Race conditions under concurrent requests; one request can corrupt state visible to all others.

---

### Missing Authorization on All Endpoints
**Detection signals:**
- No `@login_required`, middleware, or token check on any route.
- Admin and user endpoints treated identically — no role check.
- Deleting or updating resources without verifying the requester owns them.

**Severity:** HIGH
**Impact:** Any anonymous user can read, write, or delete any data.

---

## MEDIUM

### N+1 Query Problem
**Detection signals:**
- A loop over a query result that issues another query per row: `for row in cursor.fetchall(): cursor2.execute(…)`.
- ORM usage: `for task in Task.query.all(): user = User.query.get(task.user_id)`.
- Three or more nested cursor objects or nested callback DB calls in the same function.
- Financial or report endpoints that issue one query per entity to build aggregates.

**Severity:** MEDIUM
**Impact:** Response time grows O(N) or O(N×M) with data volume; endpoint becomes unusable at scale.

---

### Logic / Validation Duplication
**Detection signals:**
- Same validation block (field checks, regex, range checks) copy-pasted between create and update handlers.
- Status-list or enum values defined as string literals in multiple places: `["pending", "approved", "cancelled"]` in 3 files.
- `process_task_data()` or similar helper defined but never called — routes duplicate its logic inline.

**Severity:** MEDIUM
**Impact:** Changing a rule requires finding and updating every copy; inconsistencies cause subtle bugs.

---

### Callback Hell / Pyramid of Doom
**Detection signals:**
- Deeply nested anonymous functions: 4+ levels of indentation in a single callback chain.
- Error handling absent or inconsistent across nesting levels (early `return res.send(…)` in inner callbacks, outer callback never notified).
- Async operations that could use `Promise`, `async/await`, or equivalent chained instead as nested callbacks.

**Severity:** MEDIUM
**Impact:** Silent failures propagate undetected; code is untestable and very hard to reason about.

---

### Silent Account Creation / Consent Violation
**Detection signals:**
- Checkout or action flow creates a user record if one doesn't exist, without notifying the user.
- Default password hard-coded during implicit registration: `"123456"`, `"changeme"`.
- No email confirmation or acknowledgment step before persisting user credentials.

**Severity:** MEDIUM
**Impact:** GDPR/privacy violation; users may be unaware they have an account; default password is predictable.

---

### Business Logic in Model Layer
**Detection signals:**
- Model function performs discount/pricing calculations, workflow decisions, or notification logic alongside DB queries.
- Magic numbers embedded in model: `if revenue > 10000: discount = 0.1`.
- Model method returns formatted business reports rather than raw data.

**Severity:** MEDIUM
**Impact:** Business rules cannot be tested without a database; changing policy requires editing data-access code.

---

### Missing Input Validation on Routes
**Detection signals:**
- Route reads `req.body.field` or `request.get_json().get(…)` and passes it directly to DB without type or range check.
- No email format validation, no numeric range check, no enum membership check.
- Only non-null check: `if not field: return 400`.

**Severity:** MEDIUM
**Impact:** Invalid data corrupts the database; type errors cause uncaught exceptions that leak stack traces.

---

## LOW

### Debug / Print Logging in Production
**Detection signals:**
- `print(…)` used as the sole logging mechanism throughout handlers.
- Comments or fake side-effects: `print("ENVIANDO EMAIL: …")` where no actual email is sent.
- `DEBUG = True` or `app.run(debug=True)` in production configuration.
- Environment hardcoded as `"ambiente": "producao"` while `DEBUG` is `True`.

**Severity:** LOW
**Impact:** No structured logs for monitoring or alerting; fake integrations give false confidence.

---

### Magic Numbers / Magic Strings
**Detection signals:**
- Threshold values appear without named constants: `if revenue > 10000`, `if preco > 1000`.
- Discount rates inline: `0.1`, `0.05`, `0.02`.
- Enum values repeated as literals: `["pending", "approved", "cancelled"]` defined in 4 different files.
- Status strings like `"admin"`, `"cliente"`, `"producao"` scattered throughout code.

**Severity:** LOW
**Impact:** Intent of values is unclear; changing a threshold requires finding every occurrence.

---

### Unused Imports
**Detection signals:**
- `import os, sys, json, time` at the top of a file where none of these are referenced in the body.
- ORM or framework imports that are never called.
- Helper modules imported but their functions are duplicated inline instead of called.

**Severity:** LOW
**Impact:** Inflated dependency surface; suggests copy-paste origin; may cause import-time side effects.

---

### Bare `except` Clauses
**Detection signals:**
- `except:` with no exception type specified.
- `except Exception as e: pass` or `except: return jsonify({"error": "erro interno"})` with no logging.
- `try/except` blocks that swallow the original error, making debugging impossible.

**Severity:** LOW
**Impact:** All exception types caught silently; program continues in unknown state; root causes invisible.

---

### Inconsistent / Cryptic Variable Names
**Detection signals:**
- Single-character variable names for non-loop variables: `u`, `e`, `p`, `cid`, `cc` used across 50 lines.
- Abbreviations that require domain knowledge: `enrId`, `csPending`, `enrPending`.
- Local variable shadows a built-in: `id = …`, `list = …`, `type = …`.

**Severity:** LOW
**Impact:** Readability — any future developer must memorize the mapping; increases cognitive load and bug risk.

---

### In-Memory / Ephemeral Database in Production Path
**Detection signals:**
- SQLite `:memory:` database used in the main application entry point (not just tests).
- Database file path hardcoded without environment-variable override.
- Seed data inserted unconditionally at startup alongside schema creation.

**Severity:** LOW (escalates to HIGH if this is the only persistence layer)
**Impact:** All data lost on restart; known seed data always present (default users/passwords).
