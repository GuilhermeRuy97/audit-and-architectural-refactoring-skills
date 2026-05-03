import bcrypt
from database import get_db


def _safe_dict(row):
    """Return user dict without the password hash."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_all():
    db = get_db()
    rows = db.execute("SELECT * FROM usuarios").fetchall()
    return [_safe_dict(r) for r in rows]


def get_by_id(user_id):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
    return _safe_dict(row) if row else None


def get_by_email(email):
    """Returns full row including password hash — only for auth check."""
    db = get_db()
    return db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()


def create(nome, email, senha_plaintext, tipo="cliente"):
    hashed = bcrypt.hashpw(senha_plaintext.encode(), bcrypt.gensalt()).decode()
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, hashed, tipo),
    )
    db.commit()
    return cursor.lastrowid


def verify_password(user_row, senha_plaintext):
    return bcrypt.checkpw(senha_plaintext.encode(), user_row["senha"].encode())
