def get_stem_polarity(pillar: str) -> str:
    if not pillar:
        return 'YANG'
    first_char = pillar.strip()[0]
    yang_stems = ['甲', '丙', '戊', '庚', '壬']
    if first_char in yang_stems:
        return 'YANG'
    return 'YIN'
