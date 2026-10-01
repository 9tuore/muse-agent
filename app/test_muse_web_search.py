import unittest
from unittest.mock import patch

from muse_web_search import search_public


HTML = b'''<html><ol id="b_results">
<li class="b_algo"><h2><a href="https://packaging.python.org/">Python Packaging User Guide</a></h2>
<p class="b_lineclamp2">Official guide for packaging.</p></li>
<li class="b_algo"><h2><a href="https://127.0.0.1/admin">Private admin</a></h2></li>
<li class="b_algo"><h2><a href="https://example.org/other">Other source</a></h2></li>
</ol></html>'''


class FakeResponse:
    status = 200

    def getheader(self, name, default=""):
        return "text/html; charset=utf-8" if name == "Content-Type" else default

    def read(self, size):
        return HTML


class FakeConnection:
    def __init__(self, host, address):
        self.host = host

    def request(self, method, path, headers):
        self.method, self.path = method, path

    def getresponse(self):
        return FakeResponse()

    def close(self):
        pass


class SearchTests(unittest.TestCase):
    def test_public_domain_filter_excludes_private_and_unapproved_results(self):
        with patch("muse_web_search._PinnedHTTPS", FakeConnection), \
             patch("muse_web_search._public_address", return_value="151.101.0.223"):
            output = search_public("Python packaging", allowed_domains=["packaging.python.org"])
        self.assertEqual(output["candidate_count"], 3)
        self.assertEqual(len(output["results"]), 1)
        self.assertEqual(output["results"][0]["rank"], 1)
        self.assertEqual(output["results"][0]["url"], "https://packaging.python.org/")
        self.assertTrue(output["untrusted_source"])

    def test_invalid_limit_and_query_are_rejected_before_network(self):
        for query, limit in (("", 1), ("x", 1), ("Python", 11), ("Python", True)):
            with self.subTest(query=query, limit=limit):
                with self.assertRaisesRegex(ValueError, "search_query_or_limit_invalid"):
                    search_public(query, max_results=limit)


if __name__ == "__main__":
    unittest.main()
