-- Independent system Calendar path. Only exact authorized synthetic IDs are touched.
on run argv
    set mode to item 1 of argv
    set testID to item 2 of argv
    if testID does not start with "MUSE-R2-" then error "Synthetic ID required"
    set s to current date
    set year of s to 2026
    set month of s to October
    set day of s to 4
    set time of s to (15 * hours + 30 * minutes)
    set e to s + hours
    tell application "Calendar"
        set targetCalendar to first calendar whose name is "工作"
        set matching to every event of targetCalendar whose summary is testID
        if mode is "create" then
            if (count matching) is not 0 then error "Duplicate synthetic event refused"
            set created to make new event at end of events of targetCalendar with properties {summary:testID, start date:s, end date:e, location:"Muse synthetic acceptance"}
            return uid of created
        else if mode is "get" then
            if (count matching) is not 1 then return "NOT_FOUND"
            return uid of item 1 of matching
        else if mode is "delete" then
            if (count matching) is not 1 then error "Exact synthetic event missing or ambiguous"
            delete item 1 of matching
            return "DELETED"
        else
            error "Unsupported operation"
        end if
    end tell
end run
