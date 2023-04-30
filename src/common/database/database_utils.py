from typing import Dict

from sqlalchemy import Column, asc, desc
from sqlalchemy.orm import Query


def add_pagination(query: Query, filters: Dict) -> Query:
    page = get_page(filters)
    page_size = get_page_size(filters)

    query = query.limit(page_size)
    query = query.offset(page * page_size)
    return query


def get_page(filters: Dict) -> int:
    page = filters.get("page")
    return page if page is not None else 0


def get_page_size(filters: Dict) -> int:
    page_size = filters.get("page_size")
    return page_size if page_size is not None else 50


def add_sorting(query: Query, column: Column, filters: Dict) -> Query:
    sort_order = filters.get("sort_order")
    if sort_order in {"asc", "ASC"}:
        query = query.order_by(asc(column))
    if sort_order in {"desc", "DESC"}:
        query = query.order_by(desc(column))
    return query
