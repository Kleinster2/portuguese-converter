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
    'aquilo': 'akilu',
    'aquele': 'akêli',
    'aqueles': 'akêlis',
    'aquelela': 'akéla',
    'aquelelas': 'akélas',
    'ela': 'éla',
    'elas': 'élas',
    'ele': 'êli',
    'eles': 'êlis',
    'eli': 'êli',
    'essa': 'éssa',
    'essas': 'éssas',
    'esse': 'êssi',
    'esses': 'êssis',
    'esta': 'ésta',
    'estas': 'éstas',
    'este': 'êsti',
    'estes': 'êstis',
    'eu': 'eu',
    'meu': 'mêu',
    'nesta': 'néssa',
    'nestas': 'néssas',
    'neste': 'nêssi',
    'nestes': 'nêssis',
    'nossa': 'nóssa',
    'nossas': 'nóssas',
    'nosso': 'nóssu',
    'nossos': 'nóssus',
    'quais': 'kuais',
    'quaisquer': 'kuauké',
    'qual': 'kuau',
    'qualquer': 'kuauké',
    'quando': 'cuandu',
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
    'voce' : 'cê',
    'você' : 'cê',
    'voces' : 'cêys',
    'vocês' : 'cêys',

    # Adverbs
    'demais': 'dimais',
    'devagar': 'divagá',
    'outro': 'ôtru',
    'outros': 'ôtrus',
    'outra': 'ôtra',
    'outras': 'ôtras',

    # Prepositions and Conjunctions
    'à': 'a',
    'às': 'as',
    'com': 'cum',
    'sem': 'sêyn',
    'e': 'i',
    'em': 'ein',
    'mas': 'máys',
    'para': 'pra',
    'pela': 'pela',
    'pelas': 'pelas',
    'pelo': 'pelu',
    'pelos': 'pelus',
    'por': 'pur',
    'porque': 'purkê',
    'porquê': 'purkê',
    'de': 'di',
    'dele': 'dêli',
    'deles': 'dêlis',
    'desta': 'déssa',
    'destas': 'déssas',
    'deste': 'dêssi',
    'destes': 'dêssis',

    # Tech Terms
    'app': 'épi',
    'apps': 'épis',
    'celular': 'celulá',
    'email': 'imêiu',
    'facebook': 'feicibúqui',
    'google': 'gugou',
    'instagram': 'instagran',
    'internet': 'internéti',
    'link': 'linki',
    'links': 'linkis',
    'mouse': 'mauzi',
    'site': 'sáiti',
    'sites': 'sáitis',
    'smartphone': 'ysmartifôni',
    'tablet': 'tábleti',
    'tiktok': 'tikitóki',
    'twitter': 'tuíter',
    'whatsapp': 'uatizápi',
    'wifi': 'uaifai',
    'youtube': 'iutiúbi',
    'chat': 'chati',
    'ipad': 'aipédi',

    # Common Words and Expressions
    'aí': 'aí',
    'ali': 'alí',
    'aqui': 'akí',
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
    'nao': 'nãu',
    'não': 'nãu',
    'obrigada': 'brigada',
    'obrigado': 'brigadu',
    'que': 'ki',
    'sempre': 'seynpri',
    'também': 'tãmbêyn',
    'tambem': 'tãmbêyn',
    'teatro': 'tiatru',
    'teatros': 'tiatrus',
    'última': 'útima',
    'últimas': 'útimas',
    'último': 'útimu',
    'últimos': 'útimus',
    'dormir': 'durmí',
    'dormiu': 'durmíu',
    'dormiram': 'durmíram',
    'atual': 'atuau',
    'atualmente': 'atuaumêinti',
    'agora': 'agóra',
    'hoje': 'ôji',
    'mes': 'mêys',
    'meses': 'mêzis',
    'menos': 'menus',
    'menor': 'menor',
    'menores': 'menoris',
    'pouco': 'pôcu',
    'poucos': 'pôcus',
    'pouca': 'pôca',
    'poucas': 'pôcas',
    'bonito': 'bunitu',
    'bonita': 'bunita',
    'bonitas': 'bunitas',
    'bonitos': 'bunitus'
}

