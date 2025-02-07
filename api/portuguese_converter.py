#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import traceback
import io
import unicodedata

# Words ending in 'l' that have special accent patterns
ACCENTED_L_SUFFIXES = {
    'avel': 'ável',  # amável, notável, etc.
    'ável': 'ável',  # For words that already have the accent
    'ivel': 'ível',  # possível, visível, etc.
    'ível': 'ível',  # For words that already have the accent
    'ovel': 'óvel',  # móvel, imóvel, etc.
    'óvel': 'óvel',  # For words that already have the accent
}

# Words ending in 'l' that have unique accent patterns
ACCENTED_L_WORDS = {
    'ágil', 'útil', 'fácil', 'fútil', 'hábil', 'débil', 'dócil', 
    'fértil', 'fóssil', 'frágil', 'hífen', 'hóstil', 'húmil', 
    'lábil', 'míssil', 'pénsil', 'réptil', 'têxtil', 'tátil', 
    'túnel', 'dúctil', 'cônsul', 'níquel', 'álcool'
}

# Pre-defined phonetic transformations that bypass regular rules
PHONETIC_DICTIONARY = {
    # Pronouns and Articles
    'ate': 'até',
    # 'algum': 'augun',
    # 'alguma': 'auguma',
    # 'algumas': 'augumas',
    # 'alguns': 'auguns',
    'alguém': 'auguêin',
    'alguem': 'auguêin',
    'ninguém': 'ninguêin',
    'ninguem': 'ninguêin',
    'aquilo': 'akilu',
    'aquele': 'akêli',
    'aqueles': 'akêlis',
    'aquela': 'akéla',
    'aquelas': 'akélas',
    'daquilo': 'dakilu',
    'daquele': 'dakêli',
    'daqueles': 'dakêlis',
    'daquela': 'dakéla',
    'daquelas': 'dakélas',
    'naquilo': 'nakilu',
    'naquele': 'nakêli',
    'naqueles': 'nakêlis',
    'naquela': 'nakéla',
    'naquelas': 'nakélas',
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
    # 'eu': 'eu',
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
    'tao': 'tãu',
    'ta': 'tá',
    'me' : 'mi',
    'lhe' : 'ly',
    'lhes' : 'lys',
    'nos' : 'nus',
    'o' : 'u',
    'os' : 'us',
    'voce' : 'ucê',
    'você' : 'ucê',
    'voces' : 'ucêis',
    'vocês' : 'ucêis',

    # Adverbs
    'demais': 'dimais',
    'devagar': 'divagá',
    # 'outro': 'ôtru',
    # 'outros': 'ôtrus',
    # 'outra': 'ôtra',
    # 'outras': 'ôtras',

    # Prepositions and Conjunctions
    'à': 'a',
    'às': 'as',
    'com': 'cu',
    'sem': 'sêyn',
    'e': 'i',
    'em': 'in',
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
    'dessa': 'déssa',
    'dessas': 'déssas',
    'desse': 'dêssi',
    'desses': 'dêssis',

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
    # 'bem': 'beyn',
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
    'nao': 'nãun',
    'não': 'nãun',
    'obrigada': 'brigada',
    'obrigado': 'brigadu',
    'que': 'ki',
    'sempre': 'seynpri',
    'também': 'tãmbêin',
    'tambem': 'tãmbêin',
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
    'menor': 'menór',
    'menores': 'menoris',
    'pouco': 'pôcu',
    'poucos': 'pôcus',
    'pouca': 'pôca',
    'poucas': 'pôcas',
    'bonito': 'bunitu',
    'bonita': 'bunita',
    'bonitas': 'bunitas',
    'bonitos': 'bunitus',
    'olho': 'ôliu',
    'olhos': 'ôlius',
    'menino': 'mininu',
    'menina': 'minina',
    'meninas': 'mininas',
    'meninos': 'mininus'
}

# Direct transformations that bypass the phonetic rules pipeline
DIRECT_TRANSFORMATIONS = {
    'vamos': 'vam',
    'para': 'pra',
    'nova': 'nôva',
    'novas': 'nóvas',
    'novamente': 'nóvamenti',
    'otimo': 'ótimu',
    'ótimo': 'ótimu'
}

