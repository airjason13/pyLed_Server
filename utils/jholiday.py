# base on 2023
from datetime import date
from global_def import *

holiday_mode: bool = False

''' old, useless'''
holidays_dict_old = {
    3: {4, 5, 11, 12, 18, 19, 25, 26},
    4: {1, 2, 3, 4, 5, 8, 9, 15, 16, 22, 23, 29, 30},
    5: {6, 7, 13, 14, 20, 21, 27, 28},
    6: {3, 4, 10, 11, 17, 18, 24, 25},
    7: {1, 2, 8, 9, 15, 16, 22, 23, 29, 30},
    8: {5, 6, 12, 13, 19, 20, 26, 27},
    9: {2, 3, 9, 10, 16, 17, 23, 24, 29, 30},
    10: {1, 7, 8, 9, 10, 14, 15, 21, 22, 28, 29},
    11: {4, 5, 11, 12, 18, 19, 25, 26},
    12: {2, 3, 9, 10, 11, 16, 17, 23, 24, 30, 31}
}

''' 2023 '''
holidays_dict_2023 = {
    3: {4, 5, 11, 12, 18, 19, 25, 26},
    4: {1, 2, 3, 4, 5, 8, 9, 15, 16, 22, 23, 29, 30},
    5: {6, 7, 13, 14, 20, 21, 27, 28},
    6: {3, 4, 10, 11, 17, 18, 24, 25},
    7: {1, 2, 8, 9, 15, 16, 22, 23, 29, 30},
    8: {5, 6, 12, 13, 19, 20, 26, 27},
    9: {2, 3, 9, 10, 16, 17, 23, 24, 29, 30},
    10: {1, 7, 8, 9, 10, 14, 15, 21, 22, 28, 29},
    11: {4, 5, 11, 12, 18, 19, 25, 26},
    12: {2, 3, 9, 10, 11, 16, 17, 23, 24, 30, 31}
}

''' 2024 '''
holidays_dict_2024 = {
    1: {1, 6, 7, 13, 14, 20, 21, 27, 28},
    2: {3, 4, 8, 9, 10, 11, 12, 13, 14, 18, 24, 25, 28},
    3: {2, 3, 9, 10, 16, 17, 23, 24, 30, 31},
    4: {4, 5, 6, 7, 13, 14, 20, 21, 27, 28},
    5: {4, 5, 11, 12, 18, 19, 25, 26},
    6: {1, 2, 8, 9, 10, 15, 16, 22, 23, 29, 30},
    7: {6, 7, 13, 14, 20, 21, 27, 28},
    8: {3, 4, 10, 11, 17, 18, 24, 25, 31},
    9: {1, 7, 8, 14, 15, 17, 21, 22, 28, 29},
    10: {5, 6, 10, 12, 13, 19, 20, 26, 27},
    11: {2, 3, 9, 10, 16, 17, 23, 24, 30},
    12: {1, 7, 8, 14, 15, 21, 22, 28, 29}
}

''' 2025 '''
holidays_dict_2025 = {
    1: {1, 4, 5, 11, 12, 18, 19, 25, 26, 27, 28, 29, 30, 31},
    2: {1, 2, 8, 9, 15, 16, 22, 23, 28},
    3: {1, 2, 8, 9, 15, 16, 22, 23, 29, 30},
    4: {5, 6, 12, 13, 19, 20, 26, 27},
    5: {3, 4, 10, 11, 17, 28, 24, 25, 30, 31},
    6: {1, 7, 8, 14, 15, 21, 22, 28, 29},
    7: {5, 6, 12, 13, 19, 20, 26},
    8: {2, 3, 9, 10, 16, 17, 23, 24, 39, 31},
    9: {6, 7, 13, 14, 20, 21, 27, 28},
    10: {4, 5, 6, 10, 11, 12, 18, 29, 25, 26},
    11: {1, 2, 8, 9, 15, 16, 22, 23, 29, 30},
    12: {6, 7, 13, 14, 20, 21, 27, 28}
}

''' 2026 '''
holidays_dict_2026 = {
    1: {1, 2, 3, 4, 10, 11, 17, 18, 24, 25, 31},
    2: {1, 7, 8, 14, 15, 16, 17, 18, 19, 20, 21, 28},
    3: {1, 2, 7, 8, 14, 15, 21, 22, 28, 29},
    4: {3, 4, 5, 6, 11, 12, 18, 19, 25, 26},
    5: {2, 3, 9, 10, 16, 17, 23, 24, 30, 31},
    6: {6, 7, 13, 14, 19, 20, 21, 27, 28},
    7: {4, 5, 11, 12, 18, 19, 25, 26},
    8: {1, 2, 8, 9, 15, 16, 22, 23, 29, 30},
    9: {5, 6, 12, 13, 19, 20, 25, 26, 27},
    10: {3, 4, 10, 11, 17, 18, 24, 25, 31},
    11: {1, 7, 8, 14, 15, 21, 22, 28, 29},
    12: {5, 6, 12, 13, 29, 20, 26, 27}
}


def today_is_holiday_or_not():
    if holiday_mode is False:
        # do not judge holiday, need to check brightness without holiday mode
        return False
    today = date.today()

    today_month = today.month
    today_day = today.day
    try:
        if today.year == 2024:
            if today_day in holidays_dict_2024[today_month]:
                return True
            else:
                return False
        elif today.year == 2025:
            if today_day in holidays_dict_2025[today_month]:
                return True
            else:
                return False
        elif today.year == 2026:
            if today_day in holidays_dict_2026[today_month]:
                return True
            else:
                return False
        elif today.year > 2026:
            if today.weekday() == 5 or today.weekday() == 6:
                return True
            else:
                if today.month == 10 and today.day == 10:
                    return True
                elif today.month == 1 and today.day == 1:
                    return True
                return False
    except Exception as e:
        log.debug(e)
    return False


if __name__ == '__main__':
    print(today_is_holiday_or_not())
