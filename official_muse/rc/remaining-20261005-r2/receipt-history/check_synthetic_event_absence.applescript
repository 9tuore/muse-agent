tell application "Calendar"
    set targets to calendars whose name is "工作"
    set titleCount to 0
    set uidCount to 0
    repeat with cal in targets
        set titleCount to titleCount + (count of (every event of cal whose summary is "初赛验收 - MUSE-R2-REMAINING-20261005-2008"))
        set uidCount to uidCount + (count of (every event of cal whose uid is "CDBB19C1-1806-4F53-94E9-6FC1ED7D659C"))
    end repeat
    return {titleCount, uidCount}
end tell
