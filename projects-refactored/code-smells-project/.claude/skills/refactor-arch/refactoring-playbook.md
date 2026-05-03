# Refactoring Playbook

Concrete transformation patterns for each anti-pattern, with before/after code.
At least 8 patterns covered. All examples show both Python and Node.js where relevant.

---

## Pattern 1: Fix SQL Injection → Parameterized Queries

**Anti-pattern:** String concatenation builds SQL from user input.

**Before (Python):**
```python
cursor.execute(
    "SELECT * FROM users WHERE email = '" + email + "' AND password = '" + pwd + "'"
)
cursor.execute("SELECT * FROM products WHERE id = " + str(id))
cursor.execute(
    "INSERT INTO products (name, price) VALUES ('" + name + "', " + str(price) + ")"
)
```

**After (Python):**
```python
cursor.execute(
    "SELECT * FROM users WHERE email = ? AND password = ?",
    (email, hashed_pwd)
)
cursor.execute("SELECT * FROM products WHERE id = ?", (id,))
cursor.execute(
    "INSERT INTO products (name, price) VALUES (?, ?)",
    (name, price)
)
```

**Before (Node.js/sqlite3):**
```javascript
db.get("SELECT * FROM users WHERE email = '" + email + "'", callback);
```

**After (Node.js/sqlite3):**
```javascript
db.get("SELECT * FROM users WHERE email = ?", [email], callback);
```

**Rule:** Every value that comes from outside the application (HTTP request, env var, file) must go through a parameter placeholder (`?`, `$1`, `:name`), never concatenated into the query string.

---

## Pattern 2: Extract Secrets to Environment Variables

**Anti-pattern:** Secrets hardcoded in source files.

**Before:**
```python
# app.py
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```
```javascript
// utils.js
const config = {
  paymentGatewayKey: "pk_live_1234567890abcdef",
  dbPass: "senha_super_secreta_prod_123",
};
```

**After:**
```python
# config/settings.py
import os
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")
```
```javascript
// config/index.js
module.exports = {
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
  dbPass: process.env.DB_PASS,
  port: parseInt(process.env.PORT) || 3000,
};
// Fail fast if required secrets are missing
if (!module.exports.paymentGatewayKey) {
  throw new Error("PAYMENT_GATEWAY_KEY environment variable is required");
}
```
```
# .env (NOT committed to version control — add to .gitignore)
SECRET_KEY=generate-a-real-random-key-here
PAYMENT_GATEWAY_KEY=pk_live_…
DB_PASS=…
```

**Rule:** Any value that differs between environments (dev/staging/prod) or that would cause harm if leaked belongs in an environment variable, not source code.

---

## Pattern 3: Replace Weak Hashing with Proper Password Storage

**Anti-pattern:** MD5, SHA-1, or custom "crypto" for passwords.

**Before (Python — MD5, no salt):**
```python
import hashlib
def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()

def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()
```

**After (Python — bcrypt):**
```python
import bcrypt

def set_password(self, pwd: str) -> None:
    self.password = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_password(self, pwd: str) -> bool:
    return bcrypt.checkpw(pwd.encode(), self.password.encode())
```

**Before (Node.js — custom "badCrypto"):**
```javascript
function badCrypto(pwd) {
    let hash = "";
    for (let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString("base64").substring(0, 2);
    }
    return hash.substring(0, 10);
}
```

**After (Node.js — bcrypt):**
```javascript
const bcrypt = require("bcrypt");
const SALT_ROUNDS = 12;

async function hashPassword(pwd) {
    return bcrypt.hash(pwd, SALT_ROUNDS);
}

async function verifyPassword(pwd, hash) {
    return bcrypt.compare(pwd, hash);
}
```

**Rule:** Use bcrypt, argon2, or scrypt. Never MD5/SHA-1 for passwords. Always apply a per-user salt (bcrypt does this automatically).

---

## Pattern 4: Add Authentication Middleware

**Anti-pattern:** No auth check anywhere; every endpoint is publicly accessible.

**Before:**
```python
@bp.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks]), 200
```

**After (Python/Flask):**
```python
# middlewares/auth.py
from functools import wraps
from flask import request, jsonify, g
import jwt
from config.settings import SECRET_KEY

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            g.current_user_id = payload["sub"]
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

# routes/task_routes.py
@bp.route("/tasks", methods=["GET"])
@require_auth
def get_tasks():
    tasks = TaskController.get_all_tasks(user_id=g.current_user_id)
    return jsonify(tasks), 200
```

