# Architecture Guidelines — MVC Target Pattern

This document defines the target MVC architecture used by the `/refactor-arch` skill.
It is technology-agnostic: apply the same layer responsibilities whether the stack is Python/Flask, Node.js/Express, Ruby/Rails, or any other framework.

---

## Target Directory Structure

```
src/
├── config/
│   └── settings.py / config.js       ← All environment config, no hardcoded values
├── models/
│   ├── user_model.py / user.js        ← Data shape + DB access ONLY
│   └── …
├── controllers/
│   ├── user_controller.py / userController.js   ← Business logic, orchestration
│   └── …
├── routes/ (also called "views" in some frameworks)
│   ├── user_routes.py / userRoutes.js  ← HTTP wiring ONLY
│   └── …
├── services/                          ← Optional: cross-domain business logic
│   └── notification_service.py / …
├── middlewares/
│   └── auth.py / auth.js              ← Auth, logging, error handling
└── app.py / app.js                    ← Composition root, startup ONLY
```

Adapt names to the project's existing conventions (e.g., `blueprints/` instead of `routes/` in Flask). The layer boundaries matter more than directory names.

---

## Layer Responsibilities

### Config Layer (`config/`)

**What it does:**
- Reads environment variables (`.env`, `os.environ`, `process.env`).
- Provides a single config object/module imported by the rest of the app.
- Sets defaults for development; production values come from environment.

**Rules:**
- No hardcoded secrets, passwords, or API keys — ever.
- No application logic.
- Imported by other layers; imports nothing from the application.

**Example config pattern:**
```python
# Python
import os
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
```

```javascript
// Node.js
module.exports = {
  secretKey: process.env.SECRET_KEY || "dev-only-insecure-key",
  port: parseInt(process.env.PORT) || 3000,
  paymentKey: process.env.PAYMENT_GATEWAY_KEY,  // no default for production secrets
};
```

---

### Model Layer (`models/`)

**What it does:**
- Defines the data shape (ORM model class, schema, table structure).
- Contains ONLY data access: queries, inserts, updates, deletes.
- May include simple field-level validation (column constraints, type checks).
- May include serialization helpers (`to_dict()`, `toJSON()`).

**Rules:**
- No HTTP context (`request`, `req`, `res`).
- No business logic (discounts, workflow rules, notifications).
- No cross-model orchestration (a Product model should not know about Orders).
- All SQL uses parameterized queries — never string concatenation.
- Passwords hashed with a strong algorithm (bcrypt, argon2, scrypt) before storage.

**What does NOT belong here:**
- Discount calculations, pricing rules.
- Email/SMS notifications.
- Application-level validation (business rules).
- Any reference to `request` or HTTP status codes.

---

### Controller Layer (`controllers/`)

**What it does:**
- Orchestrates business logic: calls models, applies rules, coordinates between models.
- Contains the "what happens when" logic (create order → check stock → charge → enroll).
- Returns data (not HTTP responses) to the route layer.
- May call services for cross-cutting concerns (notifications, payments).

**Rules:**
- No direct HTTP parsing (`request.get_json()`, `req.body`) — receives already-parsed data from routes.
- No `jsonify()`, `res.json()`, `res.send()` — returns plain dicts/objects.
- No raw SQL — uses models.
- Business rules and validation logic live here, not in routes.

**Typical controller signature:**
```python
# Python
def create_order(user_id: int, items: list) -> dict:
    user = UserModel.get_by_id(user_id)
    if not user:
        raise NotFoundError("User not found")
    total = OrderModel.calculate_total(items)
    order = OrderModel.create(user_id=user_id, total=total)
    NotificationService.order_created(user, order)
    return order.to_dict()
```

```javascript
// Node.js
async function createOrder(userId, items) {
  const user = await UserModel.findById(userId);
  if (!user) throw new NotFoundError("User not found");
  const total = await OrderModel.calculateTotal(items);
  const order = await OrderModel.create({ userId, total });
  await NotificationService.orderCreated(user, order);
  return order.toJSON();
}
```

---

### Route / View Layer (`routes/`)

