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
        if not any(c in word for c in 'áéíóúâêîôûãẽĩõũ'):
            word = re.sub(r'o([^aeiouáéíóúâêîôûãẽĩõũ]+)', r'u\1', word)
            word = re.sub(r'e([^aeiouáéíóúâêîôûãẽĩõũ]+)', r'i\1', word)
    
    return word

def tokenize_text(text):
    """Split text into word tokens and punctuation, preserving their order."""
    # Define punctuation pattern
    punct_pattern = r'([.,!?;:])'
    
    # Split on punctuation, keeping the punctuation marks
    parts = re.split(f'({punct_pattern})', text)
    
    # Group into tokens
    tokens = []
    current_word = ''
    current_punct = ''
    
    for part in parts:
        if re.match(punct_pattern, part):
            current_punct += part
        else:
            # Handle whitespace-separated words
            words = part.split()
            for i, word in enumerate(words):
                if i > 0:  # If not the first word, store previous
                    tokens.append((current_word, current_punct))
                    current_word = ''
                    current_punct = ''
                current_word = word
            
            if not words:  # If part was just spaces
                if current_word:  # Store accumulated word if exists
                    tokens.append((current_word, current_punct))
                    current_word = ''
                    current_punct = ''
    
    # Don't forget the last token
    if current_word or current_punct:
        tokens.append((current_word, current_punct))
    
    return tokens

def transform_text(text):
    """Transform text while properly handling punctuation."""
    try:
        # Split into tokens with punctuation
        tokens = tokenize_text(text)
        
        # Transform each word token
        transformed_tokens = []
        for word, punct in tokens:
            if word:  # Only transform non-empty words
                transformed_word = apply_phonetic_rules(word)
                transformed_word = preserve_capital(word, transformed_word)
                transformed_tokens.append((transformed_word, punct))
            elif punct:  # Preserve standalone punctuation
                transformed_tokens.append(('', punct))
        
        # Handle vowel combinations between words
        final_tokens = []
        i = 0
        while i < len(transformed_tokens):
            if i < len(transformed_tokens) - 1:
                curr_word, curr_punct = transformed_tokens[i]
                next_word, next_punct = transformed_tokens[i + 1]
                
                combined_word, remaining = handle_vowel_combination(curr_word, next_word)
                
                if remaining:  # No combination occurred
                    final_tokens.append((curr_word, curr_punct))
                    i += 1
                else:  # Combination occurred
                    final_tokens.append((combined_word, curr_punct + next_punct))
                    i += 2
            else:
                final_tokens.append(transformed_tokens[i])
                i += 1
        
        # Reconstruct text with proper spacing and punctuation
        result = []
        for word, punct in final_tokens:
            if word:
                result.append(word)
            if punct:
                result.append(punct)
        
        return ' '.join(result).strip()
        
    except Exception as e:
        print(f"Error in transform_text: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise

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

def convert_text(text):
    """Convert Portuguese text to its phonetic representation."""
    return transform_text(text)

def main():
    text = "Olá, como você está?"
    print(convert_text(text))

if __name__ == "__main__":
    main()
