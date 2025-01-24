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

# Test each word pair with different Unicode forms
test_word_pair("por que")  # Plain form
test_word_pair("por quê")  # Precomposed form (U+00EA)
test_word_pair("por que\u0302")  # Decomposed form (e + U+0302)
