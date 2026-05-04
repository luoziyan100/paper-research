"""Scoring helper functions shared by agents."""

from __future__ import annotations

from typing import Optional

from paper_research.models import CriticReview, Scorecard


def low_score_summary(scorecard: Optional[Scorecard], language: str) -> str:
    if not scorecard:
        return "暂无上一轮评分" if language == "zh" else "no prior scorecard"
    threshold = 12 if language == "zh" else 14
    low_scores = [
        f"{score.name} {score.points}/{score.max_points}"
        for score in scorecard.scores
        if score.points <= threshold
    ]
    if low_scores:
        return "；".join(low_scores) if language == "zh" else "; ".join(low_scores)
    return "没有明显低分项" if language == "zh" else "no clear low-score items"


def critic_mentions_reproducibility(critic_review: Optional[CriticReview]) -> bool:
    if not critic_review:
        return False
    combined = " ".join(critic_review.issues + critic_review.recommendations).lower()
    return "reproduc" in combined or "可复现" in combined or "证据引用" in combined
