"""Targeted examples for the lint title heuristic (R1).

R1 is intentionally narrow: only the two anti-patterns the SKILL has
called out (gerund first word, all-caps tech token). These tests pin that
narrowness so the rule can't drift toward false positives.
"""

from __future__ import annotations

import pytest

from spears.lint import _check_title_verb


@pytest.mark.parametrize(
    "title",
    [
        "Prevent Abuse Attacks",
        "View Current Quota",
        "Sign In With Email",
        "Block Repeated Failed Attempts",
        "Export Account Activity",
    ],
)
def test_R1_passes_user_verb_titles(title):
    assert _check_title_verb(title) is None


@pytest.mark.parametrize(
    "title",
    [
        "Caching Strategy",
        "Logging Pipeline",
        "Streaming Updates",
    ],
)
def test_R1_flags_gerund_first_word(title):
    msg = _check_title_verb(title)
    assert msg is not None and "gerund" in msg, (title, msg)


@pytest.mark.parametrize(
    "title",
    [
        "Rate Limiting",
        "Cache Caching",
        "Token Validating",
    ],
)
def test_R1_flags_noun_phrase_with_gerund_second_word(title):
    msg = _check_title_verb(title)
    assert msg is not None and "noun phrase" in msg, (title, msg)


@pytest.mark.parametrize(
    "title",
    [
        "IP-Based Rate Limiting",
        "JWT Token Validation",
        "API Throttle",
        "URL Shortener",
    ],
)
def test_R1_flags_tech_token_prefix(title):
    msg = _check_title_verb(title)
    assert msg is not None and "tech token" in msg, (title, msg)


def test_R1_empty_title_is_flagged():
    assert _check_title_verb("") is not None
    assert _check_title_verb("   ") is not None


@pytest.mark.parametrize(
    "title",
    [
        # Words not on our verb allowlist but not matching either anti-
        # pattern. The heuristic stays silent rather than false-positive.
        "Quietly Refresh Tokens",
        "Smoothly Resume Playback",
    ],
)
def test_R1_unknown_first_word_does_not_false_positive(title):
    assert _check_title_verb(title) is None
