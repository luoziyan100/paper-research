"""Paper research report workflow."""

from paper_research.benchmark import BenchmarkSearchAgent
from paper_research.scoring import ReportScoringAgent
from paper_research.workflow import (
    ContinuousRunConfig,
    WorkflowConfig,
    run_continuous_workflow,
    run_research_workflow,
)

__all__ = [
    "BenchmarkSearchAgent",
    "ContinuousRunConfig",
    "ReportScoringAgent",
    "WorkflowConfig",
    "run_continuous_workflow",
    "run_research_workflow",
]
