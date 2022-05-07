import re
from typing import Optional

MAX_RU_LITER_COUNT_BEGIN = 4
RU_PATTERN_DEL_BEGIN = r'^[А-Яа-я ]'
RU_PATTERN_DEL_END = r'[А-Яа-я ]$'
RU_PATTERN_DEL_ALL = r'[А-Яа-я]'
SYMBOLS = r'[\.\,\-\\\|\/ ]'
MATCH_MAP = {
    'А': 'A',
    'В': 'B',
    'Е': 'E',
    'К': 'K',
    'М': 'M',
    'Н': 'H',
    'О': 'O',
    'Р': 'P',
    'С': 'C',
    'Т': 'T',
    'Х': 'X'
}
RUS_LITERALS = r'[' + ''.join(MATCH_MAP.keys()) + ']'


def convert_case(match_obj: re.Match):
    return MATCH_MAP[match_obj.group()]


def delete_ru_literals_begin(text: str) -> str:
    return re.sub(RU_PATTERN_DEL_BEGIN, '', text)


def delete_ru_literals_end(text: str) -> str:
    return re.sub(RU_PATTERN_DEL_END, '', text)


def delete_ru_literals_all(text: str) -> str:
    return re.sub(RU_PATTERN_DEL_ALL, '', text)


def delete_symbols(text: Optional[str]) -> Optional[str]:
    return re.sub(SYMBOLS, '', str(text))


def get_ru_literal_count_begin(text: str) -> int:
    result = re.findall(RU_PATTERN_DEL_BEGIN, text)
    count = len(result)
    return count if count == 0 else len(*result)


def transliterate(text: str) -> str:
    res = re.sub(RUS_LITERALS, convert_case, text)
    return res


def stringify(text: str) -> str:
    return '*' + '*'.join(text) + '*'


def prepare_text(text: str) -> str:
    text = delete_symbols(text).lower()
    text = delete_ru_literals_all(text)
    return text
