"""Deterministic toy corpus shared by lab-01 and lab-02.

The corpus is generated from a small template grammar plus lexical noise, so
that a trigram model sees many unseen contexts at test time (the situation
Chapter 3 uses to motivate smoothing). Tokenisation is already done: each
sentence is a list of tokens that includes the boundary symbols <s> and </s>.
"""

import random

SUBJECTS = ["i", "you", "we", "they", "the man", "the woman", "my friend", "the student"]
VERBS = ["want", "need", "like", "see", "buy", "eat", "find", "know"]
OBJECTS = ["food", "coffee", "books", "tickets", "the menu", "a table",
           "green eggs", "ham", "chinese food", "english food", "lunch", "breakfast"]
PLACES = ["here", "there", "downtown", "near the station", "on main street"]
TIMES = ["today", "tomorrow", "at noon", "tonight"]

TEMPLATES = [
    "{s} {v} {o}",
    "{s} {v} {o} {t}",
    "{s} do not {v} {o}",
    "{s} would like {o} {t}",
    "can you tell me where to find {o}",
    "i am looking for {o} {p}",
    "what time does {o} open {t}",
    "do you know a good place for {o}",
    "{s} and {s2} {v} {o} {p}",
    "please show me {o} {p}",
]


def _sentence(rng):
    tpl = rng.choice(TEMPLATES)
    text = tpl.format(
        s=rng.choice(SUBJECTS),
        s2=rng.choice(SUBJECTS),
        v=rng.choice(VERBS),
        o=rng.choice(OBJECTS),
        p=rng.choice(PLACES),
        t=rng.choice(TIMES),
    )
    return ["<s>"] + text.split() + ["</s>"]


def build_corpus(n_sentences=320, seed=7):
    """Return (train, dev, test) as lists of token lists (70/15/15 split)."""
    rng = random.Random(seed)
    sents = [_sentence(rng) for _ in range(n_sentences)]
    # A few hand-written sentences with unusual word orders: they make the
    # trigram model's zero counts visible without making the corpus artificial.
    sents += [
        "<s> the coffee here is good </s>".split(),
        "<s> i think the menu is small </s>".split(),
        "<s> we need a table for two </s>".split(),
        "<s> they know the woman near the station </s>".split(),
        "<s> you can find books downtown </s>".split(),
        "<s> the student would like green eggs tonight </s>".split(),
        "<s> do you like english food </s>".split(),
        "<s> i do not know the man </s>".split(),
    ]
    # Deduplicate: identical sentences in different splits would leak the test set.
    seen, unique = set(), []
    for s in sents:
        key = tuple(s)
        if key not in seen:
            seen.add(key)
            unique.append(s)
    sents = unique
    print(f"corpus: {len(sents)} unique sentences")
    rng.shuffle(sents)
    n = len(sents)
    n_train = int(n * 0.70)
    n_dev = int(n * 0.15)
    train = sents[:n_train]
    dev = sents[n_train:n_train + n_dev]
    test = sents[n_train + n_dev:]
    assert not ({tuple(s) for s in train} & {tuple(s) for s in test}), "train/test overlap"
    assert not ({tuple(s) for s in train} & {tuple(s) for s in dev}), "train/dev overlap"
    assert not ({tuple(s) for s in dev} & {tuple(s) for s in test}), "dev/test overlap"
    return train, dev, test


if __name__ == "__main__":
    tr, dv, te = build_corpus()
    print(len(tr), len(dv), len(te))
    print(" ".join(tr[0]))
