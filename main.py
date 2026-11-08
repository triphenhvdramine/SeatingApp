from ortools.sat.python import cp_model
from openpyxl import load_workbook
import numpy as np

wb = load_workbook('guest_seating_preferences_500.xlsx')
sh = wb.active

allVisitors = {}
visitorSize = {}
visitorPrefs = {}

for col in sh.iter_cols(min_col=1, max_col=1, min_row=2):
    for cell in col:
        allVisitors[cell.value] = cell.row-1

lastKey = sh.max_row

for col in sh.iter_cols(min_col=2, max_col=2, min_row=2):
    for cell in col:
        friends = [friend.strip() for friend in cell.value.split(",")]
        for i in range(len(friends)):
            if(friends[i] not in allVisitors):
                allVisitors[friends[i]] = lastKey
                lastKey += 1

for col in sh.iter_cols(min_col=1, max_col=1, min_row=2):
    for cell in col:
        adjCell = sh.cell(row=cell.row, column=2)
        valGuest = cell.value
        valFriends = adjCell.value

        guestNum = allVisitors.get(valGuest)
        friendsNames = [friend.strip() for friend in valFriends.split(",")]
        friendsNum = tuple([allVisitors.get(friend) for friend in friendsNames])

        visitorPrefs[guestNum] = friendsNum

for col in sh.iter_cols(min_col=3, max_col=3, min_row=2):
    for cell in col:
        visitorSize[cell.row-1] = cell.value
