from __future__ import annotations
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID
from sqlalchemy import func, or_, select, update
from app.models.enums import ThreatCategory
from app.models.threat_pattern import ThreatPattern
from app.repositories.base import RepositoryBase
from app.utils.url_parser import extract_domain, normalize_url


class ThreatRepository(RepositoryBase):
    """Database operations for threat patterns."""

    async def create_pattern(self, pattern_data: Mapping[str, object]) -> ThreatPattern:
        """Create a threat pattern."""

        pattern = ThreatPattern(**self._mapping_data(pattern_data))
        self.db.add(pattern)
        await self.db.commit()
        await self.db.refresh(pattern)
        return pattern

    async def update_pattern(self, pattern_id: UUID, update_data: Mapping[str, object]) -> ThreatPattern | None:
        """Update a threat pattern."""

        pattern = await self.get_pattern(pattern_id)
        if pattern is None:
            return None
        for key, value in self._mapping_data(update_data).items():
            if hasattr(pattern, key):
                setattr(pattern, key, value)
        await self.db.commit()
        await self.db.refresh(pattern)
        return pattern

    async def get_pattern(self, pattern_id: UUID) -> ThreatPattern | None:
        """Fetch a pattern by UUID."""

        result = await self.db.execute(
            select(ThreatPattern).where(ThreatPattern.id == pattern_id)
        )
        return result.scalar_one_or_none()

    async def find_matching_pattern(
        self,
        *,
        malicious_domain: str | None = None,
        malicious_phone: str | None = None,
        keyword_signature: str | None = None,
        threat_category: ThreatCategory | None = None,
    ) -> ThreatPattern | None:
        """Find a pattern that matches any supplied indicators."""

        filters = []
        if malicious_domain:
            domain = extract_domain(normalize_url(malicious_domain)) if malicious_domain.startswith(("http://", "https://")) else malicious_domain.lower()
            filters.append(func.lower(ThreatPattern.malicious_domain) == domain.lower())
        if malicious_phone:
            filters.append(ThreatPattern.malicious_phone == malicious_phone)
        if keyword_signature:
            filters.append(ThreatPattern.keyword_signature.ilike(f"%{keyword_signature}%"))
        if threat_category is not None:
            filters.append(ThreatPattern.threat_category == threat_category)
        if not filters:
            return None
        stmt = (
            select(ThreatPattern)
            .where(or_(*filters))
            .order_by(ThreatPattern.last_seen.desc().nullslast(), ThreatPattern.reports_count.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def increment_reports_count(
        self,
        pattern_id: UUID,
        *,
        amount: int = 1,
        last_seen: datetime | None = None,
    ) -> ThreatPattern | None:
        """Increment the report counter for a pattern."""

        pattern = await self.get_pattern(pattern_id)
        if pattern is None:
            return None
        pattern.reports_count += amount
        pattern.last_seen = last_seen or datetime.now(tz=UTC)
        await self.db.commit()
        await self.db.refresh(pattern)
        return pattern

    async def list_patterns(
        self,
        *,
        page: int = 1,
        size: int = 20,
        threat_category: ThreatCategory | None = None,
    ) -> tuple[list[ThreatPattern], int]:
        """List patterns with optional filtering."""

        stmt = select(ThreatPattern)
        count_stmt = self._count_statement(ThreatPattern)
        if threat_category is not None:
            stmt = stmt.where(ThreatPattern.threat_category == threat_category)
            count_stmt = count_stmt.where(ThreatPattern.threat_category == threat_category)
        stmt = stmt.order_by(ThreatPattern.reports_count.desc(), ThreatPattern.confidence_score.desc())
        return await self._paginate(stmt, count_stmt, page=page, size=size)

    async def top_patterns(self, *, limit: int = 10) -> list[ThreatPattern]:
        """Return the highest priority threat patterns."""

        result = await self.db.execute(
            select(ThreatPattern)
            .order_by(ThreatPattern.reports_count.desc(), ThreatPattern.confidence_score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

