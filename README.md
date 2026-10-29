# hedge-detector

**A style checker for academic prose: flags hedges (`may`, `possibly`), weasel phrases
(`many researchers agree`), empty intensifiers (`very`, `clearly`), wordy fillers (`in order to`)
and passive voice, with line numbers and concrete suggestions.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Over-hedging makes findings sound weaker than the evidence; unsupported generalizations draw
reviewer criticism; fillers waste a word limit; stacked passives hide who did what. Grammar
checkers are cloud services that may not be allowed for unpublished work. This tool runs locally
on LaTeX, Markdown or text and is fully transparent: every rule is a readable regular expression.

## Features

- Five categories: `hedge`, `weasel`, `intensifier`, `filler` (with replacement), `passive`
  (distinguishes passives with an explicit agent, which convert easily to active voice)
- Does not flag statistical uses such as "significantly different"
- Ignores LaTeX comments, citation keys, labels, inline math and code spans
- Density per 1000 words to compare drafts or co-authors' sections; most frequent offenders
- JSON output for editor integrations

## Usage

```bash
pip install .
hedge-detector discussion.tex
hedge-detector paper.md -c filler -c weasel
hedge-detector paper.md --summary
```

Hedging is not always wrong: appropriate caution is part of good science. Use the report to
review each instance, not to delete them all.

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