**What it does:**
- Wires HTTP paths to controller functions.
- Parses and validates HTTP input (body, params, query string).
- Calls the appropriate controller with parsed data.
- Translates controller output (or errors) to HTTP responses.
- Applies route-level middleware (auth guards, rate limits).

**Rules:**
- Must be thin — no business logic.
- Validates input format and presence; business validation stays in controller.
- Single responsibility: parse → delegate → respond.
- All protected routes apply authentication middleware.

**Typical route pattern:**
```python
# Python (Flask)
@bp.route("/orders", methods=["POST"])
@require_auth
def create_order_route():
    data = request.get_json()
    if not data or "items" not in data:
        return jsonify({"error": "items required"}), 400
    try:
        result = OrderController.create_order(
            user_id=g.current_user.id,
            items=data["items"]
        )
        return jsonify(result), 201
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except BusinessError as e:
        return jsonify({"error": str(e)}), 422
```

```javascript
// Node.js (Express)
router.post("/orders", requireAuth, async (req, res) => {
  const { items } = req.body;
  if (!items) return res.status(400).json({ error: "items required" });
  try {
    const result = await OrderController.createOrder(req.user.id, items);
    res.status(201).json(result);
  } catch (e) {
    if (e instanceof NotFoundError) return res.status(404).json({ error: e.message });
    res.status(422).json({ error: e.message });
  }
});
```

---

### Service Layer (`services/`) — Optional

**When to add it:**
- When business logic needs to coordinate across multiple controllers (e.g., NotificationService used by both OrderController and UserController).
- When integrating external systems (payment gateways, email providers, storage).
- When a concern (audit logging, caching) is cross-cutting.

**Rules:**
- No HTTP context.
- No model-level SQL (delegates to models).
- Stateless where possible; if stateful, use dependency injection.

---

### Middleware Layer (`middlewares/`)

**What it does:**
- `auth.py / auth.js` — Validates tokens, sets `g.current_user` / `req.user`.
- `error_handler.py / errorHandler.js` — Centralized exception-to-HTTP mapping.
- `logging.py / logger.js` — Structured request/response logging.

**Rules:**
- Must be composable and stateless.
- Auth middleware always runs before route handlers on protected routes.
- Error handler always registered last (in Express: after all routes).

---

### Composition Root (`app.py / app.js`)

**What it does:**
- Creates the app instance.
- Loads config.
- Registers middleware.
- Registers route blueprints / routers.
- Starts the server.

**Rules:**
- No business logic.
- No inline route handlers.
- No direct DB queries.
- Readable as a "table of contents" for the application.

---

## Cross-Layer Rules (All Technologies)

| Rule | Why |
|---|---|
| No HTTP objects below the Route layer | Controllers and Models must be testable without an HTTP server |
| No raw SQL in Controllers or Routes | Models own persistence; SQL in controllers tightly couples business and storage layers |
| No secrets or magic values outside Config | Hard to rotate credentials; production values differ from dev |
| Auth checked before any route handler body | Forgetting auth on a new route is a common vulnerability; middleware prevents this |
| Parameterized queries everywhere | String concatenation is SQL Injection by definition |
| Passwords hashed with adaptive algorithm | MD5/SHA1 are trivially brute-forced; bcrypt/argon2 are designed for this |
| Errors propagate as exceptions, not return values | Mixed error/result returns lead to callers forgetting to check |

---

## What "MVC-compliant" Looks Like for Each Project

### Python / Flask
- Models: SQLAlchemy ORM classes in `models/`, using `db.session` — no raw SQL.
- Controllers: Pure Python functions in `controllers/` — no `request`/`jsonify`.
- Routes: Flask Blueprints in `routes/` — thin handlers applying `@require_auth`.
- Config: `config/settings.py` reading from `os.environ`.

### Node.js / Express
- Models: Module functions or classes in `models/` — parameterized queries via `?` or `$1` placeholders.
- Controllers: Async functions in `controllers/` — no `req`/`res`.
- Routes: Express Routers in `routes/` — thin handlers with `async/await` and `try/catch`.
- Config: `config/index.js` reading from `process.env`.

### General (any stack)
The same layer boundaries apply. The names and import mechanisms differ; the responsibilities do not.
