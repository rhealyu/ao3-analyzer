# AO3 Analyzer

A small tool that scrapes an AO3 fic and tries to figure out who's on top. Built for fun, not science.

## What it does

Paste in an AO3 work URL, and it'll:
- Extract the main ship from the tags
- Scan the fic text for dominance/submission signals
- Spit out a verdict: who's TOP, who's not, or if they're switching

## How to run

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```

## Limitations (a lot of them)

This thing works on vibes and keyword matching, so take the results with a massive grain of salt. Some known issues:

- **Pronoun resolution is rough.** It tries to track "he/him" back to the right character but gets confused easily, especially in long fics or ones with similarly-gendered characters.
- **The lexicon is small and biased.** It was built with a specific type of fic in mind. If the author uses unusual phrasing or non-English words, the tool will probably miss it entirely.
- **No narrative context.** It can't tell if a DOM-coded action is a flashback, a dream, or being used ironically.
- **Only works on English fics.** Mostly. Kind of.
- **Short fics get weird results** because there's just not enough signal to work with.

## Want to make it better?

### Option 1: Expand the lexicon yourself

The easiest way. Open `lexicon.py` and add words to whichever category fits:

```python
"STRONG_DOM": {
    "your_word_here": 3,  # weight 1-3, higher = stronger signal
    ...
},
```

Categories available: `STRONG_DOM`, `MID_DOM`, `STRONG_SUB`, `MID_SUB`, `WEAK_SUB`, `POSITION_PHRASES`, `PHRASAL_VERBS`, `SWITCH_SIGNALS`.

If you read a lot of fic in a specific fandom or style, you'll probably notice patterns the current lexicon misses — just throw them in.

### Option 2: Train an actual model

If you want something smarter, you could replace the keyword-matching logic in `analyze()` with a proper classifier. A few approaches that could work:

- **Fine-tune a small BERT-style model** on labeled fic sentences (label = dom/sub/neutral). Even a few hundred examples would probably beat the current approach.
- **Use sentence embeddings** (e.g. `sentence-transformers`) to measure semantic similarity to prototypical dom/sub sentences instead of exact keyword matching.
- **GPT-based classification** — just prompt an LLM with the sentence and ask it to classify. Slower and costs money but requires zero training data.

If you go the training route, the hardest part is getting labeled data. One option: manually label a batch of sentences from fics you know well, since you already have intuitions about what reads as DOM vs SUB.

## Stack

- `streamlit` — UI
- `spacy` — dependency parsing for subject/object detection
- `beautifulsoup4` + `requests` — scraping AO3
- pure vibes — analysis logic

---

*Made for personal use. Please be responsible about scraping AO3 and follow their Terms of Service.*
