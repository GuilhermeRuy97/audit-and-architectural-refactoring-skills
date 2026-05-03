================================
ARCHITECTURE AUDIT REPORT
================================
Project:   code-smells-project
Stack:     Python + Flask 3.1.1
Files:     4 analyzed | ~782 lines of code
================================

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 2 | LOW: 2
Total findings: 10

## Findings

### [CRITICAL] SQL Injection throughout models.py
File:           models.py:28, 47-50, 57-60, 65-68, 92, 109-112, 126-130,
                140, 149-150, 155-165, 174, 188, 192-193, 280-297
Relevant code:
  cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
  cursor.execute("INSERT INTO produtos (nome, …) VALUES ('" + nome + "', …)")
  cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
  query += " AND (nome LIKE '%" + termo + "%')"
Description:    Every query in models.py is built by concatenating user-supplied
                values directly into SQL strings. No parameterized queries exist
                anywhere in the file. The login query (lines 109-112) allows trivial
                authentication bypass: supplying email = "' OR '1'='1" logs in as
                any user. The search endpoint (lines 285-297) allows UNION-based
                data exfiltration.
Impact:         Full database compromise — authentication bypass, extraction of all
                user passwords, and destructive queries — all accessible without
                any credentials via standard HTTP requests.
Recommendation: Replace every concatenated query with a parameterized form:
                cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
                cursor.execute("INSERT INTO produtos (nome) VALUES (?)", (nome,))

### [CRITICAL] Unauthenticated arbitrary SQL execution endpoint
File:           app.py:59-78 (/admin/query)
                app.py:47-57 (/admin/reset-db)
Relevant code:
  @app.route("/admin/query", methods=["POST"])
  def executar_query():
      dados = request.get_json()
      query = dados.get("sql", "")
      cursor.execute(query)
Description:    The /admin/query route accepts any SQL string from the request body
                and executes it directly against the database. No authentication,
                no allowlist, no restrictions of any kind. The companion
                /admin/reset-db endpoint (lines 47-57) truncates all four tables
                with a single POST request — also with no auth.
Impact:         Any anonymous HTTP client can submit {"sql": "DROP TABLE usuarios"}
                or SELECT all user data. This is a complete remote database takeover
                accessible from the internet with one curl command.
Recommendation: Remove /admin/query entirely — arbitrary SQL execution has no place
                in a production API. Remove or add strict authentication + role check
                to /admin/reset-db, and replace it with specific, named admin operations.

### [CRITICAL] Hardcoded SECRET_KEY in source and actively leaked in API response
File:           app.py:7  (hardcoded in source)
                controllers.py:289  (returned in JSON response body)
Relevant code:
  # app.py:7
  app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
  # controllers.py:289
  "secret_key": "minha-chave-super-secreta-123"
Description:    The application's signing key is hardcoded as a string literal
                committed to version control. Worse, the /health endpoint explicitly
                returns this secret key in plaintext to any caller. Every request
                to GET /health leaks the key.
Impact:         Attackers can forge session tokens. The credential lives permanently
                in git history. Any monitoring tool, proxy, or CDN log captures
                the key passively on every health check poll.
Recommendation: Move to environment variable: SECRET_KEY = os.environ["SECRET_KEY"].
                Remove the secret_key field from the health check response entirely.

### [HIGH] Passwords stored in plaintext and returned in API responses
File:           database.py:76-83  (seed data with plaintext passwords)
                models.py:79-87    (get_todos_usuarios returns senha field)
                controllers.py:128-134  (listar_usuarios exposes all passwords)
Relevant code:
  ("Admin", "admin@loja.com", "admin123", "admin"),
  "senha": row["senha"],
Description:    User passwords are stored as plaintext in the database (no hashing).
                get_todos_usuarios() returns the senha field to every caller, and
                listar_usuarios exposes all users including their passwords via GET
                /usuarios with no authentication required.
Impact:         Any database leak immediately reveals every user's real password.
                The /usuarios endpoint actively broadcasts all passwords in plain
                HTTP responses to any anonymous caller.
Recommendation: Hash all passwords with bcrypt before storage. Remove senha from
                all serialization. Never return password data in any response.

### [HIGH] No authentication on any endpoint
File:           app.py:11-30
Relevant code:
  app.add_url_rule("/usuarios", "listar_usuarios", controllers.listar_usuarios, methods=["GET"])
  app.add_url_rule("/pedidos", "listar_todos_pedidos", controllers.listar_todos_pedidos, methods=["GET"])
