from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


class RepositoryBase:
    """Shared helpers for async SQLAlchemy repositories."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def _normalize_pagination(page: int | None, size: int | None) -> tuple[int, int]:
        page_value = max(page or 1, 1)
        size_value = max(size or 20, 1)
        return page_value, size_value

    async def _paginate(
        self,
        stmt: Select[Any],
        count_stmt: Select[Any],
        *,
        page: int | None = None,
        size: int | None = None,
    ) -> tuple[list[Any], int]:
        """Execute a paginated query and return items plus total count."""

        page_value, size_value = self._normalize_pagination(page, size)
        total = await self.db.scalar(count_stmt)
        result = await self.db.execute(
            stmt.offset((page_value - 1) * size_value).limit(size_value)
        )
        return list(result.scalars().all()), int(total or 0)

    @staticmethod
    def _count_statement(entity: Any, *criteria: Any) -> Select[Any]:
        """Build a count query for an ORM entity."""

        stmt = select(func.count()).select_from(entity)
        if criteria:
            stmt = stmt.where(*criteria)
        return stmt

    @staticmethod
    def _mapping_data(data: Mapping[str, Any] | None) -> dict[str, Any]:
        """Normalize mapping-like input into a plain dictionary."""

        return dict(data or {})

