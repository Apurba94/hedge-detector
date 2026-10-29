"""Rule-based style detector producing line/column findings."""
import re
from collections import Counter, namedtuple

Finding = namedtuple("Finding", "line col category match suggestion")

HEDGES = ["may", "might", "could", "possibly", "perhaps", "likely", "unlikely", "probably", "presumably",
          "apparently", "seems?", "seemed", "appears?", "appeared", "suggests?", "suggested", "tends? to",
          "somewhat", "relatively", "fairly", "rather", "to some extent", "in some cases",
          "it is (?:possible|plausible|conceivable) that", "arguably", "potentially"]
WEASELS = ["many (?:researchers|studies|scientists|authors)", "it is (?:widely|generally|commonly) (?:believed|accepted|known)",
           "some (?:researchers|studies|people) (?:argue|believe|suggest|say)", "experts (?:say|agree|believe)",
           "it has been (?:suggested|argued|shown)", "studies (?:show|have shown)", "research (?:shows|suggests)"]
INTENSIFIERS = ["very", "extremely", "highly", "really", "clearly", "obviously", "of course", "undoubtedly",
                "remarkably", "significantly(?! (?:different|higher|lower|greater|associated|correlated|more|less))",
                "dramatically", "truly", "absolutely", "completely", "totally", "novel", "groundbreaking"]
FILLERS = {
    "in order to": "to", "due to the fact that": "because", "a large number of": "many",
    "in the event that": "if", "at this point in time": "now", "has the ability to": "can",
    "it should be noted that": "(delete)", "it is important to note that": "(delete)",
    "it is worth noting that": "(delete)", "in spite of the fact that": "although",
    "with regard to": "about", "a majority of": "most", "the fact that": "that", "for the purpose of": "to",
    "is able to": "can", "in the case of": "for", "on the basis of": "based on", "prior to": "before",
    "subsequent to": "after", "utilize": "use", "utilization": "use", "facilitate": "help",
    "in close proximity": "near", "a number of": "several", "basically": "(delete)", "actually": "(delete)",
}
_BE = r"(?:is|are|was|were|be|been|being)"
_IRREGULAR = ("shown|known|seen|given|taken|done|made|found|chosen|written|drawn|grown|held|kept|left|lost|"
              "paid|put|read|run|set|sent|spent|told|thought|understood|built|bought|caught|brought|fed|led")
PASSIVE = re.compile(r"\b(%s)\s+(?:\w+ly\s+)?(\w+ed|%s)\b(\s+by\b)?" % (_BE, _IRREGULAR), re.I)

RULES = {
    "hedge": [(re.compile(r"\b%s\b" % h, re.I), "state the claim directly if the evidence supports it") for h in HEDGES],
    "weasel": [(re.compile(r"\b%s\b" % w, re.I), "cite specific sources") for w in WEASELS],
    "intensifier": [(re.compile(r"\b%s\b" % w, re.I), "let the data show the strength") for w in INTENSIFIERS],
    "filler": [(re.compile(r"\b%s\b" % re.escape(k), re.I), "-> " + v) for k, v in FILLERS.items()],
}


def _mask(text):
    """Blank out LaTeX comments, commands' arguments like \\cite{...}, math and code, keeping offsets."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"(?<!\\)%.*", blank, text)
    text = re.sub(r"\\(?:cite\w*|ref|label|eqref|url|begin|end|includegraphics)\s*(?:\[[^\]]*\])?\{[^}]*\}", blank, text)
    text = re.sub(r"\$[^$]*\$|`[^`]*`", blank, text)
    return text


def detect(text, categories=("hedge", "weasel", "intensifier", "filler", "passive")):
    masked = _mask(text)
    starts = [0] + [m.end() for m in re.finditer(r"\n", masked)]

    def loc(pos):
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1, pos - starts[lo] + 1

    found = []
    for cat in categories:
        if cat == "passive":
            for m in PASSIVE.finditer(masked):
                line, col = loc(m.start())
                tip = "agent given: try active voice" if m.group(3) else "consider active voice (who did it?)"
                found.append(Finding(line, col, "passive", m.group(0).strip(), tip))
            continue
        for rx, tip in RULES[cat]:
            for m in rx.finditer(masked):
                line, col = loc(m.start())
                found.append(Finding(line, col, cat, m.group(0), tip))
    # drop findings fully contained in a longer finding at the same place (e.g. 'the fact that' in 'due to the fact that')
    found.sort(key=lambda f: (f.line, f.col, -len(f.match)))
    out = []
    for f in found:
        if out and out[-1].line == f.line and out[-1].category == f.category and \
                out[-1].col <= f.col < out[-1].col + len(out[-1].match):
            continue
        out.append(f)
    return out


def summarize(findings, text):
    words = max(1, len(re.findall(r"\w+", text)))
    per = Counter(f.category for f in findings)
    top = Counter(f.match.lower() for f in findings).most_common(10)
    return {"words": words, "counts": dict(per), "per_1000_words": {k: round(1000 * v / words, 1) for k, v in per.items()},
            "most_frequent": top}