# Word pairs that need special handling (not covered by regular rules)
WORD_PAIRS = {
    'a gente': 'agênti',
    'por que': 'purkê',
    'por quê': 'purkê',
    'para que': 'prakê',
    'para quê': 'prakê',
    'vamos embora': 'vambora',
    'vamo embora': 'vambora',
    'para você': 'prucê',
    'pra você': 'prucê',
    'para vocês': 'prucêys',
    'pra vocês': 'prucêys',
    'com você': 'cumcê',
    'com vocês': 'cumcêys',
    'sem você': 'sêyn ucê',
    'sem vocês': 'sêyn ucêys',
    'sem voce': 'sêyn ucê',
    'sem voces': 'sêyn ucêys',
    'para voce': 'prucê',
    'para voces': 'prucêys',
    'pra voce': 'prucê',
    'pra voces': 'prucêys',
    'com voce': 'cucê',
    'com voces': 'cucêys',
    'de voce': 'ducê',
    'de voces': 'ducêys',
    'de você': 'ducê',
    'de vocês': 'ducêys',
    'o que': 'ukê',
    'em um': 'num',
    'em uns': 'nuns',
    'em uma': 'numa',
    'em umas': 'numas',
    'em ele': 'nêli',
    'em eles': 'nêlis',
    'em ela': 'néla',
    'em elas': 'nélas',
    'em eles': 'nêlis',
    'com um': 'cum',
    'com uma': 'cuma',
    'com umas': 'cumas',
    'com uns': 'cuns',
    'com a': 'cua',
    'com as': 'cuas',
    'com o': 'cuo',
    'com os': 'cus',
    'com ele': 'cuêli',
    'com eles': 'cuêlis',
    'com ela': 'cuéla',
    'com elas': 'cuélas',
    'como você': 'comcê',
    'como vocês': 'comcêys',
    'como voce': 'comcê',
    'como voces': 'comcêys',
    'que eu': 'keu',
    'que é': 'ké',
    'esse é': 'êssé',
    'essa é': 'éssé',
    'está você': 'cê tá',
    'está voce': 'cê tá',
    'esta você': 'cê tá',
    'ta voce': 'cê tá',
    'tá você': 'cê tá',
    'tá voce': 'cê tá',
    'ta você': 'cê tá',
    'estão vocês': 'cêys tãum',
    'estão voces': 'cêys tãum',
    'estao vocês': 'cêys tãum',
    'estao voces': 'cêys tãum',
    'tão vocês': 'cêys tãum',
    'tão voces': 'cêys tãum',
    'tao voces': 'cêys tãum',
    'tao vocês': 'cêys tãum',
    'e você': 'iucê',
    'onde você': 'ond\'cê',
    'onde vocês': 'ond\'cêys',
    'onde voce': 'ond\'cê',
    'onde voces': 'ond\'cêys',
    'para de': 'para di',
    'vai voce': 'cê vai',   
    'vai você': 'cê vai',
    'vao voces': 'cêys vãu',
    'vão vocês': 'cêys vãu',
    'vao vocês': 'cêys vãu',
    'vão voces': 'cêys vãu',
    'esta voce': 'cê tá',
    'está voce': 'cê tá',
    'esta você': 'cê tá',
    'está você': 'cê tá',
    'ta voce': 'cê tá',
    'tá voce': 'cê tá',
    'ta você': 'cê tá',
    'tá você': 'cê tá',
    'estao voces': 'cêys tãu',
    'estão voces': 'cêys tãu',
    'estao vocês': 'cêys tãu',
    'estão vocês': 'cêys tãu',
    'tão voces': 'cêys tãu',
    'tão vocês': 'cêys tãu',
    'tao voces': 'cêys tãu',
    'tao vocês': 'cêys tãu',
    'anda voce': 'cê ãnda',
    'anda você': 'cê ãnda',
    'andam voces': 'cêys andãu',
    'andam vocês': 'cêys andãu',
    'do outro': 'dôtru',
    'de outro': 'dôtru',
    'da outra': 'dôtra',
    'dos outros': 'dôtrus',
    'das outras': 'dôtras',
    'em outro': 'nôtru',
    'em outra': 'nôtra',
    'em outros': 'nôtrus',
    'em outras': 'nôtras'
}

