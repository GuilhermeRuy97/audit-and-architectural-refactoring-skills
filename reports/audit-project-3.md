================================
ARCHITECTURE AUDIT REPORT
================================
Project:   task-manager-api
Stack:     Python + Flask 3.0.0 + SQLAlchemy 2.x (flask-sqlalchemy 3.1.1)
Files:     12 analyzed | ~700 lines of code
================================

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 4 | LOW: 3
Total findings: 13

## Findings

### [CRITICAL] Hardcoded Flask SECRET_KEY in Source Code
File:           app.py:13
Relevant code:
  app.config['SECRET_KEY'] = 'super-secret-key-123'
Description:    The Flask SECRET_KEY is hardcoded directly in version-controlled source
                code. This key is used to sign sessions and any future JWT tokens.
Impact:         Any developer or attacker with repository access can use the known key
                to forge session cookies or signed tokens and impersonate any user,
                including admins. The secret also lives permanently in git history
                even after a future fix.
Recommendation: Remove from source. Load from environment: SECRET_KEY = os.environ['SECRET_KEY'].
                Add SECRET_KEY to .env.example with an empty value and document that
                operators must generate a random 32-byte hex string.

---

### [CRITICAL] Hardcoded SMTP Credentials in Notification Service
File:           services/notification_service.py:8-10
Relevant code:
  self.email_user = 'taskmanager@gmail.com'
  self.email_password = 'senha123'
Description:    The Gmail account username and plaintext password are hardcoded in the
                class constructor. These credentials are committed to version control
                and visible to any repository reader.
Impact:         An attacker with read access to the repo can log into the Gmail account,
                send phishing emails from the application's address, and read all
                incoming mail (e.g., password reset links sent to users).
Recommendation: Move to environment variables: email_user = os.environ['SMTP_USER']
                and email_password = os.environ['SMTP_PASSWORD']. Add both keys to
                .env.example.

---

### [CRITICAL] Password Hash Returned in API Responses
File:           models/user.py:16-25 and routes/user_routes.py:207-211
Relevant code:
  # models/user.py:22
  'password': self.password,

  # routes/user_routes.py:209 (login response)
  'user': user.to_dict(),
Description:    The User.to_dict() serialization method includes the 'password' field.
                This object is returned verbatim in the login response body and in
                GET /users/<id>. Every caller receives the stored MD5 hash.
Impact:         Password hashes are broadcast to every client that calls /login or
                fetches a user profile. An attacker can collect hashes through normal
                API calls and crack them offline with GPU-based MD5 reversal (billions
                of MD5 hashes per second on consumer hardware).
Recommendation: Remove 'password' from to_dict(). Create a separate safe_dict() method
                that excludes sensitive fields, and use it everywhere in route responses.

---

### [HIGH] Broken/Weak Password Hashing (MD5, No Salt)
File:           models/user.py:27-32
Relevant code:
  def set_password(self, pwd):
      self.password = hashlib.md5(pwd.encode()).hexdigest()

  def check_password(self, pwd):
      return self.password == hashlib.md5(pwd.encode()).hexdigest()
Description:    Passwords are hashed with MD5, a fast general-purpose hash with no
                salt. MD5 is not a key derivation function; it was never designed for
                password storage. Identical passwords produce identical hashes.
Impact:         A leaked database combined with any rainbow table (freely available
                online) immediately reveals all common passwords. GPU rigs can evaluate
                billions of MD5 hashes per second, making brute-force of short passwords
                (e.g., '1234' from seed.py) trivial in milliseconds.
Recommendation: Replace with bcrypt: pip install flask-bcrypt. Use
                bcrypt.generate_password_hash(pwd, rounds=12) to store and
                bcrypt.check_password_hash(stored, pwd) to verify. No manual salt
                management needed.

---

### [HIGH] Fake Authentication Token and No Authorization Middleware
File:           routes/user_routes.py:207-211
Relevant code:
  return jsonify({
      'message': 'Login realizado com sucesso',
      'user': user.to_dict(),
      'token': 'fake-jwt-token-' + str(user.id)
  }), 200
