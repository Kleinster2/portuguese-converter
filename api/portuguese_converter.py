#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import traceback
import io

def apply_phonetic_rules(word):
    """
    Apply Portuguese phonetic rules to transform a word.
    There are 9 main rules here:
      1) Final unstressed vowels often reduce ('o'->'u', 'os'->'us', etc.)
      2) 's' between vowels becomes 'z'
      3) 'ão' at the end becomes 'aum'
      4) 'lh' => 'ly'
      5) Final 'l' => 'u'
      6) Common verb endings (ar -> á, er -> ê, ir -> í)
      7) Common reductions (está->tá, para->pra, você->cê)
      8) Nasalization (final 'm' -> 'n', etc.)
      9) Vowel raising in unstressed syllables
    """
    if not word:
        return word
        
    word = word.lower()
    
    # Rule 1: Final unstressed vowels often reduce
    if len(word) > 1:
        word = re.sub(r'o$', 'u', word)   # final 'o' => 'u'
        word = re.sub(r'os$', 'us', word) # final 'os' => 'us'
        word = re.sub(r'e$', 'i', word)   # final 'e' => 'i'
        word = re.sub(r'es$', 'is', word) # final 'es' => 'is'
    
    # Rule 2: 's' between vowels becomes 'z'
    word = re.sub(
        r'([aeiouáéíóúâêîôûãẽĩõũ])s([aeiouáéíóúâêîôûãẽĩõũ])', 
        r'\1z\2', 
        word
    )
    
    # Rule 3: 'ão' becomes 'aum' at the end of words
    word = re.sub(r'ão$', 'aum', word)
    
    # Rule 4: 'lh' => 'ly'
    word = word.replace('lh', 'ly')
    
    # Rule 5: Final 'l' => 'u'
    word = re.sub(r'l$', 'u', word)
    
    # Rule 6: Common verb endings
    if len(word) > 2:
        if word.endswith('ar'):
            word = word[:-2] + 'á'
        elif word.endswith('er'):
            word = word[:-2] + 'ê'
        elif word.endswith('ir'):
            word = word[:-2] + 'í'
            
    # Rule 7: Common reductions
    word = re.sub(r'^está', 'tá', word)
    word = re.sub(r'^para', 'pra', word)
    word = re.sub(r'^você', 'cê', word)
    
    # Rule 8: Nasalization
    word = re.sub(r'm$', 'n', word)  # final 'm' => 'n'
    word = re.sub(r'([aeiou])m([pbfv])', r'\1n\2', word)
    
    # Rule 9: Vowel raising in unstressed syllables (if no stressed vowels)
    if len(word) > 2:
        if not any(c in word for c in 'áéíóúâêîôûãẽĩõũ'):
            word = re.sub(r'o([^aeiouáéíóúâêîôûãẽĩõũ]+)', r'u\1', word)
            word = re.sub(r'e([^aeiouáéíóúâêîôûãẽĩõũ]+)', r'i\1', word)
    
    return word

def preserve_capital(original, transformed):
    """
    Preserve capitalization from the original word in the transformed word.
    If the original starts with uppercase, transform the new word similarly.
    """
    if not original or not transformed:
        return transformed
    if original[0].isupper():
        return transformed[0].upper() + transformed[1:]
    return transformed

def handle_vowel_combination(first, second):
    """
    Handle vowel combinations between words according to Portuguese pronunciation rules.
    There are 2 main checks:
      1) If the first ends in a vowel and the second starts with the same vowel => merge
      2) If first ends in 'a' or 'o' and second starts with 'e' => merge with 'i'
    """
    if not first or not second:
        return first, second
    
    # Rule 1: Merge same vowel
    if (first[-1] in 'aeiouáéíóúâêîôûãẽĩõũ'
        and second[0] in 'aeiouáéíóúâêîôûãẽĩõũ'
        and first[-1].lower() == second[0].lower()):
        return first + second[1:], ''
    
    # Rule 2: If first ends in 'a' or 'o' and second starts with an unstressed 'e'
    if first[-1] in 'ao' and second.startswith('e'):
        return first + 'i' + second[1:], ''
    
    return first, second

def tokenize_text(text):
    """
    Split text into a list of (word, punct) pairs via a single pass:
      - If token is punctuation: ( '', punctuation )
      - If token is a word: ( word, '' )
    Regex: ([.,!?;:]) => punctuation 
           ([A-Za-zÀ-ÖØ-öø-ÿ0-9]+) => word with possible accents/digits
    """
    pattern = r'([.,!?;:])|([A-Za-zÀ-ÖØ-öø-ÿ0-9]+)'
    tokens = []
    
    for match in re.finditer(pattern, text):
        punct = match.group(1)
        word  = match.group(2)
        if punct:  
            # purely punctuation
            tokens.append(('', punct))
        elif word:
            # purely word
            tokens.append((word, ''))
    
    return tokens

def transform_text(text):
    """
    Transform text while properly handling punctuation, capitalization, 
    and vowel-combination rules.
    Steps in total:
      1) Tokenize via single-pass 'tokenize_text'.
      2) Apply 'apply_phonetic_rules' + 'preserve_capital' to each word token.
      3) Attempt to merge vowel combinations across adjacent tokens.
      4) Reconstruct the final string with minimal extra spaces.
    """
    try:
        # 1) Tokenize
        tokens = tokenize_text(text)
        
        # 2) Apply phonetic rules + preserve capitalization
        transformed_tokens = []
        for (word, punct) in tokens:
            if word:
                new_word = apply_phonetic_rules(word)
                new_word = preserve_capital(word, new_word)
                transformed_tokens.append((new_word, punct))
            else:
                # purely punctuation
                transformed_tokens.append((word, punct))
        
        # 3) Handle possible vowel merges
        final_tokens = []
        i = 0
        while i < len(transformed_tokens):
            if i < len(transformed_tokens) - 1:
                curr_word, curr_punct = transformed_tokens[i]
                next_word, next_punct = transformed_tokens[i + 1]
                
                # Merge only if both tokens contain words
                if curr_word and next_word:
                    merged, leftover = handle_vowel_combination(curr_word, next_word)
                    if leftover == '':
                        # They merged, combine punctuation
                        final_tokens.append((merged, curr_punct + next_punct))
                        i += 2
                        continue
                # If no merge happened, just append
                final_tokens.append((curr_word, curr_punct))
                i += 1
            else:
                # last token
                final_tokens.append(transformed_tokens[i])
                i += 1
        
        # 4) Reconstruct final string
        output_parts = []
        for w, p in final_tokens:
            if w:
                output_parts.append(w)
            if p:
                output_parts.append(p)
        
        # Join with spaces, then remove spaces before punctuation
        text_with_spaces = ' '.join(output_parts)
        result = re.sub(r'\s+([.,!?;:])', r'\1', text_with_spaces).strip()
        
        return result
        
    except Exception as e:
        print(f"Error in transform_text: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return ""

def convert_text(text):
    """Convert Portuguese text to its phonetic representation."""
    return transform_text(text)

def main():
    # Set UTF-8 encoding for stdout
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == "__main__":
    main()
