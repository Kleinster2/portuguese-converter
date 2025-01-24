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

# Test each word pair
test_word_pair("por que")
test_word_pair("por quê")
test_word_pair("com você")
test_word_pair("com voce")
