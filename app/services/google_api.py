from datetime import datetime, timedelta
from typing import List

from aiogoogle import Aiogoogle
from app.core.config import settings
from app.core.consts import (
    CREATE_VERSION,
    UPDATE_VERSION,
    USER_PERMISSION_VERSION,
    LOCALE,
    SHEET_TYPE,
    TITLE,
    ROW_COUNT,
    COLUMN_COUNT,
    SHEET_ID,
)


FORMAT = '%Y/%m/%d %H:%M:%S'


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    datetime_now = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', CREATE_VERSION)
    spreadsheet_body = {
        'properties': {
            'title': f'Отчёт от {datetime_now}',
            'locale': 'ru_RU',
        },
        'sheets': [{
            'properties': {
                'sheetType': SHEET_TYPE,
                'sheetId': SHEET_ID,
                'title': TITLE,
                'gridProperties': {
                    'rowCount': ROW_COUNT,
                    'columnCount': COLUMN_COUNT,
                }
            }
        }]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body),
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
    spreadsheet_id: str,
    wrapper_services: Aiogoogle,
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email,
    }
    service = await wrapper_services.discover(
        'drive',
        USER_PERMISSION_VERSION,
    )
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id",
        )
    )


async def spreadsheets_update_value(
    spreadsheet_id: str,
    projects: List,
    wrapper_services: Aiogoogle,
) -> None:
    RANGE = 'A1:E30'

    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', UPDATE_VERSION)
    table_values = [
        ['Отчёт от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание'],
    ]
    for project in projects:
        new_row = [
            str(project['name']),
            str(timedelta(project['completion'])),
            str(project['description']),
        ]
        table_values.append(new_row)

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values,
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=RANGE,
            valueInputOption='USER_ENTERED',
            json=update_body,
        )
    )
