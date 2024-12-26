import re
import sys
import traceback

def apply_phonetic_rules(word):
    """Apply Portuguese phonetic rules to transform a word."""
    if not word:
        return word
        
    word = word.lower()
    
    # Rule 1: Final unstressed vowels often reduce
    if len(word) > 1:
        word = re.sub(r'o$', 'u', word)  # final 'o' becomes 'u'
        word = re.sub(r'os$', 'us', word)  # final 'os' becomes 'us'
        word = re.sub(r'e$', 'i', word)  # final 'e' becomes 'i'
        word = re.sub(r'es$', 'is', word)  # final 'es' becomes 'is'
    
    # Rule 2: 's' between vowels becomes 'z'
    word = re.sub(r'([aeiouáéíóúâêîôûãẽĩõũ])s([aeiouáéíóúâêîôûãẽĩõũ])', r'\1z\2', word)
    
    # Rule 3: 'ão' becomes 'aum' at the end of words
    word = re.sub(r'ão$', 'aum', word)
    
    # Rule 4: Simplify double letters
    word = re.sub(r'rr', 'r', word)
    word = re.sub(r'ss', 's', word)
    
    # Rule 5: Simplify common consonant clusters
    word = word.replace('nh', 'ny')
    word = word.replace('lh', 'ly')
    
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
    word = re.sub(r'm$', 'n', word)  # final 'm' becomes 'n'
    word = re.sub(r'([aeiou])m([pbfv])', r'\1n\2', word)  # 'm' before labial consonants becomes 'n'
    
    # Rule 9: Vowel raising in unstressed syllables
    if len(word) > 2:
        # Only if not already a stressed syllable
        if not any(c in word for c in 'áéíóúâêîôû'):
            word = re.sub(r'o([^aeiouáéíóúâêîôûãẽĩõũ]+)', r'u\1', word)
            word = re.sub(r'e([^aeiouáéíóúâêîôûãẽĩõũ]+)', r'i\1', word)
    
    return word

def tokenize_punct(text):
    """Split text into tokens, preserving punctuation as separate tokens."""
    # Add spaces around punctuation
    text = re.sub(r'([.,!?;:])', r' \1 ', text)
    # Split on whitespace
    tokens = text.split()
    # Group tokens with their punctuation
    token_pairs = []
    for token in tokens:
        if token in '.,!?;:':
            if token_pairs:
                token_pairs[-1] = (token_pairs[-1][0], token)
            else:
                token_pairs.append(('', token))
        else:
            token_pairs.append((token, ''))
    return token_pairs

def reattach_punct(token_pairs):
    """Reattach punctuation to tokens."""
    return [t + p for t, p in token_pairs]

def preserve_capital(original, transformed):
    """Preserve capitalization from original word in transformed word."""
    if not original or not transformed:
        return transformed
    if original[0].isupper():
        return transformed[0].upper() + transformed[1:]
    return transformed

def handle_vowel_combination(first, second):
    """Handle vowel combinations between words according to Portuguese pronunciation rules."""
    if not first or not second:
        return first, second
        
    # Rule 1: If first word ends in a vowel and second starts with the same vowel, merge them
    if (first[-1] in 'aeiouáéíóúâêîôûãẽĩõũ' and 
        second[0] in 'aeiouáéíóúâêîôûãẽĩõũ' and 
        first[-1].lower() == second[0].lower()):
        return first + second[1:], ''
        
    # Rule 2: If first word ends in 'a' or 'o' and second starts with unstressed 'e', merge with 'i'
    if first[-1] in 'ao' and second.startswith('e'):
        return first + 'i' + second[1:], ''
        
    return first, second

def transform_tokens(clean_tokens):
    """Transform a list of tokens according to our rules."""
    try:
        if not clean_tokens:
            print("No tokens to transform", file=sys.stderr)
            return []
            
        print(f"Starting transformation of tokens: {clean_tokens}", file=sys.stderr)
        
        # Apply phonetic rules to each token
        transformed = []
        for token in clean_tokens:
            transformed_token = apply_phonetic_rules(token)
            transformed.append(transformed_token)
            print(f"Transformed {token} -> {transformed_token}", file=sys.stderr)
        
        # Handle vowel combinations between words
        final_tokens = []
        i = 0
        while i < len(transformed):
            if i < len(transformed) - 1:
                first, second = handle_vowel_combination(transformed[i], transformed[i + 1])
                if second:  # No combination occurred
                    final_tokens.append(first)
                    i += 1
                else:  # Combination occurred
                    final_tokens.append(first)
                    i += 2
            else:
                final_tokens.append(transformed[i])
                i += 1
        
        # Preserve capitalization of the first word
        if final_tokens and clean_tokens:
            final_tokens[0] = preserve_capital(clean_tokens[0], final_tokens[0])
        
        print(f"Final output: {final_tokens}", file=sys.stderr)
        return final_tokens
        
    except Exception as e:
        print(f"Error in transform_tokens: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise
