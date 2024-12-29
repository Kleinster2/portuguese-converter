#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import traceback
import io

# Pre-defined phonetic transformations that bypass regular rules
PHONETIC_DICTIONARY = {
    'muito': 'muyntu',
    'muitos': 'muyntus',
    'muita': 'muynta',
    'muitas': 'muyntas',
    'mais': 'máys',
    'mas': 'máys',
    'então': 'entãum',
    'não': 'nãum',
    'bem': 'beyn',
    'também': 'tãmbêyn',
    'último': 'útimu',
    'última': 'útima',
    'últimos': 'útimus',
    'últimas': 'útimas',
    'quem': 'kêyn',
    'sempre': 'seynpri',
    'juntos': 'juntu',
    'atrás': 'atráyz',
    'com' : 'cum',
    'vamos' : 'vam',
    'eli' : 'êli',
    'ela' :'éla',
    'à' : 'a',
    'às' : 'as',
    'e' : 'y'
}

def apply_phonetic_rules(word):
    """
    Apply Portuguese phonetic rules to transform a word.
    First checks a dictionary of pre-defined transformations,
    if not found, applies the rules in sequence.
    
    Rules Rule 1p - Rule 10p:

    Rule 1p: Final unstressed vowels reduce ('o'->'u', 'os'->'us', etc.)
    Rule 2p: Vowel raising in unstressed syllables
    Rule 3p: 'ão' at the end becomes 'aum'
    Rule 4p: 's' between vowels becomes 'z'
    Rule 5p: 'lh' => 'ly'
    Rule 6p: Final 'l' => 'u'
    Rule 7p: Final 'm' => 'n' (nasalization)
    Rule 8p: Verb endings (ar -> á, er -> ê, ir -> í)
    Rule 9p: Common reductions (está->tá, para->pra, você->cê)
    Rule 10p: Remove initial 'h' (hoje->oje, homem->omem)
    """
    if not word:
        return word
        
    word = word.lower()
    
    # Check dictionary first
    if word in PHONETIC_DICTIONARY:
        return PHONETIC_DICTIONARY[word]
    
    # If not in dictionary, apply rules in sequence
    # Rule 1p
    word = re.sub(r'o$', 'u', word)   # final 'o' => 'u'
    if len(word) > 1:  # Only check length for plural endings
        word = re.sub(r'os$', 'us', word) # final 'os' => 'us'
        word = re.sub(r'e$', 'i', word)   # final 'e' => 'i'
        word = re.sub(r'es$', 'is', word) # final 'es' => 'is'
    
    # Rule 4p
    word = re.sub(
        r'([aeiouáéíóúâêîôûãẽĩõũy])s([aeiouáéíóúâêîôûãẽĩõũy])', 
        r'\1z\2', 
        word
    )
    
    # Rule 3p
    word = re.sub(r'ão$', 'aum', word)
    
    # Rule 5p
    word = word.replace('lh', 'ly')
    
    # Rule 6p
    word = re.sub(r'l$', 'u', word)
    
    # Rule 8p
    if len(word) > 2:
        if word.endswith('ar'):
            word = word[:-2] + 'á'
        elif word.endswith('er'):
            word = word[:-2] + 'ê'
        elif word.endswith('ir'):
            word = word[:-2] + 'í'
            
    # Rule 9p
    word = re.sub(r'^está', 'tá', word)
    word = re.sub(r'^para', 'pra', word)
    word = re.sub(r'^você', 'cê', word)
    
    # Rule 10p
    if word.startswith('h'):
        word = word[1:]
    
    # Rule 7p
    # word = re.sub(r'm$', 'ym', word)  # final 'm' => 'n'
    word = re.sub(r'([aeiou])m([pbfv])', r'\1ym\2', word)
    
    # Rule 2p
    # Commented out to prevent over-transformation
    # if len(word) > 2:
    #     if not any(c in word for c in 'áéíóúâêîôûãẽĩõũy'):
    #         word = re.sub(r'o([^aeiouáéíóúâêîôûãẽĩõũy]+)', r'u\1', word)
    #         word = re.sub(r'e([^aeiouáéíóúâêîôûãẽĩõũy]+)', r'i\1', word)
    
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
    Rules Rule 1c - Rule 5c:

    Rule 1c: If the first ends in a vowel and the second starts with the same vowel => merge
    Rule 2c: If first ends in 'a' or 'o' and second starts with 'e' => merge with 'i'
    Rule 3c: If first ends in 'a' and second starts with vowel
    Rule 4c: If first ends in 'u' and second starts with vowel => add 'w' between
    Rule 5c: All other vowel combinations - just stitch them together
    """
    if not first or not second:
        return first, second
    
    # Rule 1c
    if (first[-1] in 'aeiouáéíóúâêîôûãẽĩõũy'
        and second[0] in 'aeiouáéíóúâêîôûãẽĩõũy'
        and first[-1].lower() == second[0].lower()):
        return first + second[1:], ''
    
    # Rule 2c
    # if first[-1] in 'ao' and second.startswith('e'):
    #     return first + 'i' + second[1:], ''
    
    # Rule 3c
    if first[-1] == 'a' and second[0] in 'eiouáéíóúâêîôûãẽĩõũy':
        return first[:-1] + second, ''

    # Rule 4c
    if first[-1] == 'u' and second[0] in 'aeiouáéíóúâêîôûãẽĩõũy':
        return first + 'w' + second, ''

    # Rule 5c
    if first[-1] in 'eiouáéíóúâêîôûãẽĩõũy' and second[0] in 'aeiouáéíóúâêîôûãẽĩõũy':
        return first + second, ''

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
