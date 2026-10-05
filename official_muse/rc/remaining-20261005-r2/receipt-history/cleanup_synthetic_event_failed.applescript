tell application "Calendar"
    set targets to calendars whose name is "工作"
    set hits to {}
    repeat with cal in targets
        repeat with ev in (every event of cal whose summary is "初赛验收 - MUSE-R2-REMAINING-20261005-2008")
            set end of hits to ev
        end repeat
    end repeat
    if (count of hits) is not 1 then error "Synthetic event count is not exactly one; no deletion"
    set ev to item 1 of hits
    if uid of ev is not "CDBB19C1-1806-4F53-94E9-6FC1ED7D659C" then error "Synthetic UID mismatch; no deletion"
    set s to start date of ev
    set e to end date of ev
    if (year of s) is not 2026 or (month of s as integer) is not 10 or (day of s) is not 6 or (hours of s) is not 16 or (minutes of s) is not 0 then error "Unexpected synthetic start; no deletion"
    if (year of e) is not 2026 or (month of e as integer) is not 10 or (day of e) is not 6 or (hours of e) is not 16 or (minutes of e) is not 30 then error "Unexpected synthetic end; no deletion"
    delete ev
    set remaining to 0
    repeat with cal in targets
        set remaining to remaining + (count of (every event of cal whose summary is "初赛验收 - MUSE-R2-REMAINING-20261005-2008"))
    end repeat
    if remaining is not 0 then error "Cleanup not independently confirmed"
    return "SYNTHETIC_EVENT_DELETED_AND_ABSENT"
end tell
