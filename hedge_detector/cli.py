"""Command-line interface for hedge-detector."""
import argparse
import json

from .core import detect, summarize

CATS = ("hedge", "weasel", "intensifier", "filler", "passive")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hedge-detector", description="Flag hedges, weasel words, fillers and passive voice.")
    ap.add_argument("file")
    ap.add_argument("-c", "--category", action="append", choices=CATS, help="only these categories (repeatable)")
    ap.add_argument("--summary", action="store_true", help="only print the summary")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    with open(args.file, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    findings = detect(text, tuple(args.category or CATS))
    summ = summarize(findings, text)
    if args.json:
        print(json.dumps({"summary": summ, "findings": [f._asdict() for f in findings]}, indent=2))
        return 0
    if not args.summary:
        for f in findings:
            print("%s:%d:%d: [%s] '%s' - %s" % (args.file, f.line, f.col, f.category, f.match, f.suggestion))
    print("\n%d words. " % summ["words"] + ", ".join("%s: %d (%.1f/1000 words)" % (k, v, summ["per_1000_words"][k])
                                                    for k, v in sorted(summ["counts"].items())))
    if summ["most_frequent"]:
        print("Most frequent: " + ", ".join("%s x%d" % t for t in summ["most_frequent"][:5]))
    return 0