# Verb identification constants
IRREGULAR_VERBS = {
    "estar": "está", "estou": "tô", "estás": "tá", "está": "tá", "estamos": "tamu", "estão": "tãum",
    "ser": "sê", "sou": "sô", "é": "é", "somos": "somu", "são": "sãum",
    "ter": "tê", "tenho": "tenhu", "tem": "teim", "temos": "temu", "têm": "teim", "tive": "tivi", "teve": "tevi", "tivemos": "tivemu", "tiveram": "tiveraum", "tinha": "tinha", "tinhamos": "tinhamu", "tinham": "tinhaum",
    "fazer": "fazê", "faco": "fassu", "faço": "fassu", "faz": "fays", "fazemos": "fazêmu", "fazem": "fázeym", "fiz": "fis", "fez": "fêz", "fizemos": "fizemu", "fizeram": "fizérãu", "fazia": "fazia", "faziamos": "faziamu", "faziam": "faziãu", "faria": "fazia", "fariam": "faziãu",
    "ir": "ih", "vou": "vô", "vai": "vai", "vamos": "vam", "vão": "vãum",
    "vir": "vim", "venho": "venhu", "vem": "veym", "vimos": "vimu", "vêm": "veym",
    "dizer": "dizê", "digo": "digu", "diz": "dis", "dizemos": "dizemu", "dizem": "dizeym", "disse": "dissi", "dissemos": "dissemu", "disseram": "disseraum", "diria": "diria", "diriamos": "diriamus", "diriam": "diriaum", "dizia": "dizia", "diziamos": "diziamus", "diziam": "diziaum", "diga": "diz", "digamos": "digamu", "digam": "digãu",
    "pedir": "pedí", "peço": "pessu", "pedi": "pédi", "pedimos": "pedímu", "pedem": "pédeym",
    "dar": "dá", "dou": "dô", "dá": "dá", "damos": "dãmu", "dão": "dãum", "dei": "dei", "deu": "deu", "demos": "démus", "deram": "déraum",
    "faço": "fassu", "faz": "fays", "fazemos": "fazemu", "fazem": "fazeym", "fiz": "fis", "fizemos": "fizemu", "fizeram": "fizeraum",
    "querer": "kerê", "quero": "kéru", "quer": "ké", "queremos": "kerêmu", "querem": "kéreym", "quis": "kis", "quisemos": "kizemu", "quiseram": "kizeraum",
    "poder": "podê", "posso": "póssu", "pode": "pódi", "podemos": "podêmu", "podem": "pódeym", "pude": "pudi", "pudemos": "pudemu", "puderam": "puderaum",
    "ver": "vê", "vejo": "veju", "vê": "vê","ve": "vê", "vemos": "vemu", "veêm": "vem", "vi": "vi", "viu": "viu", "vimos": "vimu", "viram": "viraum",
    "saber": "sabê", "sei": "sei",
}

# Basic/Essential Verbs
BASIC_VERB_ROOTS = {
    "abr", "and", "bat", "beb", "cai", "cant", "ced", "cheg", "com", "corr", "cri", "deix", "dorm", "dur", 
    "entr", "exist", "fal", "faz", "fech", "fic", "ir", "lê", "mor", "nad", "nasc", "ouv", "par", "part", 
    "pass", "perd", "sa", "sai", "sent", "ser", "tem", "ter", "tir", "toc", "val", "venc", "vend", "ver", 
    "vir", "viv", "volt"
}

# Common Action Verbs
ACTION_VERB_ROOTS = {
    "abus", "acab", "aceit", "acess", "acompanh", "acord", "adiant", "afast", "ajud", "alug", "amarr", "amol", "apag", "avanç", "apanh", "apront", "apress",
    "aproveit", "arm", "arrast", "arremess", "arrum", "assin", "atend", "atra", "atras", "atravess", "atualiz", "aument", "avis", "bail", 
    "baix", "beij", "brinc", "busc", "caç", "calç", "carreg", "cham", "chut", "coç", "colet", "colid", "colh", "começ", 
    "compr", "comunic", "control", "convid", "coloc", "copi", "corrig", "cort", "cozinh", "cumpr", "curt", "danc", 
    "danç", "descans", "destac", "destru", "dit", "edit", "empreg", "empurr", "encontr", "encost", "enfeit", "engol", "entreg", "envi", "escolh", "escut", 
    "flert", "form", "grit", "guard", "imprim", "jog", "junt", "lav", "levant", "lig", "limp", "lut", "marc", 
    "met", "mex", "molh", "mord", "mostr", "mud", "olh", "peg", "reform", "remarc", "remov", "repet", "resist", "retir", "reun", "salt", 
    "salv", "samb", "soletr", "som", "solt", "sorri", "sub", "suport", "torc", "trabalh", "transport", "trat", "troc", "utiliz", "vest", "viaj"
}

