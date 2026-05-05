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

    def test_protocol_relative_redirect_target_becomes_https(self):
        html = """
        <a class="result__a" href="/url?q=%2F%2Fexample.com%2Fprotocol-report">
          Protocol Relative Report
        </a>
        <div class="result__snippet">
          Protocol relative snippet.
        </div>
        """

        results = extract_duckduckgo_results(html)

        self.assertEqual(results[0]["url"], "https://example.com/protocol-report")

    def test_direct_protocol_relative_result_becomes_https(self):
        html = """
        <a class="result__a" href=" //example.com/direct-report ">
          Direct Protocol Relative Report
        </a>
        <div class="result__snippet">
          Direct protocol relative snippet.
        </div>
        """

        results = extract_duckduckgo_results(html)

        self.assertEqual(results[0]["url"], "https://example.com/direct-report")

    def test_skipped_anchor_does_not_steal_next_snippet(self):
        html = """
        <a class="result__a" href="ftp://example.com/skip">
          Skipped Result
        </a>
        <div class="result__snippet">
          Skipped snippet.
        </div>
        <a class="result__a" href="https://example.com/real">
          Real Result
        </a>
        <div class="result__snippet">
          Real snippet.
        </div>
        """

        results = extract_duckduckgo_results(html)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Real Result")
        self.assertEqual(results[0]["snippet"], "Real snippet.")


if __name__ == "__main__":
    unittest.main()