Description:    The login endpoint returns a predictable string instead of a real JWT.
                The token encodes the user ID in plaintext ('fake-jwt-token-3'). No
                middleware anywhere in the codebase validates any token before allowing
                access to any route. All task, user, category, and report endpoints are
                completely unauthenticated.
Impact:         Any unauthenticated caller can read all users (including their password
                hashes), modify or delete any task, and access full productivity reports.
                An attacker can also trivially impersonate any user by guessing their ID
                (e.g., sending 'fake-jwt-token-1' as admin).
Recommendation: Use PyJWT (pip install pyjwt) to generate a real signed token on login.
                Create an auth middleware (middlewares/auth.py) that verifies the
                Authorization: Bearer <token> header on every protected route using
                @functools.wraps and a before_request hook or Blueprint decorator.

---

### [HIGH] Business Logic Trapped in Route Handlers
File:           routes/task_routes.py:85-154 and routes/report_routes.py:13-101
Relevant code:
  @task_bp.route('/tasks', methods=['POST'])
  def create_task():          # 70-line handler: parse, validate,
      ...                     # user lookup, category lookup, date parse,
      ...                     # tag normalization, commit, error handling
Description:    Route handlers contain all validation logic, relational lookups, data
                transformation, statistics computation, and persistence. The POST /tasks
                handler is 70 lines; the GET /reports/summary handler is 89 lines. There
                is no controller layer to house this logic.
Impact:         Business logic cannot be unit-tested without spinning up an HTTP context.
                Validation rules are duplicated between create and update handlers.
                Changing any business rule (e.g., allowed statuses) requires editing
                HTTP-layer files.
Recommendation: Create a controllers/ layer (e.g., controllers/task_controller.py).
                Route handlers should only parse the request, call the controller, and
                return the response (3-5 lines each). Controllers own validation,
                lookups, and persistence calls.

---

### [MEDIUM] N+1 Query Problem in GET /tasks
File:           routes/task_routes.py:41-57
Relevant code:
  for t in tasks:
      if t.user_id:
          user = User.query.get(t.user_id)   # +1 query per task
      if t.category_id:
          cat = Category.query.get(t.category_id)  # +1 query per task
Description:    After fetching all tasks in a single query, the handler issues two
                additional ORM queries per task — one to resolve the user name and one
                to resolve the category name. For N tasks, the endpoint executes 1 + 2N
                database round trips.
Impact:         With 100 tasks, the endpoint executes 201 queries. Response time grows
                linearly with data volume; the endpoint becomes unusable at scale and
                can exhaust connection pool resources under concurrent load.
Recommendation: Use SQLAlchemy eager loading: Task.query.options(
                joinedload(Task.user), joinedload(Task.category)).all(). The ORM will
                generate a single JOIN query that fetches all related data at once.

---

### [MEDIUM] N+1 Query in Summary Report per User
File:           routes/report_routes.py:53-68
Relevant code:
  users = User.query.all()
  for u in users:
      user_tasks = Task.query.filter_by(user_id=u.id).all()
Description:    The summary report fetches all users then issues one Task.query per user
                inside the loop to compute per-user productivity statistics.
Impact:         With M users, the endpoint executes 1 + M queries. A system with 50
                users runs 51 queries on every report request, blocking the DB
                connection for the full duration.
Recommendation: Replace the per-user query loop with a single aggregated query using
                SQLAlchemy's func.count() and group_by(Task.user_id), or use a SQL
                subquery that counts tasks per user in one pass.

---

### [MEDIUM] Overdue Calculation Logic Duplicated in Four Places
File:           routes/task_routes.py:30-39, 71-80, 283-287 and routes/user_routes.py:172-180
Relevant code:
  if t.due_date:
      if t.due_date < datetime.utcnow():
          if t.status != 'done' and t.status != 'cancelled':
              task_data['overdue'] = True
Description:    The same three-level nested overdue check is copy-pasted in four route
                handlers. The Task model already defines an is_overdue() method
                (models/task.py:50-60) that implements the same logic, but it is never
                called from any route. Similarly, utils/helpers.py defines validate_email()
                and process_task_data() that are never imported or used; routes duplicate
                their logic inline.
