from datetime import datetime


def year_processor():
    year = datetime.now().year
    return dict(year=year)
