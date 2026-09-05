"""In-memory reputation scoring engine."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import DefaultDict


@dataclass(slots=True)
class ReputationRecord:
    """Represents a reputation score for a tracked entity."""

    entity: str
    trust_score: float = 100.0
    report_count: int = 0


@dataclass(slots=True)
class ReputationEngine:
    """Maintain reputation scores for URLs, phones, and accounts."""

    records: DefaultDict[str, ReputationRecord] = field(
        default_factory=lambda: defaultdict(lambda: ReputationRecord(entity="", trust_score=100.0, report_count=0))
    )

    def _get_record(self, entity: str) -> ReputationRecord:
        record = self.records[entity]
        if record.entity == "":
            record.entity = entity
        return record

    def register_report(self, entity: str, severity: float = 1.0) -> ReputationRecord:
        """Decrease trust score for an entity when a report is received."""

        record = self._get_record(entity)
        record.report_count += 1
        record.trust_score = max(0.0, record.trust_score - (severity * 8.0))
        return record

    def register_positive_signal(self, entity: str, weight: float = 1.0) -> ReputationRecord:
        """Increase trust score for a validated entity."""

        record = self._get_record(entity)
        record.trust_score = min(100.0, record.trust_score + (weight * 5.0))
        return record

    def get_trust_score(self, entity: str) -> float:
        """Return the trust score for an entity."""

        return self._get_record(entity).trust_score

