from database import get_db


def _fetch_orders(where_clause, params):
    """Fetch orders with items in a single JOIN query — eliminates N+1 problem."""
    db = get_db()
    sql = f"""
        SELECT
            p.id, p.usuario_id, p.status, p.total, p.criado_em,
            ip.produto_id, ip.quantidade, ip.preco_unitario,
            pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
        {where_clause}
        ORDER BY p.id
    """
    rows = db.execute(sql, params).fetchall()
    return _assemble(rows)


def _assemble(rows):
    orders = {}
    for row in rows:
        oid = row["id"]
        if oid not in orders:
            orders[oid] = {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
        if row["produto_id"] is not None:
            orders[oid]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] or "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(orders.values())


def get_all():
    return _fetch_orders("", ())


def get_by_user(usuario_id):
    return _fetch_orders("WHERE p.usuario_id = ?", (usuario_id,))


def create(usuario_id, itens):
    db = get_db()

    # Validate stock and collect price data in one pass per item
    item_data = []
    total = 0
    for item in itens:
        row = db.execute(
            "SELECT id, preco, estoque, nome FROM produtos WHERE id = ? AND ativo = 1",
            (item["produto_id"],),
        ).fetchone()
        if row is None:
            return None, f"Produto {item['produto_id']} não encontrado"
        if row["estoque"] < item["quantidade"]:
            return None, f"Estoque insuficiente para {row['nome']}"
        total += row["preco"] * item["quantidade"]
        item_data.append({
            "produto_id": item["produto_id"],
            "quantidade": item["quantidade"],
            "preco_unitario": row["preco"],
        })

    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    pedido_id = cursor.lastrowid

    for item in item_data:
        db.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
        )
        db.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}, None


def update_status(pedido_id, novo_status):
    db = get_db()
    db.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()


def get_sales_totals():
    db = get_db()
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos").fetchone()[0]
    pendentes = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'").fetchone()[0]
    aprovados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'").fetchone()[0]
    cancelados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'").fetchone()[0]
    return {
        "total_pedidos": total_pedidos,
        "faturamento": faturamento,
        "pendentes": pendentes,
        "aprovados": aprovados,
        "cancelados": cancelados,
    }