# Word pairs that need special handling (not covered by regular rules)
WORD_PAIRS = {
    'a gente': 'agenti',
    'por que': 'purkê',
    'por quê': 'purkê',
    'para que': 'prakê',
    'para quê': 'prakê',
    'vamos embora': 'vambóra',
    'vamo embora': 'vambóra',
    'com você': 'cucê',
    'com vocês': 'cucêys',
    'com voce': 'cucê',
    'com vocês': 'cucêys',
    'sem você': 'sêyn ucê',
    'sem vocês': 'sêyn ucêys',
    'sem voce': 'sêyn ucê',
    'sem voces': 'sêyn ucêys',
    # 'para você': 'prucê',
    # 'pra você': 'prucê',
    # 'para vocês': 'prucêys',
    # 'pra vocês': 'prucêys',    
    # 'para voce': 'prucê',
    # 'para voces': 'prucêys',
    # 'pra voce': 'prucê',
    # 'pra voces': 'prucêys',
    'com voce': 'cucê',
    'com voces': 'cucêys',
    'de voce': 'ducê',
    'de voces': 'ducêys',
    'de você': 'ducê',
    'de vocês': 'ducêys',
    # 'o que': 'ukê',
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
    'com você': 'cucê',
    'com vocês': 'cucêis',
    'com voce': 'cucê',
    'com voces': 'cucêis',
    'como você': 'comucê',
    'como vocês': 'comucêis',
    'como voce': 'comucê',
    'como voces': 'comucêis',
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
    "estar": "está", "estou": "tô", "estás": "tá", "está": "tá", "estamos": "tam", "estão": "tãum", "estive": "tivi", "esteve": "tevi", "estivemos": "tivimu", "estiveram": "tiverãu", "estava": "tava", "estavamos": "tavamu", "estavam": "tavãu",
    "ser": "sê", "sou": "sô", "é": "é", "somos": "somu", "são": "sãun", "fui": "fui", "foi": "fôi", "fomos": "fomu", "foram": "forãu",
    "ter": "tê", "tenho": "tenhu", "tem": "tein", "temos": "temu", "têm": "teim", "tive": "tivi", "teve": "tevi", "tivemos": "tivemu", "tiveram": "tiveraum", "tinha": "tinha", "tinhamos": "tinhamu", "tinham": "tinhaum",
    "fazer": "fazê", "faco": "fassu", "faço": "fassu", "faz": "fays", "fazemos": "fazêmu", "fazem": "fázeym", "fiz": "fis", "fez": "fêiz", "fizemos": "fizemu", "fizeram": "fizérãu", "fazia": "fazia", "faziamos": "faziamu", "faziam": "faziãu", "faria": "fazia", "fariam": "faziãu",
    "ir": "ih", "vou": "vô", "vai": "vai", "vamos": "vamos", "vão": "vãun",
    "vir": "vim", "venho": "venhu", "vem": "veyn", "vimos": "vimu", "vêm": "veym",
    "dizer": "dizê", "digo": "digu", "diz": "dis", "dizemos": "dizemu", "dizem": "dizeym", "disse": "dissi", "dissemos": "dissemu", "disseram": "disseraum", "diria": "diria", "diríamos": "diriamus", "diriamos": "diriamus", "diriam": "diriaum", "diga": "diz", "digamos": "digamu", "digam": "digãu",
    "pedir": "pedí", "peço": "pessu", "pedi": "pédi", "pedimos": "pedímu", "pedem": "pédeym",
    "dar": "dá", "dou": "dô", "dá": "dá", "damos": "dãmu", "dão": "dãun", "dei": "dei", "deu": "deu", "demos": "démus", "deram": "déraum",
    "faço": "fassu", "faz": "fays", "fazemos": "fazemu", "fazem": "fazeym", "fiz": "fis", "fizemos": "fizemu", "fizeram": "fizeraum",
    "querer": "kerê", "quero": "kéru", "quer": "ké", "queremos": "kerêmu", "querem": "kéreym", "quis": "kis", "quisemos": "kizemu", "quiseram": "kizeraum",
    "poder": "podê", "posso": "póssu", "pode": "pódi", "podemos": "podêmu", "podem": "pódeym", "pude": "pudi", "pudemos": "pudemu", "puderam": "puderaum",
    "ver": "vê", "vejo": "veju", "vê": "vê", "ve": "vê", "vemos": "vemu", "veem": "veem", "vi": "vi", "viu": "viu", "vimos": "vimu", "viram": "viraum",
    "saber": "sabê", "sei": "sei", "soube": "soube", "soubemos": "soubemos", "souberam": "souberam",
    "trazer": "trazê", "trago": "trago", "traz": "traz", "trazemos": "traizemu", "trazem": "traizeym", "trocar": "troca", "trocamos": "trocamu", "trocam": "trocaum", "trocaram": "trocaum",
    "mentir": "menti", "minto": "minto", "mente": "meinti", "mentimos": "mintimos", "mentem": "mentem", "mentia": "mintia", "mentiamos": "mintiamos", "mentiam": "mintiam", "mentiram": "mintiram",
    "ler": "lê", "leio": "lêiu", "lê": "lê", "lemos": "lêmus",
    "olhar": "olia", "olho": "olho", "olhamos": "olhamus", "olham": "olham", "olharam": "olharam",
    "errar": "erra", "erro": "erro", "erramos": "erramu", "erram": "erram", "errou": "errou", "erraram": "erraram",
    "experimentar": "isprimentá", "experimento": "isprimentu", "experimenta": "isprimenta", "experimentamos": "isprimentãmu", "experimentam": "isprimentam", "experimentei": "isprimentei", "experimentou": "isprimentou", "experimentaram": "isprimentaram",
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
    "abus", "acab", "aceit", "acess", "acompanh", "acord", "adiant", "afast", "ajud", "alug", "amarr", "ameaç", "amol", "apag", "avanç", "apanh", "apront", "apress",
    "aproveit", "arm", "arrast", "arremess", "arrum", "assin", "atend", "atra", "atras", "atravess", "atualiz", "aument", "avanç", "avis", "bail", 
    "baix", "beij", "brinc", "busc", "caç", "calç", "carreg", "cham", "chut", "coç", "colet", "colid", "colh", "começ",  "comec", 
    "compr", "comunic", "control", "convid", "coloc", "copi", "corrig", "cort", "cozinh", "cumpr", "curt", "danc", 
    "danç", "descans", "desliz", "destac", "destru", "dit", "edit", "empreg", "empurr", "encontr", "encost", "enfeit", "engol", "entreg", "envi", "escolh", "escut", 
    "flert", "form", "grit", "guard", "imprim", "inund", "jog", "junt", "lav", "levant", "lig", "limp", "livr", "lut", "marc", 
    "met", "mex", "molh", "mord", "mostr", "mud", "olh", "peg", "proteg", "provoc", "reform", "reaj", "realiz", "receb", "reclam", "reduz", "reflet", "relax", "represent", "reserv", 
    "resolv", "respond", "restit", "romp", "segu", "serv", "sorr", "sub", "substitu", "suj", "surprend", 
    "traduz", "transform", "un", "us", "suport", "sustent", "torc", "trabalh", "transport", "trat", "troc", "utiliz", "vest", "viaj"
}