**After (Node.js/Express):**
```javascript
// middlewares/auth.js
const jwt = require("jsonwebtoken");
const { secretKey } = require("../config");

function requireAuth(req, res, next) {
    const token = (req.headers.authorization || "").replace("Bearer ", "");
    if (!token) return res.status(401).json({ error: "Authentication required" });
    try {
        req.user = jwt.verify(token, secretKey);
        next();
    } catch {
        res.status(401).json({ error: "Invalid token" });
    }
}
module.exports = { requireAuth };

// routes/taskRoutes.js
router.get("/tasks", requireAuth, async (req, res) => { … });
```

**Rule:** Auth is middleware, not something to remember in each handler. Apply it once at route registration time.

---

## Pattern 5: Eliminate N+1 Queries with JOINs or Eager Loading

**Anti-pattern:** A query per row inside a loop.

**Before (Python — 3 nested cursors):**
```python
def get_all_orders():
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    result = []
    for order in orders:
        cursor2.execute("SELECT * FROM order_items WHERE order_id = " + str(order["id"]))
        items = cursor2.fetchall()
        for item in items:
            cursor3.execute("SELECT name FROM products WHERE id = " + str(item["product_id"]))
            prod = cursor3.fetchone()
            …
    return result
```

**After (Python — single JOIN query):**
```python
def get_all_orders():
    cursor.execute("""
        SELECT o.id, o.status, o.total,
               oi.quantity, oi.unit_price,
               p.name AS product_name
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.id
        LEFT JOIN products p ON p.id = oi.product_id
        ORDER BY o.id
    """)
    rows = cursor.fetchall()
    orders = {}
    for row in rows:
        if row["id"] not in orders:
            orders[row["id"]] = {"id": row["id"], "status": row["status"], "items": []}
        if row["product_name"]:
            orders[row["id"]]["items"].append({
                "product": row["product_name"],
                "quantity": row["quantity"],
                "price": row["unit_price"],
            })
    return list(orders.values())
```

**After (SQLAlchemy ORM — eager loading):**
```python
from sqlalchemy.orm import joinedload

def get_all_orders():
    orders = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).all()
    return [o.to_dict() for o in orders]
```

**Rule:** If you see a loop that contains a query, replace it with a JOIN or eager load. Every such loop multiplies database round-trips.

---

## Pattern 6: Extract Business Logic from Routes into Controllers

**Anti-pattern:** Route handler contains pricing, workflow, or calculation logic.

**Before:**
```python
@app.route("/reports/sales", methods=["GET"])
def sales_report():
    cursor.execute("SELECT COUNT(*) FROM orders")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(total) FROM orders")
    revenue = cursor.fetchone()[0] or 0

    # Business logic in the route
    discount = 0
    if revenue > 10000:
        discount = revenue * 0.1
    elif revenue > 5000:
        discount = revenue * 0.05
    elif revenue > 1000:
        discount = revenue * 0.02

    return jsonify({"revenue": revenue, "discount": discount}), 200
```

**After:**
```python
# controllers/report_controller.py
DISCOUNT_TIERS = [
    (10000, 0.10),
    (5000,  0.05),
    (1000,  0.02),
]

def get_sales_report() -> dict:
    totals = OrderModel.get_totals()          # delegates DB to model
    revenue = totals["revenue"]
    discount = next(
        (revenue * rate for threshold, rate in DISCOUNT_TIERS if revenue > threshold),
        0
    )
    return {
        "total_orders": totals["count"],
        "revenue": round(revenue, 2),
        "discount": round(discount, 2),
        "net_revenue": round(revenue - discount, 2),
    }

# routes/report_routes.py
@bp.route("/reports/sales", methods=["GET"])
@require_auth
def sales_report():
    report = ReportController.get_sales_report()
    return jsonify(report), 200
```

**Rule:** The route's job is: parse → delegate → respond. Any `if revenue > X` belongs in a controller.

---

## Pattern 7: Deduplicate Logic with Shared Helpers or Model Methods

**Anti-pattern:** The same validation or calculation block copy-pasted in 4+ places.

**Before:**
```python
# Overdue check duplicated in task_routes.py, report_routes.py, user_routes.py …
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            task_data['overdue'] = True
        else:
            task_data['overdue'] = False
    else:
        task_data['overdue'] = False
else:
    task_data['overdue'] = False
```

**After — use the existing model method:**
```python
# models/task.py — already has is_overdue() — call it
def is_overdue(self) -> bool:
    return (
        self.due_date is not None
        and self.due_date < datetime.utcnow()
        and self.status not in ("done", "cancelled")
    )

# Everywhere that needed the block:
task_data['overdue'] = task.is_overdue()
```

**Rule:** If the same block appears 3+ times, extract it. If a model already has a method for it (like `is_overdue()`), call it instead of reimplementing it inline.

---

## Pattern 8: Flatten Callback Hell with async/await

**Anti-pattern:** Deeply nested callbacks in Node.js with no error propagation.

