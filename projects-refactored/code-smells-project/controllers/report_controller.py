from models import order_model

# Discount tiers: (minimum_revenue_threshold, discount_rate)
DISCOUNT_TIERS = [
    (10_000, 0.10),
    (5_000,  0.05),
    (1_000,  0.02),
]


def get_sales_report():
    totals = order_model.get_sales_totals()
    faturamento = totals["faturamento"]
    total_pedidos = totals["total_pedidos"]

    discount_rate = next(
        (rate for threshold, rate in DISCOUNT_TIERS if faturamento > threshold),
        0,
    )
    desconto = round(faturamento * discount_rate, 2)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": desconto,
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": totals["pendentes"],
        "pedidos_aprovados": totals["aprovados"],
        "pedidos_cancelados": totals["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
