import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from hedge_detector.cli import main
from hedge_detector.core import detect, summarize


def cats(text, **kw):
    return [(f.category, f.match.lower()) for f in detect(text, **kw)]


class DetectTests(unittest.TestCase):
    def test_hedges_and_positions(self):
        f = detect("Line one.\nThis may possibly work.")
        self.assertEqual([(x.line, x.col, x.match) for x in f if x.category == "hedge"],
                         [(2, 6, "may"), (2, 10, "possibly")])

    def test_weasel_and_intensifier(self):
        c = cats("Many researchers agree this is very obviously true.", categories=("weasel", "intensifier"))
        self.assertEqual(c, [("weasel", "many researchers"), ("intensifier", "very"), ("intensifier", "obviously")])

    def test_statistical_significance_not_flagged(self):
        self.assertEqual(cats("Groups were significantly different.", categories=("intensifier",)), [])
        self.assertEqual(len(cats("This is significantly important.", categories=("intensifier",))), 1)

    def test_longest_filler_wins(self):
        f = [x for x in detect("We failed due to the fact that it rained.") if x.category == "filler"]
        self.assertEqual([(x.match, x.suggestion) for x in f], [("due to the fact that", "-> because")])

    def test_passive_voice(self):
        f = [x for x in detect("Samples were collected by the team. Data was carefully analyzed. The results "
                               "are shown.", ("passive",))]
        self.assertEqual([x.match for x in f], ["were collected by", "was carefully analyzed", "are shown"])
        self.assertIn("agent given", f[0].suggestion)

    def test_latex_masked(self):
        self.assertEqual(cats(r"\cite{may2020} $x may y$ % this may be hidden"), [])

    def test_summary_and_cli(self):
        text = "It may work. In order to test it, it was tested."
        s = summarize(detect(text), text)
        self.assertEqual(s["counts"], {"hedge": 1, "filler": 1, "passive": 1})
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "t.md")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(text)
            with redirect_stdout(io.StringIO()) as buf:
                main([p, "-c", "filler"])
            self.assertIn("[filler] 'In order to' - -> to", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
