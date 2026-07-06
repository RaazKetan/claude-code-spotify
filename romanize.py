#!/usr/bin/env python3
"""Phonetic romanization of Indic lyrics (Gurmukhi / Devanagari) to Latin, so
Punjabi & Hindi lines are singable in English letters. Stdlib only, offline.

Abugida rules: a bare consonant carries an inherent 'a'; a vowel sign (matra)
replaces it; virama removes it; addak doubles the next consonant; anusvara /
tippi / bindi nasalize to 'n'. Not a scholarly transliteration — good enough to
read along.
"""

# --- consonants (base sound, inherent 'a' added by the algorithm) ---
CONS = {
    # Gurmukhi
    'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'ng',
    'ਚ': 'ch', 'ਛ': 'chh', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': 'ny',
    'ਟ': 't', 'ਠ': 'th', 'ਡ': 'd', 'ਢ': 'dh', 'ਣ': 'n',
    'ਤ': 't', 'ਥ': 'th', 'ਦ': 'd', 'ਧ': 'dh', 'ਨ': 'n',
    'ਪ': 'p', 'ਫ': 'ph', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
    'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': 'r',
    'ਸ': 's', 'ਹ': 'h',
    # Devanagari
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
    'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
}

# base consonant + nukta -> modified sound
NUKTA_MAP = {
    'ਸ਼': 'sh', 'ਖ਼': 'kh', 'ਗ਼': 'gh', 'ਜ਼': 'z', 'ਫ਼': 'f', 'ਲ਼': 'l',
    'क़': 'q', 'ख़': 'kh', 'ग़': 'gh', 'ज़': 'z', 'फ़': 'f', 'ड़': 'r', 'ढ़': 'rh',
}

IVOWEL = {
    'ਅ': 'a', 'ਆ': 'aa', 'ਇ': 'i', 'ਈ': 'ee', 'ਉ': 'u', 'ਊ': 'oo',
    'ਏ': 'e', 'ਐ': 'ai', 'ਓ': 'o', 'ਔ': 'au',
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
    'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'ऋ': 'ri',
}

MATRA = {
    'ਾ': 'aa', 'ਿ': 'i', 'ੀ': 'ee', 'ੁ': 'u', 'ੂ': 'oo',
    'ੇ': 'e', 'ੈ': 'ai', 'ੋ': 'o', 'ੌ': 'au',
    'ा': 'aa', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
    'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ृ': 'ri',
}

DIGITS = {**{chr(0x0A66 + i): str(i) for i in range(10)},   # Gurmukhi ੦-੯
          **{chr(0x0966 + i): str(i) for i in range(10)}}   # Devanagari ०-९

VIRAMA = {'੍', '्'}
NASAL = {'ੰ', 'ਂ', 'ਃ', 'ं', 'ँ', 'ः'}
ADDAK = {'ੱ'}
NUKTA = {'਼', '़'}


def _is_indic(ch):
    return '਀' <= ch <= '੿' or 'ऀ' <= ch <= 'ॿ'


def romanize(text):
    if not text or not any(_is_indic(c) for c in text):
        return text  # nothing to do — leave Latin lyrics untouched

    out, i, n, dbl = [], 0, len(text), False
    while i < n:
        ch = text[i]
        if ch in CONS:
            base = CONS[ch]
            i += 1
            if i < n and text[i] in NUKTA:
                base = NUKTA_MAP.get(ch + text[i], base)
                i += 1
            if dbl:
                base = base + base
                dbl = False
            if i < n and text[i] in MATRA:
                vowel = MATRA[text[i]]; i += 1
            elif i < n and text[i] in VIRAMA:
                vowel = ''; i += 1
            else:
                vowel = 'a'  # inherent
            out.append(base + vowel)
        elif ch in IVOWEL:
            out.append(IVOWEL[ch]); i += 1
        elif ch in ADDAK:
            dbl = True; i += 1
        elif ch in NASAL:
            out.append('n'); i += 1
        elif ch in DIGITS:
            out.append(DIGITS[ch]); i += 1
        elif ch in VIRAMA or ch in NUKTA:
            i += 1  # stray combiner
        else:
            out.append(ch); i += 1  # spaces, Latin, punctuation
    return ''.join(out)


if __name__ == '__main__':
    # Gurmukhi (the Coke Studio line) + Devanagari sanity checks.
    a = romanize('ਕੀ ਹੜੀ ਆ ਰਕਾ ਨ ਕਰ ਜਾ ਦਰਛੀ ਅ?')
    assert a == 'kee haree aa rakaa na kara jaa darachhee a?', a
    assert romanize('ਪੱਕਾ') == 'pakkaa', romanize('ਪੱਕਾ')          # addak
    assert romanize('मैं तेरा') == 'main teraa', romanize('मैं तेरा')  # Devanagari + nasal
    assert romanize('Beautiful Things') == 'Beautiful Things'        # Latin untouched
    print('ok')
