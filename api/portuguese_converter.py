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
    'sempre': 'seynpri',
    'juntos': 'juntu',
    'atrás': 'atráyz',
    'com' : 'cum',
    'vamos' : 'vam',
    'eli' : 'êli',
    'ela' :'éla',
    'à' : 'a',
    'às' : 'as',
    'e' : 'y',
    'seu' : 'teu',
    'seus' : 'teus',
    'sua' : 'tua',
    'suas' : 'tuas',
    'desculpa' : 'discupa',
    'desculpas' : 'discupas',
    'depois' : 'dipois',
    'por' : 'pur',
    'vou' : 'vô',
    'neste' : 'nessi',
    'nesta' : 'nessa',
    'nestes' : 'nessis',
    'nestas' : 'nessas',
    'empresa' : 'impreza',
    'empresas' : 'imprezas',
    'algum' : 'augum',
    'alguns' : 'auguns',
    'alguma' : 'auguma',
    'algumas' : 'augumas',
    'qualquer' : 'kuauké',
    'quaisquer' : 'kuauké',
    'porque' : 'purkê',
    'porquê' : 'purkê',
    'quem' : 'kêyn',
    'qual' : 'kuau',
    'quais' : 'kuais',
    'que' : 'ki',
    'teatro' : 'tiatru',
    'teatros' : 'tiatrus',
    'facebook' : 'faicibuki',
    'internet' : 'interneti',
    'app' : 'épi',
    'apps' : 'épis'
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
    
    # Store original word for capitalization check
    original = word
    word = word.lower()
    
    print(f"Checking dictionary for: '{word}'")  
    # Check dictionary with lowercase word
    if word in PHONETIC_DICTIONARY:
        print(f"Found in dictionary: '{word}' -> '{PHONETIC_DICTIONARY[word]}'")  
        transformed = PHONETIC_DICTIONARY[word]
        # Preserve original capitalization
        return preserve_capital(original, transformed)
    else:
        print(f"Not found in dictionary: '{word}'")  
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

        word = re.sub(r'qui', 'ki', word)
        word = re.sub(r'que', 'ke', word)
        
        # Rule 7p
        # word = re.sub(r'm$', 'ym', word)  # final 'm' => 'n'
        # word = re.sub(r'([aeiou])m([pbfv])', r'\1ym\2', word)
        
        # Rule 7p - Nasal vowel combinations
        word = re.sub(r'am$', 'ãum', word)  # final 'am' -> 'ãum'
        word = re.sub(r'em$', 'eyn', word)  # final 'em' -> 'eyn'
        word = re.sub(r'im$', 'in', word)   # final 'im' -> 'in'
        word = re.sub(r'om$', 'oun', word)  # final 'om' -> 'oun'
        word = re.sub(r'um$', 'un', word)   # final 'um' -> 'un'
        
        # Rule 2p
        # Commented out to prevent over-transformation
        # if len(word) > 2:
        #     if not any(c in word for c in 'áéíóúâêîôûãẽĩõũy'):
        #         word = re.sub(r'o([^aeiouáéíóúâêîôûãẽĩõũy]+)', r'u\1', word)
        #         word = re.sub(r'e([^aeiouáéíóúâêîôûãẽĩõũy]+)', r'i\1', word)
        
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
        
        # Preserve original capitalization
        return preserve_capital(original, word)

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
    Rules Rule 1c - Rule 6c:

    Rule 1c: If the first ends in a vowel and the second starts with the same vowel => merge
    Rule 2c: If first ends in 'a' or 'o' and second starts with 'e' => merge with 'i'
    Rule 3c: If first ends in 'a' and second starts with vowel
    Rule 4c: If first ends in 'u' and second starts with vowel => add 'w' between
    Rule 5c: All other vowel combinations - just stitch them together
    Rule 6c: If first ends in 's' or 'z' and second starts with vowel => merge and use 'z'
    """
    if not first or not second:
        return first, second
        
    # Don't combine if result would be too long
    MAX_COMBINED_LENGTH = 12
    if len(first) + len(second) > MAX_COMBINED_LENGTH:
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

    # Rule 6c
    if first[-1] in 'sz' and second[0] in 'aeiouáéíóúâêîôûãẽĩõũy':
        return first[:-1] + 'z' + second, ''

    # Rule 5c
    if first[-1] in 'eiouáéíóúâêîôûãẽĩõũy' and second[0] in 'aeiouáéíóúâêîôûãẽĩõũy':
        return first + second, ''

    return first, second

def tokenize_text(text):
    """
    Capture words vs. punctuation lumps in a single pass.
    - ([A-Za-zÀ-ÖØ-öø-ÿ0-9]+): words (including accented or numeric characters).
    - ([.,!?;:]+): one or more punctuation marks.
    Returns a list of (word, punct) tuples, e.g.:
        "Olá, mundo!" => [("Olá", ""), ("", ","), ("mundo", ""), ("", "!")]
    """
    pattern = r'([A-Za-zÀ-ÖØ-öø-ÿ0-9]+)|([.,!?;:]+)'
    tokens = []
    
    for match in re.finditer(pattern, text):
        word = match.group(1)
        punct = match.group(2)
        if word:
            tokens.append((word, ''))     # (word, "")
        elif punct:
            tokens.append(('', punct))    # ("", punctuation)
    
    return tokens

def reassemble_tokens_smartly(final_tokens):
    """
    Reassemble (word, punct) tokens into a single string without
    introducing extra spaces before punctuation.
    
    Example final_tokens could be: [("Olá", ""), ("", ","), ("mundo", ""), ("", "!")]
    We want to get: "Olá, mundo!"
    
    Logic:
      - If 'word' is non-empty, append it to output (with a leading space if it's not the first).
      - If 'punct' is non-empty, append it directly (no leading space).
    """
    output = []
    for (word, punct) in final_tokens:
        # If there's a word
        if word:
            if not output:
                # First token => add the word as is
                output.append(word)
            else:
                # Not the first => prepend space before the word
                output.append(" " + word)
        
        # If there's punctuation => attach immediately (no space)
        if punct:
            output.append(punct)
    
    # Join everything into a single string
    return "".join(output)

def transform_text(text):
    """
    Transform the input text using phonetic rules,
    handle cross-word vowel combinations in multiple passes,
    then reassemble with no extra spaces around punctuation.
    """
    if not text:
        return text
    
    try:
        # 1) Tokenize => separate words and punctuation
        tokens = tokenize_text(text)
        
        # 2) Apply phonetic rules to word tokens
        transformed_tokens = []
        for (word, punct) in tokens:
            if word:
                new_word = apply_phonetic_rules(word)
                new_word = preserve_capital(word, new_word)
                transformed_tokens.append((new_word, punct))
            else:
                transformed_tokens.append((word, punct))
        
        # 3) First pass: handle vowel combos between adjacent words
        result_tokens = []
        i = 0
        while i < len(transformed_tokens):
            if i == len(transformed_tokens) - 1:
                result_tokens.append(transformed_tokens[i])
                break
            
            first_word, first_punct = transformed_tokens[i]
            second_word, second_punct = transformed_tokens[i + 1]
            
            # Only merge if both are real words
            if first_word and second_word:
                merged_first, merged_second = handle_vowel_combination(first_word, second_word)
                if merged_second == '':
                    # a merge occurred => skip the second token
                    result_tokens.append((merged_first, second_punct))
                    i += 2
                else:
                    # no merge
                    result_tokens.append((merged_first, first_punct))
                    i += 1
            else:
                result_tokens.append((first_word, first_punct))
                i += 1
        
        # 4) Second pass: catch merges that might appear after first pass
        final_tokens = []
        i = 0
        while i < len(result_tokens):
            if i == len(result_tokens) - 1:
                final_tokens.append(result_tokens[i])
                break
            
            first_word, first_punct = result_tokens[i]
            second_word, second_punct = result_tokens[i + 1]
            
            if first_word and second_word:
                merged_first, merged_second = handle_vowel_combination(first_word, second_word)
                if merged_second == '':
                    final_tokens.append((merged_first, second_punct))
                    i += 2
                else:
                    final_tokens.append((merged_first, first_punct))
                    i += 1
            else:
                final_tokens.append((first_word, first_punct))
                i += 1
        
        # 5) Reassemble without extra spaces around punctuation
        return reassemble_tokens_smartly(final_tokens)
    
    except Exception as e:
        print(f"Error transforming text: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return text

def convert_text(text):
    """Convert Portuguese text to its phonetic representation."""
    return transform_text(text)

def main():
    # Set UTF-8 encoding for stdout
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == "__main__":
    main()
