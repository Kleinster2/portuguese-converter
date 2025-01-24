#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import portuguese_converter

def test_word_pair(text):
    print(f"\nTesting: {text}")
    print("-" * 40)
    result = portuguese_converter.convert_text(text)
    print(f"Original: {result['original']}")
    print(f"Before:   {result['before']}")
    print(f"After:    {result['after']}")
    print("\nExplanations:")
    for exp in result['explanations']:
        print(f"  - {exp}")
    print("\nCombinations:")
    for comb in result['combinations']:
        print(f"  - {comb}")
    print("-" * 40)

# Test with various accent patterns
test_word_pair("por que")  # No accents
test_word_pair("por quê")  # With circumflex (precomposed)
test_word_pair("por que\u0302")  # With combining circumflex
test_word_pair("por\u00A0quê")  # With non-breaking space
test_word_pair("POR QUÊ")  # All caps with accent
test_word_pair("Por Quê")  # Title case with accent
