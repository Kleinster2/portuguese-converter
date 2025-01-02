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
    'te' : 'ti',
    'me' : 'mi',
    'lhe' : 'ly',
    'lhes' : 'lys',
    'nos' : 'nus',
    'o' : 'u',
    'os' : 'us',

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
    'tablet': 'tábleti',
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

# Verb identification constants
IRREGULAR_VERBS = {
    "estar": "está", "estou": "tô", "estás": "tá", "está": "tá", "estamos": "tamu", "estão": "tãum",
    "ser": "sê", "sou": "sô", "é": "éh", "somos": "somu", "são": "sãum",
    "ter": "tê", "tenho": "tenhu", "tem": "teym", "temos": "temu", "têm": "teym", "tive": "tivi", "teve": "tevi", "tivemos": "tivemu", "tiveram": "tiveraum", "tinha": "tinha", "tinhamos": "tinhamu", "tinham": "tinhaum",
    "fazer": "fazê", "faco": "fassu", "faço": "fassu", "faz": "fays", "fazemos": "fazêmu", "fazem": "fázeym", "fiz": "fis", "fez": "fêz", "fizemos": "fizemu", "fizeram": "fizéraum", "fazia": "fazia", "faziamos": "faziamu", "faziam": "faziaum",
    "ir": "ih", "vou": "vô", "vai": "vai", "vamos": "vam", "vão": "vãum",
    "vir": "vi", "venho": "venhu", "vem": "veym", "vimos": "vimu", "vêm": "veym",
    "dizer": "dizê", "digo": "digu", "diz": "dis", "dizemos": "dizemu", "dizem": "dizeym", "disse": "dissi", "dissemos": "dissemu", "disseram": "disseraum", "diria": "diria", "diriamos": "diriamus", "diriam": "diriaum", "dizia": "dizia", "diziamos": "diziamus", "diziam": "diziaum", "diga": "diga", "digamos": "digamus", "digam": "digaum",
    "pedir": "pedí", "peço": "pessu", "pedi": "pédi", "pedimos": "pedímu", "pedem": "pédeym",
    "dar": "dá", "dou": "dô", "dá": "dá", "damos": "dãmu", "dão": "dãum", "dei": "dei", "deu": "deu", "demos": "démus", "deram": "déraum",
    "faço": "fassu", "faz": "fays", "fazemos": "fazemu", "fazem": "fazeym", "fiz": "fis", "fizemos": "fizemu", "fizeram": "fizeraum",
    "querer": "kerê", "quero": "kéru", "quer": "ké", "queremos": "kerêmu", "querem": "kéreym", "quis": "kis", "quisemos": "kizemu", "quiseram": "kizeraum",
    "poder": "podê", "posso": "póssu", "pode": "pódi", "podemos": "podêmu", "podem": "pódeym", "pude": "pudi", "pudemos": "pudemu", "puderam": "puderaum",
    "ver": "vê", "vejo": "veju", "vê": "vê","ve": "vê", "vemos": "vemu", "veêm": "vem", "vi": "vi", "viu": "viu", "vimos": "vimu", "viram": "viraum",
}

ALL_ROOTS = {
    "abr", "acab", "acend", "ach", "acontec", "ador", "afast", "agred", "ajud", "alug", "am", "ampli", 
    "and", "anot", "apag", "apanh", "aprend", "apresent", "arm", "arrast", "arrum", "assin", "assist", 
    "assum", "atend", "atra", "atravess", "avis", "bail", "baix", "bat", "beb", "beij", "brinc", "caç", 
    "calç", "cant", "carreg", "ced", "cham", "cheg", "chut", "colet", "colh", "com", "começ", "coment", 
    "comet", "compar", "compr", "concord", "conhec", "consent", "constru", "cont", "contrat", "convers", 
    "correspond", "corr", "corrig", "cort", "cozinh", "cumpr", "curt", "danc", "danç", "decid", "defend", 
    "defin", "deix", "demor", "depend", "deposit", "desej", "desenh", "descobr", "desist", "dirig", "discut", 
    "divid", "dobr", "dorm", "empreg", "empurr", "encontr", "enfeit", "engol", "entend", "entr", "entreg", 
    "escolh", "escut", "esper", "esquec", "esqueç", "estud", "evit", "expand", "exib", "explic", "explor", 
    "expuls", "extrai", "fal", "fech", "fer", "fic", "finaliz", "flert", "gost", "grit", "guard", "imag", 
    "imped", "inform", "insist", "instru", "interromp", "jant", "jog", "lav", "lembr", "lig", "limp", "lut", 
    "mand", "met", "mex", "mor", "mord", "mostr", "mud", "nad", "observ", "oferec", "omit", "ouv", "part", 
    "pass", "perceb", "perd", "permit", "persist", "plant", "prefer", "preench", "prend", "pressent", "pretend", 
    "promet", "proteg", "reag", "reaj", "receb", "reduz", "reflet", "remov", "respond", "restit", "romp", 
    "sai", "salt", "sent", "serv", "sorr", "sub", "substitu", "surprend", "tem", "toc", "tom", "traduz", "un", 
    "val", "venc", "vend", "ver", "vest", "viv", "volt", "vot"
}

