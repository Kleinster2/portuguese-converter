#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import traceback
import io

# Pre-defined phonetic transformations that bypass regular rules
PHONETIC_DICTIONARY = {
    # Pronouns and Articles
    'algum': 'augum',
    'alguma': 'auguma',
    'algumas': 'augumas',
    'alguns': 'auguns',
    'ela': 'éla',
    'elas': 'élas',
    'ele': 'éli',
    'eles': 'élis',
    'eli': 'êli',
    'essa': 'essa',
    'essas': 'essas',
    'esse': 'essi',
    'esses': 'essis',
    'esta': 'esta',
    'estas': 'estas',
    'este': 'esti',
    'estes': 'estis',
    'eu': 'eu',
    'meu': 'meu',
    'minha': 'minya',
    'nesta': 'nessa',
    'nestas': 'nessas',
    'neste': 'nessi',
    'nestes': 'nessis',
    'nossa': 'nossa',
    'nossas': 'nossas',
    'nosso': 'nossu',
    'nossos': 'nossus',
    'quais': 'kuais',
    'quaisquer': 'kuauké',
    'qual': 'kuau',
    'qualquer': 'kuauké',
    'quem': 'kêyn',
    'seu': 'teu',
    'seus': 'teus',
    'sua': 'tua',
    'suas': 'tuas',
    'voce': 'cê',
    'você': 'cê',
    'voces': 'cês',
    'vocês': 'cês',

    # Prepositions and Conjunctions
    'à': 'a',
    'às': 'as',
    'com': 'cum',
    'e': 'y',
    'em': 'ein',
    'mas': 'máys',
    'para': 'pra',
    'pela': 'pela',
    'pelas': 'pelas',
    'pelo': 'pelu',
    'pelos': 'pelus',
    'por': 'pur',
    'por que': 'pur ke',
    'porque': 'purkê',
    'porquê': 'purkê',

    # Tech Terms
    'app': 'épi',
    'apps': 'épis',
    'celular': 'celulá',
    'email': 'iméu',
    'facebook': 'feisbuqui',
    'google': 'gugou',
    'instagram': 'instagran',
    'internet': 'interneti',
    'link': 'linki',
    'links': 'linkis',
    'mouse': 'mauzi',
    'site': 'sáiti',
    'sites': 'sáitis',
    'smartphone': 'ysmartifôni',
    'tablet': 'táblete',
    'tiktok': 'tiquitóqui',
    'twitter': 'tuíter',
    'whatsapp': 'uatzápi',
    'wifi': 'uaifai',
    'youtube': 'iutiúbi',

    # Common Verbs
    'vamos': 'vam',
    'vou': 'vô',

    # Common Words and Expressions
    'agora': 'gora',
    'aí': 'aí',
    'ali': 'ali',
    'aqui': 'aki',
    'atrás': 'atráyz',
    'bem': 'beyn',
    'depois': 'dipois',
    'desculpa': 'discupa',
    'desculpas': 'discupas',
    'empresa': 'impreza',
    'empresas': 'imprezas',
    'então': 'entãum',
    'juntos': 'juntu',
    'lá': 'lá',
    'mais': 'máys',
    'muito': 'muyntu',
    'muita': 'muynta',
    'muitas': 'muyntas',
    'muitos': 'muyntus',
    'não': 'nãum',
    'obrigada': 'brigada',
    'obrigado': 'brigadu',
    'que': 'ki',
    'sempre': 'seynpri',
    'também': 'tãmbêyn',
    'teatro': 'tiatru',
    'teatros': 'tiatrus',
    'última': 'útima',
    'últimas': 'útimas',
    'último': 'útimu',
    'últimos': 'útimus'
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
    sys.stdout.flush()
    # Check dictionary with lowercase word
    if word in PHONETIC_DICTIONARY:
        print(f"Found in dictionary: '{word}' -> '{PHONETIC_DICTIONARY[word]}'")  
        sys.stdout.flush()
        transformed = PHONETIC_DICTIONARY[word]
        # Preserve original capitalization
        return preserve_capital(original, transformed)
    else:
        print(f"Not found in dictionary: '{word}'")  
        sys.stdout.flush()
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
    Rules Rule 1c - Rule 7c:

    Rule 1c: If the first ends in a vowel and the second starts with the same vowel => merge
    Rule 2c: If first ends in 'a' or 'o' and second starts with 'e' => merge with 'i'
    Rule 3c: If first ends in 'a' and second starts with vowel
    Rule 4c: If first ends in 'u' and second starts with vowel => add 'w' between
    Rule 5c: All other vowel combinations - just stitch them together
    Rule 6c: If first ends in 's' or 'z' and second starts with vowel => merge and use 'z'
    Rule 7c: If second word is 'y' (from 'e') and third word starts with 'y' or 'i',
            and first word ends in a vowel that's not 'y' or 'i',
            then attach the 'y' to the third word
    """
    if not first or not second:
        return first, second
        
    # Special case for 'y' from 'e'
    if (second == 'y' and  # This is the transformed 'e'
        first[-1] in 'aáàâãeéèêoóòôuúùû' and  # First word ends in vowel but not y/i
        len(first) > 0):
        return first, second  # Keep them separate so 'y' can combine with next word
        
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

    # Rule 5c - moved after other rules
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
        # First tokenize the text into words and punctuation
        tokens = tokenize_text(text)
        
        # Transform each word token according to rules
        transformed_tokens = []
        for word, punct in tokens:
            if word:
                # Apply dictionary lookup or phonetic rules
                transformed = apply_phonetic_rules(word)
                transformed_tokens.append((transformed, punct))
            else:
                transformed_tokens.append(('', punct))
        
        # Now handle vowel combinations between words in multiple passes
        # Keep going until no more combinations can be made
        made_combination = True
        while made_combination:
            made_combination = False
            new_tokens = []
            i = 0
            while i < len(transformed_tokens):
                if i < len(transformed_tokens) - 2:  # We have at least 3 tokens to look at
                    word1, punct1 = transformed_tokens[i]
                    word2, punct2 = transformed_tokens[i + 1]
                    word3, punct3 = transformed_tokens[i + 2]
                    
                    # Special case for 'y' (from 'e') attraction
                    if (word2 == 'y' and 
                        word1 and word1[-1] in 'aáàâãeéèêoóòôuúùû' and
                        word3 and word3[0] in 'yi'):
                        # Combine 'y' with the third word, but avoid double y
                        new_tokens.append((word1, punct1))
                        new_tokens.append(('', punct2))
                        if word3[0] == 'y':
                            new_tokens.append((word3, punct3))  # Don't add another 'y'
                        else:
                            new_tokens.append(('y' + word3, punct3))
                        i += 3
                        made_combination = True
                        continue
                    
                # If we have at least 2 tokens left
                if i < len(transformed_tokens) - 1:
                    word1, punct1 = transformed_tokens[i]
                    word2, punct2 = transformed_tokens[i + 1]
                    
                    # Try to combine the words
                    combined1, combined2 = handle_vowel_combination(word1, word2)
                    if combined1 != word1 or combined2 != word2:
                        made_combination = True
                        if combined2:
                            new_tokens.append((combined1, punct1))
                            new_tokens.append((combined2, punct2))
                        else:
                            new_tokens.append((combined1, punct2))  # Use second punct
                        i += 2
                        continue
                
                # If no combination was made, keep the current token
                new_tokens.append(transformed_tokens[i])
                i += 1
                
            transformed_tokens = new_tokens
        
        # Finally, reassemble the tokens into a single string
        return reassemble_tokens_smartly(transformed_tokens)
    
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
