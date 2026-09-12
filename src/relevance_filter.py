"""Curio — Relevance Filter (Appraisal Engine).

Decides whether a detected gap is worth learning about.
Not everything is worth knowing — this is the quality filter
that makes Curio selective, like a child's brain.
"""

from __future__ import annotations

from .audit_log import AuditLog
from .knowledge_store import KnowledgeStore
from .models import (
    Appraisal, AuditAction, Gap, LearningDecision, Priority, _now,
)


class RelevanceFilter:
    """Scores gaps and decides whether to learn, defer, or ignore."""

    def __init__(self, store: KnowledgeStore, audit: AuditLog):
        self.store = store
        self.audit = audit

        # Active goals/topics Curio is tracking
        self._active_goals: list[str] = []
        # Domain keywords Curio is interested in
        self._tracked_domains: list[str] = []
        # Frequency counter for topics
        self._topic_frequency: dict[str, int] = {}

    def set_goals(self, goals: list[str]):
        """Set the active goals Curio should prioritize."""
        self._active_goals = goals

    def set_domains(self, domains: list[str]):
        """Set the domains Curio is tracking."""
        self._tracked_domains = domains

    def appraise(self, gap: Gap) -> Appraisal:
        """Appraise a gap and decide whether to learn.

        Scoring formula:
            relevance = (goal_alignment × 0.3)
                      + (domain_match × 0.25)
                      + (frequency × 0.2)
                      + (impact × 0.15)
                      + (learnability × 0.1)

        If relevance > 0.5 → LEARN
        If relevance 0.2–0.5 → DEFER
        If relevance < 0.2 → IGNORE
        """
        goal_score = self._score_goal_alignment(gap)
        domain_score = self._score_domain_match(gap)
        frequency_score = self._score_frequency(gap)
        impact_score = self._score_impact(gap)
        learnability_score = self._score_learnability(gap)

        relevance = (
            goal_score * 0.3
            + domain_score * 0.25
            + frequency_score * 0.2
            + impact_score * 0.15
            + learnability_score * 0.1
        )

        # Decision
        if relevance > 0.5:
            decision = LearningDecision.LEARN
        elif relevance > 0.2:
            decision = LearningDecision.DEFER
        else:
            decision = LearningDecision.IGNORE

        # Suggest sources based on gap type and domain
        sources = self._suggest_sources(gap)

        appraisal = Appraisal(
            gap_id=gap.gap_id,
            decision=decision,
            relevance_score=round(relevance, 3),
            reasoning=self._build_reasoning(
                gap, goal_score, domain_score, frequency_score,
                impact_score, learnability_score, decision,
            ),
            suggested_sources=sources,
        )

        # Update frequency tracker
        self._topic_frequency[gap.topic] = (
            self._topic_frequency.get(gap.topic, 0) + 1
        )

        # Audit
        self.audit.log(
            AuditAction.APPRAISED,
            target_id=gap.gap_id,
            decision=decision.value,
            relevance_score=appraisal.relevance_score,
            goal_score=goal_score,
            domain_score=domain_score,
            frequency_score=frequency_score,
            impact_score=impact_score,
            learnability_score=learnability_score,
        )

        return appraisal

    def _score_goal_alignment(self, gap: Gap) -> float:
        """How well does this gap align with active goals?"""
        if not self._active_goals:
            return 0.3  # Neutral if no goals set

        topic_lower = gap.topic.lower()
        for goal in self._active_goals:
            goal_words = set(goal.lower().split())
            topic_words = set(topic_lower.split())
            overlap = len(goal_words & topic_words)
            if overlap > 0:
                return min(1.0, overlap / max(len(goal_words), 1))

        return 0.1

    def _score_domain_match(self, gap: Gap) -> float:
        """Is this gap in a tracked domain?"""
        if not self._tracked_domains:
            return 0.5  # Neutral if no domains set

        topic_lower = gap.topic.lower()
        for domain in self._tracked_domains:
            if domain.lower() in topic_lower or topic_lower in domain.lower():
                return 1.0
            domain_words = set(domain.lower().split())
            topic_words = set(topic_lower.split())
            if len(domain_words & topic_words) > 0:
                return 0.7

        return 0.2

    def _score_frequency(self, gap: Gap) -> float:
        """How often has this topic come up?"""
        count = self._topic_frequency.get(gap.topic, 0)
        if count == 0:
            return 0.3
        elif count == 1:
            return 0.5
        elif count < 5:
            return 0.7
        else:
            return 1.0

    def _score_impact(self, gap: Gap) -> float:
        """What's the cost of not knowing this?"""
        if gap.priority == Priority.HIGH:
            return 1.0
        elif gap.priority == Priority.MEDIUM:
            return 0.6
        else:
            return 0.3

    def _score_learnability(self, gap: Gap) -> float:
        """Can this actually be learned from available sources?"""
        # Errors and contradictions are highly learnable
        if gap.type.value in ("CONTRADICTORY", "OUTDATED"):
            return 0.9

        # UNKNOWN gaps are learnable if they're specific enough
        if gap.type.value == "UNKNOWN":
            topic_words = gap.topic.split()
            if len(topic_words) >= 2:
                return 0.8  # Specific enough to search for
            return 0.4  # Too vague

        # INCOMPLETE gaps are moderately learnable
        return 0.7

    def _suggest_sources(self, gap: Gap) -> list[str]:
        """Suggest where to look for information about this gap."""
        sources = []

        if gap.type.value == "OUTDATED":
            sources.append("web_search:official_docs")
            sources.append("web_search:changelog")

        elif gap.type.value == "CONTRADICTORY":
            sources.append("web_search:official_docs")
            sources.append("local_files:config")

        elif gap.type.value == "UNKNOWN":
            sources.append("web_search:documentation")
            sources.append("web_search:tutorials")

        elif gap.type.value == "INCOMPLETE":
            sources.append("web_search:deep_docs")
            sources.append("local_files:related")

        return sources

    def _build_reasoning(
        self, gap: Gap,
        goal: float, domain: float, freq: float,
        impact: float, learnability: float,
        decision: LearningDecision,
    ) -> str:
        """Build a human-readable reasoning for the appraisal."""
        parts = [
            f"Gap type: {gap.type.value}",
            f"Topic: {gap.topic[:60]}",
            f"",
            f"Scores:",
            f"  Goal alignment:    {goal:.2f}",
            f"  Domain match:      {domain:.2f}",
            f"  Frequency:         {freq:.2f}",
            f"  Impact:            {impact:.2f}",
            f"  Learnability:      {learnability:.2f}",
            f"",
            f"Decision: {decision.value}",
        ]
        return "\n".join(parts)
