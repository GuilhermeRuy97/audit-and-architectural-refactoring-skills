import logging
from middlewares.error_handler import ValidationError, NotFoundError
from models import product_model

logger = logging.getLogger(__name__)

VALID_CATEGORIES = product_model.VALID_CATEGORIES


def _validate(data, require_all=True):
    if require_all:
        for field in ("nome", "preco", "estoque"):
            if field not in data:
                raise ValidationError(f"{field} é obrigatório")

    nome = data.get("nome", "")
    if nome and not (2 <= len(nome) <= 200):
        raise ValidationError("Nome deve ter entre 2 e 200 caracteres")

    preco = data.get("preco")
    if preco is not None and preco < 0:
        raise ValidationError("Preço não pode ser negativo")

    estoque = data.get("estoque")
    if estoque is not None and estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")

    categoria = data.get("categoria", "geral")
    if categoria not in VALID_CATEGORIES:
        raise ValidationError(f"Categoria inválida. Válidas: {VALID_CATEGORIES}")


def list_all():
    return product_model.get_all()


def get_one(product_id):
    produto = product_model.get_by_id(product_id)
    if not produto:
        raise NotFoundError("Produto não encontrado")
    return produto


def search(termo, categoria, preco_min, preco_max):
    return product_model.search(termo, categoria, preco_min, preco_max)


def create(data):
    _validate(data, require_all=True)
    product_id = product_model.create(
        nome=data["nome"],
        descricao=data.get("descricao", ""),
        preco=data["preco"],
        estoque=data["estoque"],
        categoria=data.get("categoria", "geral"),
    )
    logger.info("Produto criado: id=%s", product_id)
    return product_model.get_by_id(product_id)


def update(product_id, data):
    if not product_model.get_by_id(product_id):
        raise NotFoundError("Produto não encontrado")
    _validate(data, require_all=True)
    product_model.update(
        product_id,
        nome=data["nome"],
        descricao=data.get("descricao", ""),
        preco=data["preco"],
        estoque=data["estoque"],
        categoria=data.get("categoria", "geral"),
    )
    logger.info("Produto atualizado: id=%s", product_id)
    return product_model.get_by_id(product_id)


def delete(product_id):
    if not product_model.get_by_id(product_id):
        raise NotFoundError("Produto não encontrado")
    product_model.delete(product_id)
    logger.info("Produto deletado: id=%s", product_id)
