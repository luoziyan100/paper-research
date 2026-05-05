import unittest

from paper_research.web_search import extract_duckduckgo_results


class WebSearchParsingTest(unittest.TestCase):
    def test_redirect_target_whitespace_is_ignored(self):
        html = """
        <a class="result__a" href="/url?q=%20https%3A%2F%2Fexample.com%2Fspaced-report%20">
          Spaced Redirect Report
        </a>
        <div class="result__snippet">
          Spaced redirect snippet.
        </div>
        """

        results = extract_duckduckgo_results(html)

        self.assertEqual(results[0]["url"], "https://example.com/spaced-report")
        self.assertEqual(results[0]["snippet"], "Spaced redirect snippet.")


if __name__ == "__main__":
    unittest.main()
