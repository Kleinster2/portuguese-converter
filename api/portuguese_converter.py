import re
import sys

BYPASS_TRANSFORMATIONS = {
    "muito": "muyntu",
    "muitos": "muyintus",
    "muita": "muynta",
    "muitas": "muyntas",
    "e": "y",
    "até": "té",
    "mãe": "mãen",
    "mães": "mãens",
    "ou": "ô",
    "você": "cê",
    "para": "pra",
    "está": "tá",
    "estão": "tão",
    "mais": "mayz",
    "mas": "maz",
    "dois": "doyz",
    "três": "trêyz",
    "seis": "seyz",
    "dez": "dêz",
    "casa": "caza",
    "mesa": "meza",
    "coisa": "coiza",
    "causa": "cauza",
    "fase": "fazi",
    "base": "bazi"
}

def s_between_vowels_to_z(word):
    """Change 's' to 'z' when it occurs between vowels."""
    return re.sub(r'([aeiouáéíóúâêîôûãẽĩõũ])s([aeiouáéíóúâêîôûãẽĩõũ])', r'\1z\2', word)

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

def is_verb(word):
    """Check if a word is likely a verb based on common verb endings."""
    word = word.lower()
    verb_endings = ['ar', 'er', 'ir', 'ou', 'am', 'em', 'iu']
    for ending in verb_endings:
        if word.endswith(ending):
            return True
    return False

def final_endings_change(word):
    """Change final endings according to common pronunciation patterns."""
    # First apply s-to-z transformation
    word = s_between_vowels_to_z(word)
    
    # Then apply other transformations
    replacements = {
        "os": "us", "o": "u", "es": "is", "e": "i", "l": "u"
    }
    lw = word.lower()
    for ending, replacement in replacements.items():
        if lw.endswith(ending) and len(word) > 1:
            word = word[: -len(ending)] + replacement
            break
    if "à" in word:
        word = word.replace("à", "a")
    if "lh" in word:
        word = word.replace("lh", "ly")
    if is_verb(word):
        if lw.endswith("ar"):
            word = word[:-2] + "á"
        elif lw.endswith("er"):
            word = word[:-2] + "ê"
        elif lw.endswith("ir"):
            word = word[:-2] + "í"
    if lw.startswith("h") and len(word) > 1:
        word = word[1:]
    return word

def apply_final_endings(tagged_list):
    """Apply final ending changes to a list of tagged tokens."""
    return [(final_endings_change(token), tag) for token, tag in tagged_list]

def merge_prepositions(tokens):
    """Merge prepositions with the following word according to common patterns."""
    if len(tokens) < 2:
        return tokens
        
    result = []
    i = 0
    while i < len(tokens):
        current = tokens[i].lower()
        
        # Check if we can look ahead
        if i + 1 < len(tokens):
            next_token = tokens[i + 1]
            
            # Handle preposition merging
            if current in ['de', 'do', 'da', 'em', 'no', 'na']:
                result.append(current + next_token)
                i += 2
                continue
                
        result.append(tokens[i])
        i += 1
        
    return result

def handle_vowel_combination(first: str, second: str) -> str:
    """Handle vowel combinations between words according to Portuguese pronunciation rules."""
    # Define vowel groups
    open_vowels = "aáâã"
    closed_vowels = "eéêiy"
    back_vowels = "oóôu"
    all_vowels = open_vowels + closed_vowels + back_vowels
    
    if not first or not second:
        return first + second
        
    first_lower = first.lower()
    second_lower = second.lower()
    
    # Only process if ending/starting with vowels
    if not (first_lower[-1] in all_vowels and second_lower[0] in all_vowels):
        return first + second
    
    last_vowel = first_lower[-1]
    first_vowel = second_lower[0]
    
    # Special case: word ending in 'ê' + word starting with 'é' -> drop 'ê'
    if last_vowel == 'ê' and first_vowel == 'é':
        return first[:-1] + second
    
    # Rule 1: Same vowels usually merge
    if last_vowel == first_vowel:
        return first[:-1] + second
        
    # Rule 2: 'a' + 'e/i' drops the 'a' but keeps second vowel
    if last_vowel in open_vowels and first_vowel in closed_vowels:
        return first[:-1] + second  # "casa escura" → "casescura", "fala isso" → "falisso"
        
    # Rule 3: 'e/i' + 'a' adds 'y'
    if last_vowel in closed_vowels and first_vowel in open_vowels:
        return first + 'y' + second
        
    # Rule 4: 'o/u' + 'a/e/i' adds 'w'
    if last_vowel in back_vowels and first_vowel in (open_vowels + closed_vowels):
        return first + 'w' + second
    
    # Rule 5: Keep both vowels in other cases (hiatus)
    return first + second

