from enum import Enum


class Maker(str, Enum):
    ALL = 'ALL'
    PALBIT = 'PALBIT'
    YG1 = 'YG-1'
    VERGNANO = 'VERGNANO'
    VARGUS = 'VARGUS'
    SANHOG = 'SANHOG'
    OMAP = 'OMAP'
    NANOLOY = 'NANOLOY'
    LIKON = 'LIKON'
    HORN = 'HORN'
    HELION = 'HELION'
    GABRIEL_MAUVAIS = 'GABRIEL_MAUVAIS'
    FRESAL = 'FRESAL'
    DEREK = 'DEREK'
    BRICE = 'BRICE'
    Bribase = 'Bribase'
    ASKUP = 'ASKUP'
    ILIX = 'ILIX'


class Filter(str, Enum):
    string_search = 'string_search'
    ngram_search = 'ngram_search'


class Table(str, Enum):
    tool = 'Инструмент'
    brand = 'Бренд'
    analog = 'Аналог'
    analog_brand = 'Бренд аналога'
