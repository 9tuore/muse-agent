tell application "Calendar"
    set cs to calendars whose name is "工作"
    if (count of cs) is not 1 then error "Calendar count mismatch"
    set targetCalendar to item 1 of cs
    set matches to (every event of targetCalendar whose uid is "CDBB19C1-1806-4F53-94E9-6FC1ED7D659C")
    if (count of matches) is not 1 then error "UID count mismatch; no deletion"
    set targetEvent to item 1 of matches
    if summary of targetEvent is not "初赛验收 - MUSE-R2-REMAINING-20261005-2008" then error "Title mismatch; no deletion"
    set s to start date of targetEvent
    set e to end date of targetEvent
    if (year of s) is not 2026 or (month of s as integer) is not 10 or (day of s) is not 6 or (hours of s) is not 16 or (minutes of s) is not 0 or (hours of e) is not 16 or (minutes of e) is not 30 then error "Time mismatch; no deletion"
    tell targetCalendar to delete (every event whose uid is "CDBB19C1-1806-4F53-94E9-6FC1ED7D659C")
    return "EXACT_UID_DELETE_REQUESTED"
end tell