Description:    Every endpoint — products, users, orders, and reports — is publicly
                accessible with no token or session check. Any anonymous HTTP client
                can list all users (with passwords), read all orders, or change any
                order status. The login endpoint issues no token at all.
Impact:         Complete data exposure and unauthorized write access to all resources.
Recommendation: Implement a require_auth decorator using PyJWT. Apply it to all
                non-public endpoints. Login issues a signed JWT; protected routes
                validate it before execution.

### [HIGH] DEBUG mode hardcoded True in production configuration
File:           app.py:8 and app.py:88
Relevant code:
  app.config["DEBUG"] = True
  app.run(host="0.0.0.0", port=5000, debug=True)
Description:    DEBUG=True is hardcoded in both the app config and the run() call.
                Flask's debug mode activates the Werkzeug interactive debugger,
                which allows executing arbitrary Python in the browser when an
                exception occurs. The health endpoint also returns "ambiente": "producao"
                while debug is True simultaneously.
Impact:         Any uncaught exception exposes an interactive Python shell accessible
                from the network. The "producao" label actively misleads operators.
Recommendation: Read from environment:
                DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

### [MEDIUM] N+1 query problem in order listing
File:           models.py:171-233
Relevant code:
  cursor.execute("SELECT * FROM pedidos WHERE usuario_id = …")
  for row in rows:
      cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = …")
      for item in itens:
          cursor3.execute("SELECT nome FROM produtos WHERE id = …")
Description:    get_pedidos_usuario and get_todos_pedidos use two nested cursor loops:
                one query per order for its items, then one per item for the product
                name. For N orders with M items each, this issues 1 + N + (N×M) queries.
Impact:         For a store with 50 orders of 5 items each, listing orders fires 301
                queries. Response time degrades O(N×M) with data volume.
Recommendation: Replace nested loops with a single LEFT JOIN across orders, items,
                and products. Reassemble the nested structure in Python after one
                round-trip query.

### [MEDIUM] Business logic (discount calculation) embedded in Model layer
File:           models.py:256-262
Relevant code:
  if faturamento > 10000:
      desconto = faturamento * 0.1
  elif faturamento > 5000:
      desconto = faturamento * 0.05
  elif faturamento > 1000:
      desconto = faturamento * 0.02
Description:    The relatorio_vendas() function mixes DB queries with discount
                business rules using magic number thresholds and rates. Business
                rules must not live alongside data access — they cannot be unit-tested
                without a real database.
Impact:         Changing the discount policy requires editing the same file as SQL
                queries. Magic numbers are opaque and may drift inconsistently.
Recommendation: Extract discount logic to a ReportController with named constants
                (DISCOUNT_TIERS). The model returns raw totals; the controller
                applies the rules.

### [LOW] Print statements used as fake notification system
File:           controllers.py:208-210
Relevant code:
  print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado …")
  print("ENVIANDO SMS: Seu pedido foi recebido!")
  print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")
Description:    Order creation uses print() to simulate email, SMS, and push
                notifications. No actual notification is sent. These go to stdout
                in production with no structure or log routing.
Impact:         Operators believe notifications work when they do not. No structured
                logging means no alerting or monitoring is possible.
Recommendation: Replace with Python logging module. Stub a NotificationService
                that can be wired to a real provider without touching the controller.

### [LOW] Input validation duplicated between create and update product handlers
File:           controllers.py:28-55  (criar_produto)
                controllers.py:72-91  (atualizar_produto)
Relevant code:
  if "nome" not in dados: return jsonify({"erro": "Nome é obrigatório"}), 400
  if preco < 0: return jsonify({"erro": "Preço não pode ser negativo"}), 400
  categorias_validas = ["informatica", "moveis", "vestuario", "geral", …]
Description:    The field validation block is copy-pasted verbatim between
                criar_produto and atualizar_produto including the inline category list.
Impact:         Changing a rule requires updating two locations; lists can drift,
                causing inconsistent create vs. update behavior.
Recommendation: Extract to validate_product_data(data) in a shared helpers module.
                Define VALID_CATEGORIES as a module-level constant.

================================
Total: 10 findings
CRITICAL: 3 | HIGH: 3 | MEDIUM: 2 | LOW: 2
================================