**Before:**
```javascript
app.post("/checkout", (req, res) => {
    db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
        if (err || !course) return res.status(404).send("Not found");
        db.get("SELECT id FROM users WHERE email = ?", [email], (err, user) => {
            if (err) return res.status(500).send("DB Error");
            db.run("INSERT INTO enrollments …", [userId, cid], function(err) {
                if (err) return res.status(500).send("Enrollment Error");
                db.run("INSERT INTO payments …", [this.lastID, amount], function(err) {
                    if (err) return res.status(500).send("Payment Error");
                    res.json({ success: true });
                });
            });
        });
    });
});
```

**After (Node.js — async/await with promisified DB):**
```javascript
// utils/db.js — promisify sqlite3
const { promisify } = require("util");
function promisifyDb(db) {
    return {
        get: promisify(db.get.bind(db)),
        run: (sql, params) => new Promise((resolve, reject) =>
            db.run(sql, params, function(err) { err ? reject(err) : resolve(this); })
        ),
        all: promisify(db.all.bind(db)),
    };
}

// controllers/checkoutController.js
async function checkout({ userId, courseId, amount }) {
    const course = await db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [courseId]);
    if (!course) throw new NotFoundError("Course not found");

    const { lastID: enrollId } = await db.run(
        "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
        [userId, courseId]
    );
    await db.run(
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
        [enrollId, amount, "PAID"]
    );
    return { enrollmentId: enrollId };
}

// routes/checkoutRoutes.js
router.post("/checkout", requireAuth, async (req, res) => {
    try {
        const result = await CheckoutController.checkout({
            userId: req.user.id,
            courseId: req.body.courseId,
            amount: req.body.amount,
        });
        res.status(200).json(result);
    } catch (e) {
        if (e instanceof NotFoundError) return res.status(404).json({ error: e.message });
        res.status(500).json({ error: "Internal error" });
    }
});
```

**Rule:** Flatten nested callbacks with `async/await`. Each level of nesting is a place where errors can silently escape.

---

## Pattern 9: Remove Dangerous Unauthenticated Admin Endpoints

**Anti-pattern:** `/admin/reset-db` or `/admin/query` with no auth.

**Before:**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    dados = request.get_json()
    query = dados.get("sql", "")
    cursor.execute(query)   # arbitrary SQL from HTTP body!
    …
```

**After — remove entirely or secure properly:**
```python
# Option A: Remove the endpoint entirely (preferred for arbitrary SQL exec)
# This feature should never exist in a production API.

# Option B: If a limited admin interface is genuinely needed, restrict severely:
@app.route("/admin/stats", methods=["GET"])
@require_auth
@require_role("admin")
def admin_stats():
    # Only pre-defined, parameterized queries — never arbitrary SQL
    stats = AdminModel.get_stats()
    return jsonify(stats), 200
```

**Rule:** Arbitrary SQL execution via HTTP must never exist in production. Any admin endpoint requires authentication AND role checks.

---

## Pattern 10: Centralized Error Handling

**Anti-pattern:** Each route has its own `try/except` with inconsistent error shapes. Bare `except:` clauses swallow errors silently.

**Before:**
```python
@bp.route("/tasks/<int:id>", methods=["GET"])
def get_task(id):
    try:
        task = Task.query.get(id)
        return jsonify(task.to_dict()), 200
    except:  # bare except — swallows AttributeError when task is None
        return jsonify({"error": "Erro interno"}), 500
```

**After (Python/Flask):**
```python
# middlewares/error_handler.py
class NotFoundError(Exception): pass
class ValidationError(Exception): pass
class AuthError(Exception): pass

def register_error_handlers(app):
    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify({"error": str(e)}), 404

    @app.errorhandler(ValidationError)
    def handle_validation(e):
        return jsonify({"error": str(e)}), 422

    @app.errorhandler(AuthError)
    def handle_auth(e):
        return jsonify({"error": str(e)}), 401

    @app.errorhandler(Exception)
    def handle_generic(e):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Internal server error"}), 500

# routes/task_routes.py — now thin:
@bp.route("/tasks/<int:task_id>", methods=["GET"])
@require_auth
def get_task(task_id):
    task = TaskController.get_task(task_id)   # raises NotFoundError if missing
    return jsonify(task), 200
```

**After (Node.js/Express):**
```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
    if (err.name === "NotFoundError") return res.status(404).json({ error: err.message });
    if (err.name === "ValidationError") return res.status(422).json({ error: err.message });
    if (err.name === "AuthError") return res.status(401).json({ error: err.message });
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
}
// Register last in app.js:
app.use(errorHandler);
```

**Rule:** Register error handlers once, centrally. Controllers and routes throw typed exceptions; middleware maps them to HTTP status codes. Bare `except:` is always wrong.
