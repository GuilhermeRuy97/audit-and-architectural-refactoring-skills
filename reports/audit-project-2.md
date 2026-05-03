================================
ARCHITECTURE AUDIT REPORT
================================
Project:   ecommerce-api-legacy
Stack:     JavaScript (Node.js) + Express 4.18.2
Files:     3 analyzed | ~180 lines of code
================================

## Summary
CRITICAL: 2 | HIGH: 5 | MEDIUM: 3 | LOW: 4
Total findings: 14

## Findings

### [CRITICAL] Hardcoded Production Credentials in Source Code
File:           src/utils.js:1-7
Relevant code:
  const config = {
      dbUser: "admin_master",
      dbPass: "senha_super_secreta_prod_123",
      paymentGatewayKey: "pk_live_1234567890abcdef",
      smtpUser: "no-reply@fullcycle.com.br",
  };
Description:    Production database password, live payment gateway key, and SMTP
                user are hardcoded as string literals in a committed source file.
                Any developer with repository read access has all three credentials,
                and they are permanently in git history even if removed later.
Impact:         An attacker with repo access can drain the payment gateway account,
                read and delete all database records, and send email as the system.
Recommendation: Move every secret to environment variables. Create a `config/settings.js`
                that reads `process.env.DB_PASS`, `process.env.PAYMENT_GATEWAY_KEY`, etc.
                Add a `.env.example` listing the variable names (no values). Add `.env`
                to `.gitignore`.

---

