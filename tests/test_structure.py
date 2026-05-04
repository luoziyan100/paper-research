import unittest
from importlib import import_module
from pathlib import Path

from paper_research import BenchmarkSearchAgent, WorkflowConfig, run_research_workflow
from paper_research.models import RoundResult


class CodeStructureTest(unittest.TestCase):
    def test_workflow_module_stays_below_maintainability_threshold(self):
        workflow_path = Path("paper_research/workflow.py")
        line_count = len(workflow_path.read_text(encoding="utf-8").splitlines())

        self.assertLessEqual(line_count, 950)

    def test_public_api_and_models_remain_importable(self):
        self.assertEqual(WorkflowConfig.__name__, "WorkflowConfig")
        self.assertEqual(BenchmarkSearchAgent.__name__, "BenchmarkSearchAgent")
        self.assertEqual(RoundResult.__name__, "RoundResult")
        self.assertTrue(callable(run_research_workflow))

    def test_benchmark_search_agent_has_dedicated_module(self):
        benchmark_module = import_module("paper_research.benchmark")

        self.assertEqual(benchmark_module.BenchmarkSearchAgent.__name__, "BenchmarkSearchAgent")


if __name__ == "__main__":
    unittest.main()
