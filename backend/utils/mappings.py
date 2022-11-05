from models.es_models.es_tool import DataToolIn
from utils.enums import Maker
from utils.transliterate import delete_ru_literals_all, delete_symbols

makers_map = {
    Maker.PALBIT: lambda x: DataToolIn(
        article=x[0], name=x[1], maker=Maker.PALBIT, position_state=x[4],
        product_line=x[6]),
    Maker.YG1: lambda x: DataToolIn(
        article=x[0], name=x[0],
        description=(x[1] + x[5]
                     if x[5] != '-' else x[1]),
        search_field=delete_symbols(
            delete_ru_literals_all(
                x[1] + x[5]
                if x[5] != '-' else x[1])),
        product_line=x[3], maker=Maker.YG1),
    Maker.VERGNANO: lambda x: DataToolIn(
        article=x[0], name=x[1], maker=Maker.VERGNANO),
    Maker.VARGUS: lambda x: DataToolIn(
        article=x[0], name=x[1], maker=Maker.VARGUS),
    Maker.SANHOG: lambda x: DataToolIn(
        article=x[0], name=x[1], description=x[2], maker=Maker.SANHOG),
    Maker.OMAP: lambda x: DataToolIn(name=x[0], maker=Maker.OMAP),
    Maker.NANOLOY: lambda x: DataToolIn(name=x[0], maker=Maker.NANOLOY),
    Maker.LIKON: lambda x: DataToolIn(name=x[0], maker=Maker.LIKON),
    Maker.HORN: lambda x: DataToolIn(
        article=x[0], name=x[1], maker=Maker.HORN),
    Maker.HELION: lambda x: DataToolIn(
        article=x[0], name=x[0], description=x[1], maker=Maker.HELION),
    Maker.GABRIEL_MAUVAIS: lambda x: DataToolIn(
        name=x[1], description=x[3], maker=Maker.GABRIEL_MAUVAIS),
    Maker.FRESAL: lambda x: DataToolIn(
        article=x[0], name=x[0], description=x[1], maker=Maker.FRESAL),
    Maker.DEREK: lambda x: DataToolIn(name=x[0], maker=Maker.DEREK),
    Maker.BRICE: lambda x: DataToolIn(
        article=x[0], name=x[1], description=x[2], maker=Maker.BRICE),
    Maker.Bribase: lambda x: DataToolIn(
        article=x[0], name=x[1], description=x[2], maker=Maker.Bribase),
    Maker.ASKUP: lambda x: DataToolIn(name=x[0], maker=Maker.ASKUP),
    Maker.ILIX: lambda x: DataToolIn(
        article=x[0], name=str(x[1]).strip() + ' ' + str(x[2]).strip(),
        description=str(x[3]).strip(), maker=Maker.ILIX),
}