# Cognitive/Mental Verbs
COGNITIVE_VERB_ROOTS = {
    "ach", "adivinh", "ador", "admir", "admit", "afirm", "agrad", "aguent", "alcanç", "amanhec", "amar", "anot", "aprend", "apresent", 
    "assist", "assum", "chec", "coment", "comet", "compar", "concord", "conhec", "consegu", "consig", "consig", "consider", "consist", 
    "consent", "consult", "contempl", "cont", "convers", "decid", "defend", "defin", "demor", "depend", "desej", "desenh", "desenvolv", 
    "descobr", "desist", "dirig", "discut", "divid", "entend", "esper", "esquec", "esqueç", "estud", "evit", 
    "foc", "gost", "imagin", "import", "indic", "inform", "inici", "insist", "instru", "lembr", "ment", "mint", "not", "observ", "opin", 
    "particip", "pens", "perceb", "pergunt", "permit", "persist", "preocup", "prepar", "pretend", "precis", 
    "procur", "promet", "sab", "sofr", "soub", "signific", "tent", "termin", "top", "verific", "visit"
}

# Complex/Process Verbs
PROCESS_VERB_ROOTS = {
    "acumul", "atrapalh", "convert", "constru", "contrat", "correspond", "deposit", "dobr", "expand", "exib", "experiment", "explic", "explor", 
    "expuls", "extrai", "finaliz", "fortalec", "imped", "inclu", "interromp", "morr", "ocup", "oferec", "omit", "organ", "produz", 
    "quebr", "reag", "reaj", "realiz", "receb", "reclam", "reduz", "reflet", "relax", "represent", "reserv", 
    "resolv", "respond", "restit", "romp", "segu", "serv", "sorr", "sub", "substitu", "suj", "surprend", 
    "traduz", "transform", "un", "us"
}

# Combined set of all verb roots
ALL_ROOTS = BASIC_VERB_ROOTS | ACTION_VERB_ROOTS | COGNITIVE_VERB_ROOTS | PROCESS_VERB_ROOTS

# Verb endings
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

def merge_word_pairs(tokens):
    """Merge word pairs that need special handling before individual word transformations."""
    new_tokens = []
    i = 0
    while i < len(tokens):
        word1, punct1 = tokens[i]
        if i + 1 < len(tokens):
            word2, punct2 = tokens[i + 1]
            word_pair = f"{word1} {word2}".lower()
            if (word1 and word2 and not punct1 and 
                word_pair in WORD_PAIRS):
                # Merge them
                merged = preserve_capital(word1, WORD_PAIRS[word_pair])
                # Add as a single token (word, punct)
                new_tokens.append((merged, punct2))
                i += 2
                continue
        # No merge, just append the current
        new_tokens.append((word1, punct1))
        i += 1
    return new_tokens

