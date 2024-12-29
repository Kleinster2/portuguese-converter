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
    
    # Rule 4: Transform 'lh' to 'ly'
    word = word.replace('lh', 'ly')
    
    # Rule 5: Final 'l' becomes 'u'
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
    """Split text into tokens, preserving punctuation as separate tokens.
    Returns a list of tuples (word, punctuation) where punctuation may be empty."""
    # Define all punctuation marks we handle
    PUNCT_MARKS = '.,!?;:'
    
    # Add spaces around punctuation for proper tokenization
    text = re.sub(f'([{PUNCT_MARKS}])', r' \1 ', text)
    
    # Split on whitespace
    tokens = text.split()
    
    # Group tokens with their punctuation
    token_pairs = []
    for token in tokens:
        if token in PUNCT_MARKS:
            if token_pairs:
                # Attach punctuation to previous token
                token_pairs[-1] = (token_pairs[-1][0], token)
            else:
                # Handle case where text starts with punctuation
                token_pairs.append(('', token))
        else:
            # Regular word without punctuation
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

def transform_tokens(token_pairs):
    """Transform a list of token pairs according to our rules.
    Each token pair is (word, punctuation)."""
    try:
        if not token_pairs:
            print("No tokens to transform", file=sys.stderr)
            return []
            
        print(f"Starting transformation of tokens: {token_pairs}", file=sys.stderr)
        
        # Apply phonetic rules to each word (not the punctuation)
        transformed_pairs = []
        for word, punct in token_pairs:
            transformed_word = apply_phonetic_rules(word)
            transformed_pairs.append((transformed_word, punct))
            print(f"Transformed {word} -> {transformed_word}", file=sys.stderr)
        
        # Handle vowel combinations between words
        final_pairs = []
        i = 0
        while i < len(transformed_pairs):
            if i < len(transformed_pairs) - 1:
                word1, punct1 = transformed_pairs[i]
                word2, punct2 = transformed_pairs[i + 1]
                
                combined_word, remaining = handle_vowel_combination(word1, word2)
                if remaining:  # No combination occurred
                    final_pairs.append((word1, punct1))
                    i += 1
                else:  # Combination occurred
                    # Keep punctuation from both words
                    final_pairs.append((combined_word, punct1 + punct2))
                    i += 2
            else:
                final_pairs.append(transformed_pairs[i])
                i += 1
        
        # Preserve capitalization of the first word
        if final_pairs and token_pairs:
            orig_word, orig_punct = token_pairs[0]
            transformed_word, transformed_punct = final_pairs[0]
            final_pairs[0] = (preserve_capital(orig_word, transformed_word), transformed_punct)
        
        # Reattach punctuation
        final_tokens = [word + punct for word, punct in final_pairs]
        
        print(f"Final output: {final_tokens}", file=sys.stderr)
        return final_tokens
        
    except Exception as e:
        print(f"Error in transform_tokens: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise

def convert_text(text):
    """Convert Portuguese text to its phonetic representation."""
    try:
        # Split text into tokens while preserving punctuation
        token_pairs = tokenize_punct(text)
        print(f"Tokenized into: {token_pairs}", file=sys.stderr)
        
        # Transform the tokens according to our rules
        transformed = transform_tokens(token_pairs)
        
        # Join the transformed tokens back into text
        result = ' '.join(transformed)
        return result
        
    except Exception as e:
        print(f"Error in convert_text: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise

def main():
    text = "Olá, como você está?"
    print(convert_text(text))

if __name__ == "__main__":
    main()
