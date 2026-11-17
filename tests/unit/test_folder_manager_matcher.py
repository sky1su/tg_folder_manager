import pytest
from tg_folder_manager.matcher import ChatMatcher

def test_matcher_exact_match():
    include = {"News": [".*news.*", "новости"]}
    exclude = {"News": ["spam"]}
    
    # Should match
    assert ChatMatcher.match_primary("Daily News", include, exclude) == "News"
    assert ChatMatcher.match_primary("новости дня", include, exclude) == "News"

def test_matcher_regex_match():
    include = {"Crypto": [r"bit\w*"]} # matches bitcoin, bitrate etc
    exclude = {}
    
    assert ChatMatcher.match_primary("Bitcoin price", include, exclude) == "Crypto"
    assert ChatMatcher.match_primary("Bitrate news", include, exclude) == "Crypto"

def test_matcher_exclusion_logic():
    include = {"News": [".*news.*"]}
    exclude = {"News": [".*spam.*"]}
    
    # Match
    assert ChatMatcher.match_primary("Good news", include, exclude) == "News"
    # Should NOT match due to exclusion
    assert ChatMatcher.match_primary("spam news", include, exclude) is None

def test_matcher_no_match():
    include = {"A": ["a"]}
    exclude = {}
    assert ChatMatcher.match_primary("z", include, exclude) is None

def test_matcher_case_insensitivity():
    include = {"A": ["NEWS"]}
    exclude = {}
    assert ChatMatcher.match_primary("news", include, exclude) == "A"