def apply_phonetic_rules(word, next_word=None, next_next_word=None):
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

    # Check irregular verbs first
    if lword in IRREGULAR_VERBS:
    #    print(f"Found irregular verb: '{lword}' -> '{IRREGULAR_VERBS[lword]}'")
        return preserve_capital(word, IRREGULAR_VERBS[lword])

    # Special handling for não before verbs
    if lword in ["não", "nao"]:
        if next_word:
            # Check if the next word is a pronoun
            pronouns = ["me", "te", "se", "nos", "vos", "lhe", "lhes", "o", "a", "os", "as", "lo", "la", "los", "las", "no", "na", "nos", "nas"]
            if next_word.lower() in pronouns:
                # Check if the word after pronoun is a verb
                if next_next_word and is_verb(next_next_word):
                    return preserve_capital(word, "num")
            elif is_verb(next_word):
                return preserve_capital(word, "num")

    # Check dictionary
    if lword in PHONETIC_DICTIONARY:
        print(f"Found in dictionary: '{lword}' -> '{PHONETIC_DICTIONARY[lword]}'")
        return preserve_capital(word, PHONETIC_DICTIONARY[lword])

    # If not in dictionary, apply rules
    transformed = word
    
    # Apply each rule in sequence
    # Rule 1p: Final unstressed vowels reduce ('o'->'u', 'os'->'us', 'e'->'i', 'es'->'is')
    if transformed.lower().endswith('o'):
        transformed = transformed[:-1] + 'u'
    elif transformed.lower().endswith('os'):
        transformed = transformed[:-2] + 'us'
    elif transformed.lower().endswith('e'):
        transformed = transformed[:-1] + 'i'
    elif transformed.lower().endswith('es'):
        transformed = transformed[:-2] + 'is'
        
    # Rule 2p: Initial 'es' becomes 'is'
    if transformed.lower().startswith('es'):
        transformed = 'is' + transformed[2:]
        
    # Rule 3p: 'ão' at the end becomes 'aum'
    if transformed.lower().endswith('ão'):
        transformed = transformed[:-2] + 'aum'
        
    # Rule 4p: 's' between vowels becomes 'z'
    transformed = re.sub(r'([aeiouáéíóúâêîôûãẽĩõũ])s([aeiouáéíóúâêîôûãẽĩõũ])', r'\1z\2', transformed, flags=re.IGNORECASE)

    # Rule 5p: Transform 'olh' to 'ôly'
    if not is_verb(word):
        if 'olh' in transformed.lower():
            transformed = transformed.lower().replace('olh', 'ôly')

    # Rule 6p: 'lh' => 'ly'
    #if not is_verb(word):
    if 'lh' in transformed.lower():
        transformed = transformed.lower().replace('lh', 'ly')
    #    transformed = transformed.replace('lh', 'ly').replace('Lh', 'Ly').replace('LH', 'LY')

    # Rule 7p: Final 'ou' becomes 'ô'
    if transformed.lower().endswith('ou'):
        transformed = transformed[:-2] + 'ô'
        
    # Rule 8p: Final 'm' => 'n' (nasalization)
    if transformed.lower().endswith('m'):
        transformed = transformed[:-1] + 'n'
        
    # Rule 9p: Verb endings (ar -> á, er ->ê, ir -> í)
    if is_verb(word):
        if transformed.lower().endswith('ar'):
            transformed = transformed[:-2] + 'á'
        elif transformed.lower().endswith('er'):
            transformed = transformed[:-2] + 'ê'
        elif transformed.lower().endswith('ir'):
            transformed = transformed[:-2] + 'í'
    
    # Rule 10p: Remove initial 'h' (hoje->oje, homem->omem)
    if transformed.lower().startswith('h'):
        transformed = transformed[1:]
    
    # Rule 11p: Initial 'ex' becomes 'ez'
    if transformed.lower().startswith('ex'):
        transformed = 'ez' + transformed[2:]

    # Rule 12p: Initial 'pol' becomes 'pul'
    if transformed.lower().startswith('pol'):
        transformed = 'pul' + transformed[3:]

    # Rule 13p: Initial 'volt' becomes 'vout'   
    if transformed.lower().startswith('volt'):
        transformed = 'vout' + transformed[4:]

    # Rule 14p: Final 'ol' => 'óu'
    if transformed.lower().endswith('ol'):
        transformed = transformed[:-2] + 'óu'

    # Rule 15p: Final 'l' => 'u'
    if transformed.lower().endswith('l'):
        transformed = transformed[:-1] + 'u'    

    # Rule 16p: Insert 'i' between specific consonant pairs
    if any(p in transformed.lower() for p in ['bs', 'ps', 'pn', 'dv', 'pt', 'pç', 'dm', 'gn', 'tm', 'tn']):
        for p in ['bs', 'ps', 'pn', 'dv', 'pt', 'pç', 'dm', 'gn', 'tm', 'tn']:
            transformed = re.sub(f'{p}', f'{p[0]}i{p[1]}', transformed.lower())

    # Rule 17p: Append 'i' to words ending in specific consonants
    if transformed.lower().endswith(('d', 't', 'b', 'f', 'j', 'k', 'p', 't', 'v')):
        transformed = transformed + 'i' 

    # Rule 18p: Replace final 'c' with 'ki'
    if transformed.lower().endswith('c'):
        transformed = transformed[:-1] + 'ki'

    # Rule 19p: Append 'ui' to words ending in 'g'
    if transformed.lower().endswith('g'):
        transformed = transformed + 'ui'

    # Rule 20p: Transform 'eir' to 'er'
    if 'eir' in transformed.lower():
        transformed = transformed.lower().replace('eir', 'êr')

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

    Rule 0c: If word ends in 'r' and next word starts with vowel => merge keeping the 'r'
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
    MAX_COMBINED_LENGTH = 15
    if len(first) + len(second) > MAX_COMBINED_LENGTH:
        return first, second
    
    vowels = 'aeiouáéíóúâêîôûãẽĩõũy'
    
    # Rule 0c: If word ends in 'r' and next word starts with vowel => merge keeping the 'r'
    if first.endswith('r') and second[0].lower() in vowels:
        return first + second, ''

    # Special case: Double 'm' between words becomes single 'm'
    if first.endswith('ia') and second.startswith('i'):
        return first[:-2] + second, ''

    # Special case: Double 'm' between words becomes single 'm'
    if first.endswith('m') and second.startswith('m'):
        return first[:-1] + second, ''

    # Special case: 'á' followed by 'a' becomes just 'á'
    if first.endswith('á') and second.startswith('a'):
        return first[:-1] + second, ''

    # Special case: 'ê' followed by 'é' becomes just 'é'
    if first.endswith('ê') and second.startswith('é'):
        return first[:-1] + second, ''

    # Special case: Double 's' between words becomes single 's'
    if first.endswith('s') and second.startswith('s'):
        return first[:-1] + second, ''

    if (first[-1].lower() in vowels
        and second[0].lower() in vowels
        and first[-1].lower() == second[0].lower()):
        # Preserve case of second word's first letter
        return first[:-1] + second[0] + second[1:], ''
    
    # Rule 2c
    # if first[-1] in 'ao' and second.startswith('e'):
    #     return first + 'i' + second[1:], ''
    
    # Rule 3c
    if first[-1] == 'a' and second[0] in 'eiouáéíóúâêîôûãẽĩõũy':
        if second[0] in 'ie':  # Handle both 'i' and 'e'
            if first.endswith('ga'):
                return first[:-2] + 'gu' + second, ''  # Will handle both 'gui' and 'gue'
            elif first.endswith('ca'):
                return first[:-2] + 'k' + second, ''   # Will handle both 'ki' and 'ke'
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
    pattern = r'([A-Za-zÀ-ÖØ-öø-ÿ0-9]+)|([.,!?;:()\[\]{}]+)'
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
    Returns two versions:
        1. Before combination (after merging and initial transformation)
        2. After combination (final transformed text)
    """
    if not text:
        return text, text
    
    try:
        # First tokenize the text into words and punctuation
        tokens = tokenize_text(text)
        
        # Merge word pairs that need special handling
        tokens = merge_word_pairs(tokens)
        
        # Transform each word token according to rules
        transformed_tokens = []
        for i, (word, punct) in enumerate(tokens):
            if word:
                # Get next word and word after that for verb/pronoun detection
                next_word = None
                next_next_word = None
                if i + 1 < len(tokens):
                    next_word = tokens[i + 1][0]  # Get the actual next word
                    if i + 2 < len(tokens):
                        next_next_word = tokens[i + 2][0]  # Get the word after next
                # Apply dictionary lookup or phonetic rules
                transformed = apply_phonetic_rules(word, next_word, next_next_word)
                transformed_tokens.append((transformed, punct))
            else:
                transformed_tokens.append(('', punct))
        
        # Capture the "Before Combination" output
        before_combination = reassemble_tokens_smartly(transformed_tokens)
        
        # Now handle vowel combinations between words in multiple passes
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
                    if (word2 == 'y' and  # This is the transformed 'e'
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
        
        # Capture the "After Combination" output
        after_combination = reassemble_tokens_smartly(transformed_tokens)
        
        return before_combination, after_combination
    
    except Exception as e:
        print(f"Error transforming text: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return {'before': before, 'after': after}

def convert_text(text):
    """Convert Portuguese text to its phonetic representation."""
    before, after = transform_text(text)
    return {'before': before, 'after': after}

def main():
    # Set UTF-8 encoding for stdout
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Check if text is provided as a command-line argument
    if len(sys.argv) > 1:
        input_text = ' '.join(sys.argv[1:])
    else:
        # If not, read from standard input
        print("Enter the text to convert (Ctrl+D to end):")
        input_text = sys.stdin.read()
    
    # Process each line separately
    lines = input_text.splitlines()
    if not lines:
        lines = ['']
    
    # Convert and display each line
    for line in lines:
        result = convert_text(line)
        print(result['before'])
        print(result['after'])

if __name__ == "__main__":
    main()