def stitch_tokens(token_tuples):
    """Stitch together tokens based on vowel combination rules."""
    if not token_tuples:
        return token_tuples
        
    result = [token_tuples[0]]
    
    for i in range(1, len(token_tuples)):
        prev_token, prev_punct = result[-1]
        curr_token, curr_punct = token_tuples[i]
        
        # Skip empty tokens
        if not curr_token:
            continue
            
        # If previous token ended with punctuation, start new token
        if prev_punct:
            result.append((curr_token, curr_punct))
            continue
            
        # Apply vowel combination rules
        combined = handle_vowel_combination(prev_token, curr_token)
        
        # Update the last token with the combined result
        result[-1] = (combined, curr_punct)
        
    return result

def apply_initial_transformations(clean_tokens):
    """Apply initial transformations to tokens."""
    transformed = []
    for token in clean_tokens:
        lower_token = token.lower()
        if lower_token in BYPASS_TRANSFORMATIONS:
            transformed_token = BYPASS_TRANSFORMATIONS[lower_token]
            # Preserve capitalization
            if token[0].isupper():
                transformed_token = transformed_token[0].upper() + transformed_token[1:]
            transformed.append(transformed_token)
        else:
            transformed.append(token)
    return transformed

def handle_special_pronouns(current_token, next_token, next_next_token):
    """Handle special cases with pronouns."""
    pronouns = {'me', 'te', 'se', 'lhe'}
    if current_token.lower() in pronouns:
        # If followed by a verb
        if next_token and is_verb(next_token):
            return current_token + next_token
        # If part of a chain like "me a"
        if next_token and next_token.lower() in {'o', 'a', 'os', 'as'}:
            if next_next_token and is_verb(next_next_token):
                return current_token + next_token + next_next_token
    return None

def handle_s_vowel_merge(current_token, next_token, vowels):
    """Handle cases where 's' becomes 'z' between vowels across words."""
    if current_token.endswith('s') and next_token and next_token[0].lower() in vowels:
        return current_token[:-1] + 'z' + next_token
    return None

def process_token_sequence(merged_tokens):
    """Process a sequence of tokens applying various transformation rules."""
    if not merged_tokens:
        return merged_tokens
        
    result = []
    i = 0
    vowels = set('aeiouáéíóúâêîôûãẽĩõũ')
    
    while i < len(merged_tokens):
        current = merged_tokens[i]
        next_token = merged_tokens[i + 1] if i + 1 < len(merged_tokens) else None
        next_next = merged_tokens[i + 2] if i + 2 < len(merged_tokens) else None
        
        # Try special pronoun handling
        special_form = handle_special_pronouns(current, next_token, next_next)
        if special_form:
            result.append(special_form)
            i += 3 if next_next else 2
            continue
            
        # Try s+vowel merge
        if next_token:
            merged = handle_s_vowel_merge(current, next_token, vowels)
            if merged:
                result.append(merged)
                i += 2
                continue
                
        # No special cases applied, add token as is
        result.append(current)
        i += 1
        
    return result

def transform_tokens(clean_tokens):
    """Transform a list of tokens according to our rules."""
    if not clean_tokens:
        return []
    
    print(f"Starting transformation of tokens: {clean_tokens}", file=sys.stderr)
    
    # Transform the words first
    merged_tokens = apply_initial_transformations(clean_tokens)
    print(f"After initial transformations: {merged_tokens}", file=sys.stderr)
    
    updated_tokens = process_token_sequence(merged_tokens)
    print(f"After token sequence processing: {updated_tokens}", file=sys.stderr)
    
    updated_tokens = [final_endings_change(token) for token in updated_tokens]
    print(f"After final endings change: {updated_tokens}", file=sys.stderr)
    
    # Do both passes of stitching
    first_stitch = stitch_tokens([(token, '') for token in updated_tokens])
    print(f"After first stitch: {first_stitch}", file=sys.stderr)
    
    final_stitch = stitch_tokens(first_stitch)
    print(f"After final stitch: {final_stitch}", file=sys.stderr)
    
    # Get just the transformed words
    final_output = [token for token, _ in final_stitch]
    
    # Preserve capitalization only for the first word if it matches
    if final_output and clean_tokens:
        final_output[0] = preserve_capital(clean_tokens[0], final_output[0])
    
    print(f"Final output: {final_output}", file=sys.stderr)
    return final_output
