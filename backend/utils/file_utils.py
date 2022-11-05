import uuid

import aiofiles
import pandas as pd
from fastapi import HTTPException

from core.config import BASE_DIR
from utils.enums import Table

xlsx_con_type = ('application/vnd.openxmlformats'
                 '-officedocument.spreadsheetml.sheet')
zip_con_type = 'application/zip'

xlsx_headers = {
    'Content-Disposition': 'attachment; filename="response.xlsx"'
}

column_width_conf = [(0, 0, 6), (1, 1, 45), (2, 2, 20), (3, 3, 45), (4, 4, 20)]
result_sheet_name = 'Analogs'


def verify_xlsx_type(xlsx_file):
    if xlsx_file.content_type != xlsx_con_type:
        raise HTTPException(400, detail='Invalid document type')


def verify_zip_type(zip_file):
    if zip_file.content_type != zip_con_type:
        raise HTTPException(400, detail='Invalid document type')


def get_xlsx_path() -> str:
    file_name = str(uuid.uuid4()) + '.xlsx'
    file_path = str(BASE_DIR.joinpath('file_storage') / file_name)
    return file_path


async def save_file(file, file_path: str):
    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(await file.read())


def get_base_names_xlsx(file_path: str):
    with open(file_path, 'rb') as f:
        excel = pd.read_excel(f, 0, keep_default_na=False)
        return excel['Инструмент'].values


def save_xlsx_analogs(
        file_path: str, result_file_path: str, analogs: list, makers: list,
        bad: list):
    with open(file_path, 'rb') as f:
        excel = pd.read_excel(f, 0, keep_default_na=False)
        new_frame = pd.DataFrame()
        new_frame[Table.tool] = excel[Table.tool].values
        new_frame[Table.brand] = excel[Table.brand].values
        new_frame[Table.analog] = analogs
        new_frame[Table.analog_brand] = makers
        writer = pd.ExcelWriter(result_file_path, engine='xlsxwriter')
        workbook = writer.book  # noqa
        cell_format = workbook.add_format({'bg_color': '#F4A460'})
        new_frame.to_excel(writer, sheet_name=result_sheet_name)
        worksheet = writer.sheets[result_sheet_name]
        for params in column_width_conf:
            worksheet.set_column(*params)
        for row in bad:
            worksheet.write(row + 1, 3, new_frame.iloc[row, 2], cell_format)
        writer.save()


def get_columns_locs(pd_dataframe: pd.DataFrame):
    locs = {
        'base_col_num': pd_dataframe.columns.get_loc(Table.tool),
        'base_maker_col_num': pd_dataframe.columns.get_loc(Table.brand),
        'analog_col_num': pd_dataframe.columns.get_loc(Table.analog),
        'analog_maker_col_num': pd_dataframe.columns.get_loc(
            Table.analog_brand),
    }
    return locs


def verify_required_fields(file: str, fields: list[Table]):
    with open(file, 'rb') as f:
        excel = pd.read_excel(f, 0, keep_default_na=False)
        names = excel.columns.tolist()
        for field in fields:
            if field not in names:
                return False
        return True
