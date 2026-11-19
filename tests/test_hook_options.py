import unittest

from studio.brain import rank_hook_options


class HookOptionTests(unittest.TestCase):
    def test_ranks_accuracy_and_other_quality_signals(self):
        options = [
            {"text": "WAIT FOR IT", "curiosity": 95, "clarity": 90, "relevance": 90, "accuracy": 30},
            {"text": "ONE SHOT LEFT", "curiosity": 80, "clarity": 90, "relevance": 95, "accuracy": 100},
        ]
        ranked = rank_hook_options(options)
        self.assertEqual(ranked[0]["text"], "ONE SHOT LEFT")
        self.assertGreater(ranked[0]["score"], ranked[1]["score"])

    def test_rejects_empty_long_and_duplicate_options(self):
        options = [
            {"text": "", "curiosity": 100, "clarity": 100, "relevance": 100, "accuracy": 100},
            {"text": "THIS HOOK HAS WAY TOO MANY WORDS", "curiosity": 100, "clarity": 100, "relevance": 100, "accuracy": 100},
            {"text": "THE CLUTCH", "curiosity": 80, "clarity": 90, "relevance": 90, "accuracy": 95},
            {"text": "the clutch", "curiosity": 100, "clarity": 100, "relevance": 100, "accuracy": 100},
        ]
        ranked = rank_hook_options(options)
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0]["text"], "THE CLUTCH")

    def test_legacy_hook_remains_a_fallback(self):
        ranked = rank_hook_options([], "Wait for it")
        self.assertEqual(ranked[0]["text"], "WAIT FOR IT")
        self.assertEqual(ranked[0]["score"], 50)

    def test_only_five_options_are_exposed(self):
        options = [
            {"text": f"HOOK {i}", "curiosity": 50, "clarity": 50, "relevance": 50, "accuracy": 50}
            for i in range(7)
        ]
        self.assertEqual(len(rank_hook_options(options)), 5)


if __name__ == "__main__":
    unittest.main()