ALL_ENDINGS = [
    "a", "am", "amos", "ando", "ar", "ara", "ará", "aram", "arao", "arão", "aras", "arás",
    "arei", "arem", "aremos", "ares", "aria", "ariamos", "aríamos", "armos", "asse", "assem", "assemos", "ássemos", "asses",
    "aste", "ava", "avam", "avamos", "ávamos", "avas", "e", "ei", "em", "emos", "endo", "er",
    "era", "erá", "eram", "erao", "erão", "eras", "erás", "erei", "erem", "eremos",
    "eres", "eria", "eríamos", "eriamos", "es", "esse", "este", "eu", "i", "ia", "iam", "iamos", "íamos", "imas", "imos", "indo",
    "ir", "irá", "ira", "irão", "irao", "iras", "irás", "irei", "irem", "iremos",
    "ires", "iria", "iríamos", "iriamos", "irmos", "isse", "issem", "isses", "issemos", "iste", "iu", "o", "ou",
    "u", "íssemos"
]

def is_verb(word):
    """
    Check if a word is a verb by:
    1. Checking if it's in the irregular verbs dictionary
    2. Checking if it has a valid verb root and ending
    """
    if not word:
        return False
    lw = word.lower()
    if lw in IRREGULAR_VERBS or lw in IRREGULAR_VERBS.values():
        return True
    for end in ALL_ENDINGS:
        if lw.endswith(end):
            root = lw[:-len(end)]
            if root in ALL_ROOTS:
                return True
    return False

def apply_phonetic_rules(word, next_word=None):
    """
    Apply Portuguese phonetic rules to transform a word.
    First checks a dictionary of pre-defined transformations,
    if not found, applies the rules in sequence.
    
    Args:
        word: The word to transform
        next_word: The next word in the sequence (optional), used for verb detection
    """
    # First check if it's in our dictionary
    lword = word.lower()
    print(f"Checking dictionary for: '{lword}'")

    # Check if it's an irregular verb
    if lword in IRREGULAR_VERBS:
        print(f"Found irregular verb: '{lword}' -> '{IRREGULAR_VERBS[lword]}'")
        return preserve_capital(word, IRREGULAR_VERBS[lword])

    # Special handling for você/vocês and não before verbs
    if next_word and is_verb(next_word):
        if lword == "você":
            print(f"Found 'você' before verb '{next_word}', using 'cê'")
            return preserve_capital(word, "cê")
        elif lword == "vocês":
            print(f"Found 'vocês' before verb '{next_word}', using 'cês'")
            return preserve_capital(word, "cês")
        elif lword == "não":
            print(f"Found 'não' before verb '{next_word}', using 'num'")
            return preserve_capital(word, "num")

    # Check dictionary
    if lword in PHONETIC_DICTIONARY:
        print(f"Found in dictionary: '{lword}' -> '{PHONETIC_DICTIONARY[lword]}'")
        return preserve_capital(word, PHONETIC_DICTIONARY[lword])

    # If not in dictionary, apply rules
    transformed = word
    
    # Apply each rule in sequence
    # Rule 1p: Final unstressed vowels reduce ('o'->'u', 'os'->'us', etc.)
    if transformed.lower().endswith('o'):
        transformed = transformed[:-1] + 'u'
    elif transformed.lower().endswith('os'):
        transformed = transformed[:-2] + 'us'
        
    # Rule 2p: Vowel raising in unstressed syllables
    # TODO: Implement more complex vowel raising rules
    
    # Rule 3p: 'ão' at the end becomes 'aum'
    if transformed.lower().endswith('ão'):
        transformed = transformed[:-2] + 'aum'
        
    # Rule 4p: 's' between vowels becomes 'z'
    transformed = re.sub(r'([aeiouáéíóúâêîôûãẽĩõũ])s([aeiouáéíóúâêîôûãẽĩõũ])', r'\1z\2', transformed, flags=re.IGNORECASE)
    
    # Rule 5p: 'lh' => 'ly'
    transformed = transformed.replace('lh', 'ly').replace('Lh', 'Ly').replace('LH', 'LY')
    
    # Rule 6p: Final 'l' => 'u'
    if transformed.lower().endswith('l'):
        transformed = transformed[:-1] + 'u'
        
    # Rule 7p: Final 'm' => 'n' (nasalization)
    if transformed.lower().endswith('m'):
        transformed = transformed[:-1] + 'n'
        
    # Rule 8p: Verb endings (ar -> á, er -> ê, ir -> í)
    # TODO: Add more verb ending transformations
    
    # Rule 9p: Common reductions (está->tá, para->pra, você->cê)
    # Handled by dictionary lookups
    
    # Rule 10p: Remove initial 'h' (hoje->oje, homem->omem)
    if transformed.lower().startswith('h'):
        transformed = transformed[1:]
    
    return preserve_capital(word, transformed)

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
        for i, (word, punct) in enumerate(tokens):
            if word:
                # Get next word for verb detection, looking ahead past pronouns and 'não'
                next_word = None
                pronouns = {'me', 'te', 'se', 'nos', 'vos', 'lhe', 'lhes', 'o', 'a', 'os', 'as'}
                skip_words = pronouns | {'não', 'nãum', 'num'}  # Also skip não and its variations
                
                # Look ahead up to 3 words to find a verb after pronouns/não
                for j in range(1, 4):  # Increased to 4 to handle more words in between
                    if i + j < len(tokens):
                        next_token = tokens[i + j][0].lower()  # [0] to get word part of tuple
                        if next_token in skip_words:
                            continue
                        next_word = next_token
                        break
                
                # Apply dictionary lookup or phonetic rules
                transformed = apply_phonetic_rules(word, next_word)
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
