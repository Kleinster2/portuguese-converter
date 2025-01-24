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

# Test each word pair with different forms
test_word_pair("por que")  # Plain form
test_word_pair("por quê")  # With circumflex
test_word_pair("por que\u0302")  # With combining circumflex (U+0302)
test_word_pair("por\u00A0quê")  # With non-breaking space (U+00A0)