Impact:         Any change to the overdue rule (e.g., adding a grace period) must be
                applied in four separate locations. Inconsistencies between copies cause
                subtle bugs where the same task appears overdue in one endpoint and not
                in another.
Recommendation: Call Task.is_overdue() in all route handlers. Import and use
                validate_email() from utils/helpers.py in user routes. Remove the
                inline duplicates.

---

### [MEDIUM] Deprecated SQLAlchemy Query.get() API
File:           routes/user_routes.py:29, routes/task_routes.py:67, routes/report_routes.py:105
Relevant code:
  user = User.query.get(user_id)
  task = Task.query.get(task_id)
  cat = Category.query.get(cat_id)
Description:    Model.query.get(pk) is the SQLAlchemy 1.x identity-map lookup API.
                It was deprecated in SQLAlchemy 2.0. flask-sqlalchemy 3.1.1 targets
                SQLAlchemy 2.x and emits DeprecationWarning at runtime for each call.
Impact:         This pattern will be removed in a future SQLAlchemy release; using it
                now locks the project to legacy behavior and generates noise in logs that
                masks real warnings.
Recommendation: Replace all occurrences with db.session.get(Model, pk). For example:
                user = db.session.get(User, user_id). This is the SQLAlchemy 2.0+
                canonical lookup.

---

### [LOW] Debug print() Statements Used as Logging
File:           routes/task_routes.py:149, 153, 219, 233 and routes/user_routes.py:83, 89, 148
Relevant code:
  print(f"Task criada: {task.id} - {task.title}")
  print(f"ERRO: {str(e)}")
  print(f"Usuário deletado: {user_id}")
Description:    print() is used throughout route handlers as the sole observability
                mechanism. There is no structured logger, no log levels, no timestamps
                in a machine-parseable format, and no way to suppress debug output in
                production without code changes.
Impact:         In production, all output is mixed in stdout with no severity signal.
                Errors like "ERRO: ..." appear at the same level as informational
                messages. Monitoring systems cannot filter, alert on, or aggregate
                these lines.
Recommendation: Replace with Python's logging module: import logging; logger =
                logging.getLogger(__name__). Use logger.info(), logger.error(), and
                logger.exception() (the last preserves the stack trace on errors).

---

### [LOW] Bare except: Clauses Swallowing All Exceptions
File:           routes/user_routes.py:130-132, routes/task_routes.py:62-63, 137-138
Relevant code:
  except:
      db.session.rollback()
      return jsonify({'error': 'Erro ao atualizar'}), 500
Description:    Multiple try/except blocks use a bare except: with no exception type.
                This catches every exception including SystemExit, KeyboardInterrupt,
                and GeneratorExit — which should never be silenced. The caught exception
                is rolled back and discarded with no logging.
Impact:         A keyboard interrupt during a request will be swallowed and returned as
                a 500 error. Root causes of real failures are invisible because the
                exception is discarded, making debugging impossible without a debugger
                attached.
Recommendation: Replace with except Exception as e: and add logger.exception(e) before
                returning the 500 response. This preserves the stack trace in logs while
                still catching all application-level errors.

---

### [LOW] Unused Imports in Multiple Files
File:           app.py:7 and routes/task_routes.py:7
Relevant code:
  # app.py:7
  import os, sys, json, datetime   # os, sys, json never used in this file

  # routes/task_routes.py:7
  import json, os, sys, time       # all four unused
Description:    Both files import several standard-library modules that are never
                referenced in the file body. app.py imports os, sys, json alongside
                datetime; routes/task_routes.py imports json, os, sys, time — none of
                which appear in any expression in that file.
Impact:         Signals copy-paste origin; increases interpreter startup overhead
                marginally; more importantly, an auditor cannot tell which imports are
                intentional without reading the entire file.
Recommendation: Remove all unused imports. For app.py, keep only the datetime import
                (used in the /health route). For task_routes.py, remove the entire
                stdlib block.

================================
Total: 13 findings
CRITICAL: 3 | HIGH: 3 | MEDIUM: 4 | LOW: 3
================================