### [CRITICAL] No Authentication or Authorization on Any Endpoint
File:           src/AppManager.js:80-137
Relevant code:
  app.get('/api/admin/financial-report', (req, res) => {
      // no token check, no role check — full revenue data returned to anyone
      this.db.all("SELECT * FROM courses", [], (err, courses) => { ...
  app.delete('/api/users/:id', (req, res) => {
      this.db.run("DELETE FROM users WHERE id = ?", [id], ...
Description:    None of the three registered routes (POST /api/checkout,
                GET /api/admin/financial-report, DELETE /api/users/:id)
                perform any authentication or authorization check. The admin
                financial report and the user-deletion endpoint are fully open
                to anonymous HTTP requests.
Impact:         Any unauthenticated caller can retrieve all course revenue and
                student data, or permanently delete any user record by supplying
                a numeric ID in the URL.
Recommendation: Implement a JWT-based auth middleware (middlewares/auth.js) that
                validates `Authorization: Bearer <token>` on every request. Apply
                it to all routes and add a role check (e.g., req.user.role ===
                'admin') before the financial-report and delete handlers.

---

### [HIGH] Broken / Weak Password Hashing (badCrypto)
File:           src/utils.js:17-23
Relevant code:
  function badCrypto(pwd) {
      let hash = "";
      for(let i = 0; i < 10000; i++) {
          hash += Buffer.from(pwd).toString('base64').substring(0, 2);
      }
      return hash.substring(0, 10);
Description:    The badCrypto function is not a cryptographic hash — it base64-
                encodes the password in a loop and truncates to 10 characters.
                The output space is tiny (10 printable chars), it has no salt, and
                identical passwords always produce identical output, enabling
                precomputed table attacks. The function name itself signals the
                developer knew this was unsafe.
Impact:         Any database leak immediately reveals every user's real password
                via a trivial reverse lookup. The 10-char truncation means many
                different passwords map to the same stored value.
Recommendation: Replace badCrypto with bcrypt: `const bcrypt = require('bcrypt');`
                `const hash = await bcrypt.hash(password, 12);` for storage and
                `await bcrypt.compare(plaintext, hash)` for verification.

---

### [HIGH] Plaintext Password in Seed Data
File:           src/AppManager.js:18
Relevant code:
  this.db.run("INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')");
Description:    The seed user is inserted with the plaintext password '123' stored
                directly in the pass column. The badCrypto function is not even
                applied here. This means the password is visible in plain text in
                any database dump or SELECT query against the users table.
Impact:         Anyone who gains read access to the database immediately has the
                seed user's password in cleartext, enabling direct impersonation
                without any cracking effort.
Recommendation: Hash seed passwords using bcrypt before insertion, or use a startup
                script that calls the user-creation service instead of raw SQL inserts.

---

### [HIGH] God Class — AppManager Handles All Application Concerns
File:           src/AppManager.js:1-141
Relevant code:
  class AppManager {
      initDb() { /* schema creation + seed data */ }
      setupRoutes(app) {
          app.post('/api/checkout', ...   /* payment + enrollment + audit */
          app.get('/api/admin/financial-report', ...
          app.delete('/api/users/:id', ...
Description:    AppManager combines database schema initialization, HTTP route
                registration, payment processing, enrollment creation, and audit
                logging into a single class. This violates the Single Responsibility
                Principle and every MVC layer boundary simultaneously.
Impact:         No part of the business logic can be unit-tested without spinning
                up an Express app and a live SQLite database. Any change to payment
                logic risks breaking route registration or DB initialization.
Recommendation: Dissolve AppManager into dedicated layers: config/database.js
                for DB init, models/ for data access, controllers/ for business
                logic, and routes/ for HTTP route registration.

---

### [HIGH] Global Mutable State Shared Across Requests
File:           src/utils.js:9-10
Relevant code:
  let globalCache = {};
  let totalRevenue = 0;
Description:    globalCache and totalRevenue are module-level mutable variables
                exported and shared across all requests. Under concurrent load, two
                requests can read and write these variables simultaneously with no
                locking, producing race conditions.
Impact:         Cache entries from one user's request can be read or overwritten by
                another user's concurrent request, leaking data between sessions.
                totalRevenue will silently accumulate incorrect values under
                concurrent writes.
Recommendation: Remove the module-level cache; compute revenue inline from the
                database query result. Remove globalCache or replace with a proper
                scoped solution that does not share state across requests.

---

### [HIGH] Business Logic Trapped in Route Handler (Checkout)
File:           src/AppManager.js:28-78
Relevant code:
  app.post('/api/checkout', (req, res) => {
      // payment gateway call
      // conditional user creation
      // enrollment insert
      // payment insert
      // audit log insert — all inside one route callback
Description:    The /api/checkout handler is 50 lines of non-HTTP logic: it calls
                the payment gateway, conditionally creates a user, creates an
                enrollment, records a payment, and writes an audit log — all inline
                in the route callback. This is business logic that belongs in a
                service or controller layer.
Impact:         The checkout flow cannot be unit-tested without an HTTP request and
                a live database. Any change to the business rule (e.g., changing
                payment provider) requires editing HTTP-layer code.
Recommendation: Extract to controllers/checkoutController.js with a processCheckout
                function that receives plain data objects and returns a result.
                The route handler should only parse the request, call the controller,
                and format the response.

---

### [MEDIUM] Callback Hell — Four Levels of Nested DB Callbacks
File:           src/AppManager.js:36-78
Relevant code:
  this.db.get("SELECT * FROM courses ...", (err, course) => {
      this.db.get("SELECT id FROM users ...", (err, user) => {
          let processPaymentAndEnroll = (userId) => {
              this.db.run("INSERT INTO enrollments ...", function(err) {
                  self.db.run("INSERT INTO payments ...", function(err) {
Description:    The checkout handler nests four levels of SQLite callbacks
                (course lookup -> user lookup -> enrollment insert -> payment insert ->
                audit log insert). Error handling is inconsistent — some inner
                callbacks call res.send without returning, meaning outer callbacks
                can still execute after a response is sent.
Impact:         Silent error propagation: if the payment insert fails but the
                enrollment insert succeeded, the enrollment is committed with no
                corresponding payment and the client may receive no error response.
Recommendation: Promisify the sqlite3 driver or switch to better-sqlite3 (synchronous
                API). Rewrite the checkout flow as async/await with a try/catch
                block. Each DB operation should be `await db.run(...)`.

---

### [MEDIUM] N+1 Query Problem in Financial Report
File:           src/AppManager.js:88-128
Relevant code:
  this.db.all("SELECT * FROM courses", [], (err, courses) => {
      courses.forEach(c => {
          this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (err, enrollments) => {
              enrollments.forEach(enr => {
                  this.db.get("SELECT name, email FROM users WHERE id = ?", [enr.user_id], ...
                  this.db.get("SELECT amount, status FROM payments WHERE enrollment_id = ?", [enr.id], ...
Description:    The financial report fetches all courses, then for each course fetches
                all enrollments, then for each enrollment issues 2 separate queries
                (user + payment). With C courses and E enrollments per course, this
                executes 1 + C + C*E*2 database queries.
Impact:         With 10 courses and 100 enrollments each, the endpoint issues 2,011
                DB queries per request. Response time grows O(C*E) and the endpoint
                becomes unusable at production data volumes.
Recommendation: Replace with a single JOIN query:
                SELECT c.title, u.name, p.amount, p.status
                FROM courses c
                LEFT JOIN enrollments e ON e.course_id = c.id
                LEFT JOIN users u ON u.id = e.user_id
                LEFT JOIN payments p ON p.enrollment_id = e.id
                Then aggregate the result in JavaScript.

---

### [MEDIUM] Silent Account Creation with Predictable Default Password
File:           src/AppManager.js:66-71
Relevant code:
  if (!user) {
      let hash = badCrypto(p || "123456");
      this.db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [u, e, hash], ...
Description:    The checkout flow silently creates a new user account if the email
                is not found in the database. If no password is provided in the
                request, the default "123456" is used. The user is never notified
                that an account was created on their behalf.
Impact:         GDPR/privacy violation — users may be unaware they have an account.
                An attacker who knows a victim's email can enroll them in a course
                and create an account for them. The default password "123456" is
                among the most commonly guessed credentials.
Recommendation: Require explicit account registration as a separate step. Remove the
                implicit account creation from the checkout flow. Require a password
                to be supplied explicitly and validated before use.

---

### [LOW] Sensitive Data Logged to Console in Production
File:           src/AppManager.js:45
Relevant code:
  console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
Description:    The checkout handler logs the raw credit card number and the live
                payment gateway API key to stdout on every transaction. In a server
                environment, stdout is typically shipped to log aggregation systems
                where it is retained and searchable.
Impact:         Payment card data and the gateway API key will appear in any log
                management tool (CloudWatch, Splunk, Datadog), violating PCI-DSS
                compliance and exposing the key to anyone with log read access.
Recommendation: Remove this console.log entirely. Never log card numbers, tokens,
                or credentials. Use a structured logger (e.g., winston) and log
                only non-sensitive identifiers (enrollment ID, user ID).

---

### [LOW] Magic Number — Undocumented Card-Type Detection
File:           src/AppManager.js:46
Relevant code:
  let status = cc.startsWith("4") ? "PAID" : "DENIED";
Description:    The payment approval logic is a single undocumented magic string:
                cards starting with "4" (Visa IIN range) are approved; all others
                are denied. This business rule is completely invisible from the
                code alone.
Impact:         Any developer changing this line without knowing the Visa IIN prefix
                convention will break payment processing. The rule also incorrectly
                denies all Mastercard, Amex, and other valid card types.
Recommendation: Replace with a named constant: `const VISA_PREFIX = '4';` with a
                comment explaining the IIN range. Better still, delegate card
                validation to the payment gateway's actual API.

---

### [LOW] Cryptic Single-Letter Variable Names
File:           src/AppManager.js:29-34
Relevant code:
  let u = req.body.usr;
  let e = req.body.eml;
  let p = req.body.pwd;
  let cid = req.body.c_id;
  let cc = req.body.card;
Description:    The checkout route handler uses single-character and abbreviated
                variable names (u, e, p, cid, cc) throughout 50 lines of logic.
                These names require the reader to memorize their meaning from the
                assignment lines and increase the risk of variable mix-ups.
Impact:         Increased cognitive load for every future developer; higher chance of
                confusing e (email) with enr (enrollment) or p (password) with
                payment, leading to incorrect logic changes.
Recommendation: Use descriptive names: userName, email, password, courseId, cardNumber.

---

### [LOW] In-Memory SQLite — All Data Lost on Restart
File:           src/AppManager.js:7
Relevant code:
  this.db = new sqlite3.Database(':memory:');
Description:    The application uses an in-memory SQLite database as its sole
                persistence layer. Every server restart destroys all data.
                The same seed data (including the plaintext-password user) is
                re-inserted unconditionally at every startup.
Impact:         No production data survives a restart or crash. The seed user with
                password '123' is always recreated, providing a known-credential
                entry point after every restart.
Recommendation: Replace ':memory:' with a file path read from an environment variable:
                process.env.DB_PATH || './data/app.db'. Run schema creation only
                if tables do not already exist (CREATE TABLE IF NOT EXISTS).

---

================================
Total: 14 findings
CRITICAL: 2 | HIGH: 5 | MEDIUM: 3 | LOW: 4
================================
