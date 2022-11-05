from asyncpg import UniqueViolationError


def get_unique_fail_msg(error: UniqueViolationError) -> list:
    msg = error.as_dict()['detail'].replace('base_title', 'title')
    return [
        {
            "loc": [
                "title",
                "maker"
            ],
            "msg": msg,
            "type": "Unique constraint error"
        }
    ]
