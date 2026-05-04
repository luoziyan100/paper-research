import unittest
from pathlib import Path

from paper_research import WorkflowConfig, run_research_workflow
from paper_research.models import RoundResult


class CodeStructureTest(unittest.TestCase):
    def test_workflow_module_stays_below_maintainability_threshold(self):
        workflow_path = Path("paper_research/workflow.py")
        line_count = len(workflow_path.read_text(encoding="utf-8").splitlines())

        self.assertLessEqual(line_count, 1100)

    def test_public_api_and_models_remain_importable(self):
        self.assertEqual(WorkflowConfig.__name__, "WorkflowConfig")
        self.assertEqual(RoundResult.__name__, "RoundResult")
        self.assertTrue(callable(run_research_workflow))


if __name__ == "__main__":
    unittest.main()
