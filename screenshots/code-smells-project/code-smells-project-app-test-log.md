(.venv) PS C:\GitHub\GuilhermeRuy97\audit-and-architectural-refactoring-skills\projects-refactored\code-smells-project> python app.py
C:\GitHub\GuilhermeRuy97\audit-and-architectural-refactoring-skills\projects-refactored\code-smells-project\app.py:4: UserWarning: SECRET_KEY not set — using insecure development default. Set the SECRET_KEY environment variable before deploying.
  from config import settings
 * Serving Flask app 'app'
 * Debug mode: off
2026-05-03 13:59:00,392 INFO werkzeug: WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.68.001:5000
2026-05-03 13:59:00,393 INFO werkzeug: Press CTRL+C to quit
2026-05-03 13:59:00,517 INFO werkzeug: 127.0.0.1 - - [03/May/2026 13:59:00] "GET /health HTTP/1.1" 200 -
2026-05-03 14:00:47,096 INFO werkzeug: 127.0.0.1 - - [03/May/2026 14:00:47] "GET /health HTTP/1.1" 200 -
2026-05-03 14:01:09,849 INFO werkzeug: 127.0.0.1 - - [03/May/2026 14:01:09] "GET /login HTTP/1.1" 405 -
2026-05-03 14:01:32,458 INFO werkzeug: 127.0.0.1 - - [03/May/2026 14:01:32] "GET /pedidos HTTP/1.1" 401 -
2026-05-03 14:01:47,760 INFO werkzeug: 127.0.0.1 - - [03/May/2026 14:01:47] "GET /produtos HTTP/1.1" 200 -
2026-05-03 14:02:09,154 INFO werkzeug: 127.0.0.1 - - [03/May/2026 14:02:09] "GET /relatorios/vendas HTTP/1.1" 401 -
2026-05-03 14:02:23,051 INFO werkzeug: 127.0.0.1 - - [03/May/2026 14:02:23] "GET /usuarios HTTP/1.1" 401 -