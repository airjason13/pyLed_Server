# base on 2023
from datetime import date
#from global_def import *

holiday_mode = True

holidays_dict = {3: {4, 5, 11, 12, 18, 19, 25, 26},
                 4: {1, 2, 3, 4, 5, 8, 9, 15, 16, 22, 23, 29, 30},
                 5: {6, 7, 13, 14, 20, 21, 27, 28},
                 6: {3, 4, 10, 11, 17, 18, 24, 25},
                 7: {1, 2, 8, 9, 15, 16, 22, 23, 29, 30},
                 8: {5, 6, 12, 13, 19, 20, 26, 27},
                 9: {2, 3, 9, 10, 16, 17, 23, 24, 29, 30},
                 10: {1, 7, 8, 9, 10, 14, 15, 21, 22, 28, 29},
                 11: {4, 5, 11, 12, 18, 19, 25, 26},
                 12: {2, 3, 9, 10, 11, 16, 17, 23, 24, 30, 31}}


def today_is_holiday_or_not():
	# holiday_mode in  global_def.py
	if holiday_mode is False:
		# do not judge holiday, need to check brightness without holiday mode
		return False
	today = date.today()
	today_month = today.month
	today_day = today.day
	if today_day in holidays_dict[today_month]:
		return True # holiday
	else:
		return False # work day

if __name__ == '__main__':
	print(today_is_holiday_or_not())