# Cognitive/Mental Verbs
COGNITIVE_VERB_ROOTS = {
    "ach", "acontec", "adivinh", "ador", "admir", "admit", "afirm", "agrad", "aguent", "alcanç", "amanhec", "amar", "analis", "anot", "aprend", "apresent", 
    "assist", "assum", "chec", "coment", "comet", "compar", "concord", "conhec", "consegu", "consig", "consist", 
    "consent", "consult", "contempl", "cont", "convers", "decid", "defend", "defin", "demor", "depend", "desej", "desenh", "desenvolv", 
    "descobr", "desist", "dirig", "discut", "divid", "entend", "esper", "esquec", "esqueç", "estud", "evit", 
    "foc", "gost", "imagin", "import", "indic", "inform", "inici", "insist", "instru", "lembr", "ment", "mint", "not", "observ", "opin", 
    "particip", "pens", "perceb", "pergunt", "permit", "persist", "preocup", "prepar", "pretend", "precis", 
    "procur", "promet", "represent", "sab", "sofr", "soub", "signific", "tent", "termin", "top", "verific", "visit"
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

def remove_accents(text):
    """
    Remove all accents from text while preserving case.
    Uses Unicode normalization to handle both precomposed and combining characters.
    """
    # Normalize to NFD (decompose): e.g. "ê" => "e" + combining ^
    text = unicodedata.normalize('NFD', text)
    # Remove all combining marks in the range U+0300 to U+036F
    text = re.sub(r'[\u0300-\u036f]', '', text)
    # Re-normalize back to NFC for consistency
    return unicodedata.normalize('NFC', text)

def restore_accents(word, template):
    """
    Restore accents to a word based on a template word.
    For example:
        word = "que", template = "quê" -> returns "quê"
        word = "por que", template = "por quê" -> returns "por quê"
    """
    # If lengths don't match, can't restore accents
    if len(word) != len(template):
        return word
        
    # Convert both to NFD to separate base characters and combining marks
    template = unicodedata.normalize('NFD', template)
    word = unicodedata.normalize('NFD', word)
    
    # For each character in the word, if the template has an accent at that position,
    # add it to the word
    result = []
    i = 0
    while i < len(word):
        # Get base character from word
        result.append(word[i])
        
        # If template has combining marks after this position, add them
        j = i + 1
        while j < len(template) and unicodedata.combining(template[j]):
            result.append(template[j])
            j += 1
        
        i += 1
        # Skip any combining marks in word
        while i < len(word) and unicodedata.combining(word[i]):
            i += 1
    
    # Convert back to NFC (composed form)
    return unicodedata.normalize('NFC', ''.join(result))

def merge_word_pairs(tokens):
    """
    Merge only if two adjacent tokens are both words (no punctuation in between)
    and the exact pair (in lowercase) is in WORD_PAIRS.
    """
    new_tokens = []
    i = 0
    explanations = []  # Move explanations list up here
    while i < len(tokens):
        word1, punct1 = tokens[i]

        # If this token is punctuation, just keep it and move on
        if not word1:
            new_tokens.append((word1, punct1))
            i += 1
            continue

        # Check if there is a "next" token to form a pair
        if i + 1 < len(tokens):
            word2, punct2 = tokens[i + 1]

            # If the next token is actually punctuation, we cannot form a pair
            if not word2:
                # Keep the current token (word1)
                new_tokens.append((word1, punct1))
                i += 1
                continue

            # Build a pair string in lowercase
            pair = f"{word1.lower().strip()} {word2.lower().strip()}"

            # Try an exact match against WORD_PAIRS
            if pair in WORD_PAIRS:
                # If matched, create a single merged token
                replacement = WORD_PAIRS[pair]
                # Merge punctuation from both tokens
                merged_punct = punct1 + punct2
                # Add to new_tokens
                new_tokens.append((replacement, merged_punct))
                explanations.append(f"Common pronunciation and usage: {pair} → {replacement}")
                # Skip the second token in the pair
                i += 2
            else:
                # No match, keep word1 as-is
                new_tokens.append((word1, punct1))
                i += 1
        else:
            # Last token, no pair to form
            new_tokens.append((word1, punct1))
            i += 1

    return new_tokens, explanations

def apply_phonetic_rules(word, next_word=None, next_next_word=None):
    """
    Apply Portuguese phonetic rules to transform a word.
    First checks a dictionary of pre-defined transformations,
    if not found, applies the rules in sequence.
    
    Args:
        word: The word to transform
        next_word: The next word in the sequence (optional), used for verb detection
    
    Returns:
        tuple: (transformed_word, explanation)
    """
    if not word:
        return '', ''
    
    # Initialize explanation list
    explanations = []

    # First check if word is in pre-defined dictionary
    lword = word.lower()

    # Check direct transformations first - these bypass the pipeline completely
    if lword in DIRECT_TRANSFORMATIONS:
        transformed = preserve_capital(word, DIRECT_TRANSFORMATIONS[lword])
        return transformed, f"Direct transformation: {word} → {transformed}"

    # Initialize transformed word and explanations
    transformed = lword
    explanations = []

    # Special handling for não before verbs
    if lword in ["não", "nao", "nãun", "nãu"]:
        if next_word:
            # Check if the next word is a pronoun
            pronouns = ["me", "te", "se", "nos", "vos", "lhe", "lhes", "o", "a", "os", "as", "lo", "la", "los", "las", "no", "na", "nos", "nas", "já"]
            if next_word.lower() in pronouns:
                # Check if the word after pronoun is a verb
                if next_next_word and is_verb(next_next_word):
                    return preserve_capital(word, "nu"), "Negation before pronoun+verb: não → num"
                elif is_verb(next_word):
                    return preserve_capital(word, "nu"), "Negation before verb: não → num"
            # If not a pronoun, check if it's a verb directly
            elif is_verb(next_word):
                return preserve_capital(word, "nu"), "Negation before verb: não → num"

    # Special handling for ucê before verbs
    if lword in ["ucê", "você", "voce"]:
        if next_word:
            # Check if the next word is a pronoun
            pronouns = ["me", "te", "se", "nos", "vos", "lhe", "lhes", "o", "a", "os", "as", "lo", "la", "los", "las", "no", "na", "nos", "nas", "nao", "não"]
            if next_word.lower() in pronouns:
                # Check if the word after pronoun is a verb
                if next_next_word and is_verb(next_next_word):
                    return preserve_capital(word, "cê"), "Pronoun before pronoun+verb: ucê → cê"
                elif is_verb(next_word):
                    return preserve_capital(word, "cê"), "Pronoun before verb: ucê → cê"
            # If not a pronoun, check if it's a verb directly
            elif is_verb(next_word):
                return preserve_capital(word, "cê"), "Pronoun before verb: ucê → cê"

    # Special handling for ucêis before verbs
    if lword in ["ucêis", "vocês", "voces`"]:
        if next_word:
            # Check if the next word is a pronoun
            pronouns = ["me", "te", "se", "nos", "vos", "lhe", "lhes", "o", "a", "os", "as", "lo", "la", "los", "las", "no", "na", "nos", "nas", "nao", "não"]
            if next_word.lower() in pronouns:
                # Check if the word after pronoun is a verb
                if next_next_word and is_verb(next_next_word):
                    return preserve_capital(word, "cêis"), "Pronoun before pronoun+verb: ucê → cê"
                elif is_verb(next_word):
                    return preserve_capital(word, "cêis"), "Pronoun before verb: ucê → cê"
            # If not a pronoun, check if it's a verb directly
            elif is_verb(next_word):
                return preserve_capital(word, "cêis"), "Pronoun before verb: ucê → cê"
 
    # Special handling for subject pronouns (eu, nós) before verbs or pronoun+verb
    if lword in ["eu", "nós"]:
        if next_word:
            # Check if the next word is a pronoun
            pronouns = ["me", "te", "se", "nos", "vos", "lhe", "lhes", "o", "a", "os", "as", "lo", "la", "los", "las", "no", "na", "nos", "nas", "já"]
            if next_word.lower() in pronouns:
                # Check if the word after pronoun is a verb
                if next_next_word and is_verb(next_next_word):
                    return preserve_capital(word, "[" + word + "]"), "Subject pronoun before pronoun+verb: add brackets"
            # If not a pronoun, check if it's a verb directly
            elif is_verb(next_word):
                return preserve_capital(word, "[" + word + "]"), "Subject pronoun before verb: add brackets"

    # Check if it's an irregular verb - if so, skip phonetic rules but allow combinations
    if lword in IRREGULAR_VERBS:
        transformed = IRREGULAR_VERBS[lword].lower()
        transformed = preserve_capital(word, transformed)
        return transformed, f"Irregular verb: {word} → {transformed}"

    # Check phonetic dictionary
    if lword in PHONETIC_DICTIONARY:
        transformed = PHONETIC_DICTIONARY[lword].lower()
        explanations.append(f"Dictionary: {word} → {transformed}")

    # Rule 1p: Transform initial 'en' to 'in'
    if transformed.startswith('en'):
        entrar_forms = ['entrar', 'entro', 'entra', 'entramos', 'entram', 'entrei', 'entrou', 'entraram', 'entrava', 'entravam']
        if not word.lower() in entrar_forms:
            transformed = 'in' + transformed[2:]
            explanations.append("Initial en → in")
    
    # Rule 2p: Transform initial 'des' to 'dis'
    if transformed.startswith('des'):
        transformed = 'dis' + transformed[3:]
        explanations.append("Transform initial 'des' to 'dis'")

    # Rule 3p: Transform 'ovo' and 'ovos' endings to 'ôvo' and 'óvos'
    if word.endswith('ovo'):
        transformed = word[:-3] + 'ôvo'
        explanations.append("Transform ending 'ovo' to 'ôvo'")
    elif word.endswith('ovos'):
        transformed = word[:-4] + 'óvos'
        explanations.append("Transform ending 'ovos' to 'óvos'")
    
    # Rule 4p: Transform 'ogo' and 'ogos' endings to 'ôgo' and 'ógos'
    if word.endswith('ogo'):
        transformed = word[:-3] + 'ôgo'
        explanations.append("Transform ending 'ogo' to 'ôgo'")
    elif word.endswith('ogos'):
        transformed = word[:-4] + 'ógos'
        explanations.append("Transform ending 'ogos' to 'ógos'")

    # Rule 5p: Transform 'oso' and 'osos' endings to 'ôso' and 'óso'
    if word.endswith('oso'):
        transformed = word[:-3] + 'ôso'
        explanations.append("Transform ending 'oso' to 'ôso'")
    elif word.endswith('osos'):
        transformed = word[:-4] + 'óso'
        explanations.append("Transform ending 'osos' to 'ósos'")

    # Rule 6p: Final unstressed vowels reduce ('o'->'u', 'os'->'us', 'e'->'i', 'es'->'is')
    if transformed.endswith('o'):
        transformed = transformed[:-1] + 'u'
        explanations.append("Final o → u")
    elif transformed.endswith('os'):
        transformed = transformed[:-2] + 'us'
        explanations.append("Final os → us")
    elif transformed.endswith('e'):
        transformed = transformed[:-1] + 'i'
        explanations.append("Final e → i")
    elif transformed.endswith('es'):
        transformed = transformed[:-2] + 'is'
        explanations.append("Final es → is")
    
    # Rule 7p: Initial 'es' becomes 'is'
    if transformed.startswith('es'):
        transformed = 'is' + transformed[2:]
        explanations.append("Initial es → is")
    
    # Rule 8p: 'ão' at the end becomes 'aum'
    if transformed.endswith('ão'):
        transformed = transformed[:-2] + 'ãun'
        explanations.append("ão → ãun")
    
    # Rule 9p: 's' between vowels becomes 'z'
    if re.search(r'([aeiouáéíóúâêîô úãẽĩõũ])s([aeiouáéíóúâêîô úãẽĩõũ])', transformed, re.IGNORECASE):
        transformed = re.sub(r'([aeiouáéíóúâêîô úãẽĩõũ])s([aeiouáéíóúâêîô úãẽĩõũ])', r'\1z\2', transformed, flags=re.IGNORECASE)
        explanations.append("s → z between vowels")
    
    # Rule 10p: Transform 'olh' to 'ôly'
    if not is_verb(word) and 'olh' in transformed:
        transformed = transformed.replace('olh', 'ôly')
        explanations.append("olh → ôly")
    
    # Rule 11p: 'lh' => 'ly'
    if 'lh' in transformed:
        transformed = transformed.replace('lh', 'ly')
        explanations.append("lh → ly")
    
    # Rule 12p: Final 'ou' becomes 'ô'
    if transformed.endswith('ou'):
        transformed = transformed[:-2] + 'ô'
        explanations.append("ou → ô")
    
    # Rule 13p: 'al' followed by a consonant becomes 'au'
    consonants = 'bcdfgjklmnpqrstvwxz'
    if re.search(r'al[' + consonants + ']', transformed):
        transformed = re.sub(r'al([' + consonants + '])', r'au\1', transformed)
        explanations.append("al+consonant → au")

    # Rule 14p: 'on' followed by a consonant becomes 'oun'
    if re.search(r'on[' + consonants + ']', transformed):
        transformed = re.sub(r'on(?!h)([' + consonants + '])', r'oun\1', transformed)
        explanations.append("on+consonant → oun")

    # Rule 15p: Final 'am' becomes 'aun'
    if transformed.endswith('am'):
        transformed = transformed[:-2] + 'ã'
        explanations.append("Final am → ã")
    
    # Rule 16p: Final 'em' becomes 'êin'
    if transformed.endswith('em'):
        transformed = transformed[:-2] + 'êin'
        explanations.append("Final em →êin")
    
    # Rule 17p: Final 'im' becomes 'in'
    #if transformed.endswith('im'):
    #    transformed = transformed[:-2] + 'in'
    #    explanations.append("Final im → in")
    
    # Rule 18p: Final 'om' becomes 'ôun'
    if transformed.endswith('om'):
        transformed = transformed[:-2] + 'ôun'
        explanations.append("Final om → ôun")

    # Rule 19p: Final 'um' becomes 'un'
    if transformed.endswith('um'):
        transformed = transformed[:-2] + 'un'
        explanations.append("Final um → un")
    
    # Rule 20p: Infinitive endings
    if is_verb(word):
        if transformed.endswith('ar'):
            transformed = transformed[:-2] + 'á'
            explanations.append("Infinitive ending: ar → á")
        elif transformed.endswith('er'):
            transformed = transformed[:-2] + 'ê'
            explanations.append("Infinitive ending: er →ê")
        elif transformed.endswith('ir'):
            transformed = transformed[:-2] + 'í'
            explanations.append("Infinitive ending: ir → í")

    # Rule 20.5p: Nós verb endings
    if is_verb(word):
        if transformed.endswith('amos'):
            transformed = transformed[:-4] + 'ãmu'
            explanations.append("Verb ending 'amos' → 'ãmu'")
        elif transformed.endswith('emos'):
            transformed = transformed[:-4] + 'êmu'
            explanations.append("Verb ending 'emos' → 'êmu'")
        elif transformed.endswith('imos'):
            transformed = transformed[:-4] + 'imu'
            explanations.append("Verb ending 'imos' → 'imu'")

    # Rule 21p: Remove initial 'h'
    if transformed.startswith('h'):
        transformed = transformed[1:]
        explanations.append("Remove initial h")
    
    # Rule 22p: Initial 'ex' becomes 'iz'
    if transformed.startswith('ex'):
        transformed = 'iz' + transformed[2:]
        explanations.append("Initial ex → iz")
    
    # Rule 23p: Initial 'pol' becomes 'pul'
    if transformed.startswith('pol'):
        transformed = 'pul' + transformed[3:]
        explanations.append("Initial pol → pul")
    
    # Rule 24p: Final 'ol' => 'óu'
    if transformed.endswith('ol'):
        transformed = transformed[:-2] + 'óu'
        explanations.append("Final ol → óu")
    
    # Rule 25p: Final 'l' => 'u'
    if transformed.endswith('l'):
        transformed = transformed[:-1] + 'u'
        explanations.append("Final l → u")
    
    # Rule 26p: 'l' before consonant becomes 'u'
    consonants = 'bcdfgjklmnpqrstvwxz'
    if re.search(f'l[{consonants}]', transformed):
        transformed = re.sub(f'l([{consonants}])', r'u\1', transformed)
        explanations.append("l before consonant → u")

    # Rule 27p: Insert 'i' between specific consonant pairs
    for p in ['bs', 'ps', 'pn', 'dv', 'pt', 'pç', 'dm', 'gn', 'tm', 'tn']:
        if p in transformed:
            transformed = transformed.replace(p, p[0] + 'i' + p[1])
            explanations.append(f"Insert i: {p} → {p[0]}i{p[1]}")
    
    # Rule 28p: Append 'i' to words ending in specific consonants
    if transformed.endswith(('d', 't', 'b', 'f', 'j', 'k', 'p', 'v')):
        transformed = transformed + 'i'
        explanations.append(f"Append i after final consonant")
    
    # Rule 29p: Replace final 'c' with 'ki'
    if transformed.endswith('c'):
        transformed = transformed[:-1] + 'ki'
        explanations.append("Final c → ki")
    
    # Rule 30p: Append 'ui' to words ending in 'g'
    if transformed.endswith('g'):
        transformed = transformed + 'ui'
        explanations.append("Append ui after final g")
    
    # Rule 31p: Transform 'eir' to 'er'
    if 'eir' in transformed:
        transformed = transformed.replace('eir', 'êr')
        explanations.append("eir →êr")
    
    # Rule 32p: Transform initial 'ou' to 'ô'
    if transformed.startswith('ou'):
        transformed = 'ô' + transformed[2:]
        explanations.append("Transform initial 'ou' to 'ô'")
    
    # Rule 33p: Transform initial 'sou' to 'sô'
    if transformed.startswith('sou'):
        transformed = 'sô' + transformed[3:]
        explanations.append("Transform initial 'sou' to 'sô'")
    
    # Rule 34p: Transform initial 'des' to 'dis'
    if transformed.startswith('des'):
        transformed = 'dis' + transformed[3:]
        explanations.append("Transform initial 'des' to 'dis'")
    
    # Rule 35p: Transform 'ora' and 'oras' endings to 'óra' and 'óras'
    if transformed.endswith('ora'):
        transformed = transformed[:-3] + 'óra'
        explanations.append("Transform ending 'ora' to 'óra'")
    elif transformed.endswith('oras'):
        transformed = transformed[:-4] + 'óras'
        explanations.append("Transform ending 'oras' to 'óras'")

    # Rule 36p: Transform final 'ês' to 'êis'
    if transformed.endswith('ês'):
        transformed = transformed[:-2] + 'êis'
        explanations.append("Final 'ês' becomes 'êis'")
    
    # Preserve capitalization
    transformed = preserve_capital(word, transformed)
    
    explanation = " + ".join(explanations) if explanations else "No changes needed"
    return transformed, explanation

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
    1) Tokenize the input.
    2) Merge known word pairs from WORD_PAIRS before single-word phonetic rules.
    3) Apply single-word transformations (apply_phonetic_rules).
    4) Run multiple passes of inline combination rules (the big if/elif
       for 'r' + vowel, 'a' + vowel, 'sz' + vowel, etc.).
    5) Reassemble into the final text.
    """
    print("DEBUG: Input text =", repr(text))
    try:
        # ---------------------------------------------------------------------
        # 1) Normalize non-breaking spaces (optional)
        # ---------------------------------------------------------------------
        text = text.replace('\xa0', ' ')

        # ---------------------------------------------------------------------
        # 2) Tokenize
        # ---------------------------------------------------------------------
        tokens = tokenize_text(text)

        # ---------------------------------------------------------------------
        # 3) Merge word pairs first (e.g. "por que" -> "purkê")
        # ---------------------------------------------------------------------
        tokens, word_pair_explanations = merge_word_pairs(tokens)

        # ---------------------------------------------------------------------
        # 4) Apply single-word phonetic transformations to each token
        #    (including those merged into single tokens)
        # ---------------------------------------------------------------------
        transformed_tokens = []
        explanations = word_pair_explanations  # Start with word pair explanations
        for i, (word, punct) in enumerate(tokens):
            if word:
                next_word = tokens[i+1][0] if (i+1 < len(tokens)) else None
                next_next_word = tokens[i+2][0] if (i+2 < len(tokens)) else None

                # Apply dictionary + phonetic rules to this single word
                new_word, explanation = apply_phonetic_rules(word, next_word, next_next_word)
                if explanation != "No changes needed":
                    explanations.append(f"{word}: {explanation}")

                transformed_tokens.append((new_word, punct))
            else:
                # This token is punctuation-only => just keep it
                transformed_tokens.append((word, punct))

        # ---------------------------------------------------------------------
        # Capture state after transformations but before combinations
        # ---------------------------------------------------------------------
        before_combinations = reassemble_tokens_smartly(transformed_tokens)

        # ---------------------------------------------------------------------
        # 5) Now apply inline combination rules in a loop until no more merges
        #    (the big if/elif checks for 'r'+vowel, 'a'+vowel, 'sz'+vowel, etc.)
        # ---------------------------------------------------------------------
        combination_explanations = []
        made_combination = True  # Start as True to enter the loop

        while made_combination:
            made_combination = False  # Reset for this iteration
            new_tokens = []
            i = 0

            while i < len(transformed_tokens):
                if i < len(transformed_tokens) - 1:
                    word1, punct1 = transformed_tokens[i]
                    word2, punct2 = transformed_tokens[i + 1]

                    # Only try to combine if both tokens are words (no punctuation)
                    if word1 and word2 and not punct1:
                        # We'll define a small helper string of vowels
                        vowels = 'aeiouáéíóúâêîô úãẽĩõũy'

                        combined = None  # We'll set this if a merge happens
                        rule_explanation = None

                        # Try each combination rule
                        if not made_combination:
                            # Rules for combining words
                            # 1c: 'r' + vowel
                            if word1[-1] == 'r' and word2[0] in vowels:
                                combined = word1 + word2
                                rule_explanation = f"1c: {word1} + {word2} → {combined} (Keep 'r' when joining with vowel)"

                            # 2c: 'n' + 'm'
                            elif word1.endswith('n') and word2.startswith('m'):
                                combined = word1[:-1] + word2
                                rule_explanation = f"2c: {word1} + {word2} → {combined} (Drop 'n' before 'm')"

                            # 3c: Same letter/sound
                            elif word1[-1].lower() == word2[0].lower():
                                combined = word1[:-1] + word2
                                rule_explanation = f"3c: {word1} + {word2} → {combined} (Join same letter/sound)"

                            # 4c: 'a' + vowel
                            elif word1[-1] == 'a' and word2[0] in vowels:
                                combined = word1[:-1] + word2
                                rule_explanation = f"4c: {word1} + {word2} → {combined} (Join 'a' with following vowel)"

                            # 5c: 'u' + vowel
                            elif word1[-1] == 'u' and word2[0] in vowels:
                                if word1.endswith(('eu', 'êu')):
                                    combined = word1 + word2
                                    rule_explanation = f"5c.1: {word1} + {word2} → {combined} (Keep 'eu/êu' before vowel)"
                                else:
                                    combined = word1[:-1] + word2
                                    rule_explanation = f"5c.2: {word1} + {word2} → {combined} (Drop 'u' before vowel)"

                            # 6c: 's/z' + vowel
                            elif word1[-1] in 'sz' and word2[0] in vowels:
                                combined = word1[:-1] + 'z' + word2
                                rule_explanation = f"6c: {word1} + {word2} → {combined} ('s' between vowels becomes 'z')"

                            # 7c: 'm' + vowel
                            elif word1[-1] == 'm' and word2[0] in vowels:
                                combined = word1 + word2
                                rule_explanation = f"7c: {word1} + {word2} → {combined} (Join 'm' with following vowel)"

                            # 8c: 'ia' + 'i'
                            elif word1.endswith('ia') and word2.startswith('i'):
                                combined = word1[:-2] + word2
                                rule_explanation = f"8c: {word1} + {word2} → {combined} (Drop 'ia' before 'i')"

                            # 9c: 'i' + 'e/é/ê'
                            elif word1.endswith('i') and word2[0] in 'eéê':
                                combined = word1[:-1] + word2
                                rule_explanation = f"9c: {word1} + {word2} → {combined} (Drop 'i' before e/é/ê)"

                            # 10c: 'á' + 'a'
                            elif word1.endswith('á') and word2.startswith('a'):
                                combined = word1[:-1] + word2
                                rule_explanation = f"10c: {word1} + {word2} → {combined} (Convert 'á' to 'a')"

                            # 11c: 'ê' + 'é'
                            elif word1.endswith('ê') and word2.startswith('é'):
                                combined = word1[:-1] + word2
                                rule_explanation = f"11c: {word1} + {word2} → {combined} (Use é)"

                            # 12c: 'yn' + 'm'
                            elif word1.endswith('yn') and word2.startswith('m'):
                                combined = word1[:-2] + 'y' + word2
                                rule_explanation = f"12c: {word1} + {word2} → {combined} (yn + m → ym)"

                            # 13c: 'a' + 'i/e' with special cases
                            elif word1.endswith(('a', 'ã')) and word2[0] in 'ie':
                                if word1.endswith('ga'):
                                    combined = word1[:-2] + 'gu' + word2
                                    rule_explanation = f"13c.1: {word1} + {word2} → {combined} (ga + i/e → gui/gue)"
                                elif word1.endswith('ca'):
                                    combined = word1[:-2] + 'k' + word2
                                    rule_explanation = f"13c.2: {word1} + {word2} → {combined} (ca + i/e → ki/ke)"
                                else:
                                    combined = word1[:-1] + word2
                                    rule_explanation = f"13c.3: {word1} + {word2} → {combined} (Drop 'a' before i/e)"

                            # 14c: vowel + vowel
                            elif word1[-1] in vowels and word2[0] in vowels:
                                combined = word1 + word2
                                rule_explanation = f"14c: {word1} + {word2} → {combined} (Join vowels)"

                            # 15c: Same letter/sound (catch-all)
                            elif word1[-1].lower() == word2[0].lower():
                                combined = word1[:-1] + word2
                                rule_explanation = f"15c: {word1} + {word2} → {combined} (Join same letter/sound)"

                            # If we found a combination to apply
                            if combined is not None and rule_explanation is not None:
                                print(f"DEBUG: Found combination: {rule_explanation}")
                                combination_explanations.append(rule_explanation)
                                new_tokens.append((combined, punct2))
                                i += 2
                                made_combination = True
                                continue

                # If no combination was applied, keep the current token and move on
                new_tokens.append(transformed_tokens[i])
                i += 1

            # Update tokens for next iteration
            if made_combination:
                transformed_tokens = new_tokens

        # ---------------------------------------------------------------------
        # 6) Reassemble the final text
        # ---------------------------------------------------------------------
        after_combinations = reassemble_tokens_smartly(transformed_tokens)

        return {
            'before': before_combinations,
            'after': after_combinations,
            'explanations': explanations,
            'combinations': combination_explanations
        }

    except Exception as e:
        print(f"Error in transform_text: {e}")
        traceback.print_exc()
        return {
            'before': text,
            'after': text,
            'explanations': [f"Error: {str(e)}"],
            'combinations': []
        }

def convert_text(text):
    """Convert Portuguese text to its phonetic representation with explanations."""
    result = transform_text(text)
    return result

def main():
    # Set UTF-8 encoding for stdout
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Check if file is provided as a command-line argument
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            input_text = f.read()
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
        print("Word Transformations:")
        print(result['before'])
        print(result['after'])
        for explanation in result['explanations']:
            print(explanation)
        print("\nWord Combinations:")
        for combination in result['combinations']:
            print(combination)
        print()

if __name__ == "__main__":
    main()