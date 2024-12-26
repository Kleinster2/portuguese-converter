import re
import sys
import traceback

BYPASS_TRANSFORMATIONS = {
    # Quantity words
    "muito": "muyntu",
    "muitos": "muyintus",
    "muita": "muynta",
    "muitas": "muyntas",
    
    # Common conjunctions and prepositions
    "e": "y",
    "até": "té",
    "para": "pra",
    "ou": "ô",
    "mas": "maz",
    "mais": "mayz",
    "em": "in",
    "no": "nu",
    "na": "na",
    "nos": "nus",
    "nas": "nas",
    "do": "du",
    "da": "da",
    "dos": "dus",
    "das": "das",
    
    # Common verbs
    "está": "tá",
    "estão": "tão",
    "estou": "tô",
    "estava": "tava",
    "estavam": "tavam",
    "ser": "sê",
    "sou": "sô",
    
    # Common pronouns
    "você": "cê",
    "vocês": "cês",
    "ele": "eli",
    "ela": "ela",
    "eles": "elis",
    "elas": "elas",
    "mãe": "mãen",
    "mães": "mãens",
    
    # Numbers
    "dois": "doyz",
    "três": "trêyz",
    "seis": "seyz",
    "dez": "dêz",
    
    # Common nouns with 's' to 'z' transformation
    "casa": "caza",
    "mesa": "meza",
    "coisa": "coiza",
    "causa": "cauza",
    "fase": "fazi",
    "base": "bazi",
    "rosa": "roza",
    "caso": "cazu",
    "casos": "cazus",
    "meses": "mezis",
    
    # Common adjectives
    "bonito": "bunitu",
    "bonita": "bunita",
    "bonitos": "bunitus",
    "bonitas": "bunitas",
    "grande": "grandi",
    "grandes": "grandis",
    "pequeno": "pequenu",
    "pequenos": "pequenus",
    "pequena": "pequena",
    "pequenas": "pequenas"
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
            
        # Only combine if both tokens are non-empty and no punctuation between
        if prev_token and curr_token and not prev_punct:
            # Apply vowel combination rules
            combined = handle_vowel_combination(prev_token, curr_token)
            if combined != prev_token + curr_token:  # Only combine if there was a transformation
                result[-1] = (combined, curr_punct)
                continue
                
        # If no combination occurred, add as separate token
        result.append((curr_token, curr_punct))
        
    return result

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
    try:
        if not clean_tokens:
            print("No tokens to transform", file=sys.stderr)
            return []
        
        print(f"Starting transformation of tokens: {clean_tokens}", file=sys.stderr)
        
        # Transform the words first
        merged_tokens = apply_initial_transformations(clean_tokens)
        print(f"After initial transformations: {merged_tokens}", file=sys.stderr)
        
        updated_tokens = process_token_sequence(merged_tokens)
        print(f"After token sequence processing: {updated_tokens}", file=sys.stderr)
        
        updated_tokens = [final_endings_change(token) for token in updated_tokens]
        print(f"After final endings change: {updated_tokens}", file=sys.stderr)
        
        # Do one pass of stitching with empty punctuation
        final_stitch = stitch_tokens([(token, '') for token in updated_tokens])
        print(f"After stitching: {final_stitch}", file=sys.stderr)
        
        # Get just the transformed words
        final_output = [token for token, _ in final_stitch]
        
        # Preserve capitalization only for the first word if it matches
        if final_output and clean_tokens:
            final_output[0] = preserve_capital(clean_tokens[0], final_output[0])
            print(f"After preserving capitalization: {final_output}", file=sys.stderr)
        
        print(f"Final output: {final_output}", file=sys.stderr)
        return final_output
        
    except Exception as e:
        print(f"Error in transform_tokens: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise

def apply_initial_transformations(clean_tokens):
    """Apply initial transformations to tokens."""
    transformed = []
    for token in clean_tokens:
        lower_token = token.lower()
        print(f"Processing token: {token} (lower: {lower_token})", file=sys.stderr)
        if lower_token in BYPASS_TRANSFORMATIONS:
            transformed_token = BYPASS_TRANSFORMATIONS[lower_token]
            print(f"Found bypass transformation: {lower_token} -> {transformed_token}", file=sys.stderr)
            # Preserve capitalization
            if token[0].isupper():
                transformed_token = transformed_token[0].upper() + transformed_token[1:]
                print(f"Preserved capitalization: {transformed_token}", file=sys.stderr)
            transformed.append(transformed_token)
        else:
            transformed_token = token
            print(f"No bypass transformation found for: {token}", file=sys.stderr)
            transformed.append(transformed_token)
    return transformed
