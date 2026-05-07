# export-journal.py
# Reads RazorEnhanced's in-memory journal buffer and writes to C:\Temp\re_journal_export.txt
# Run this from hotkey or script list — bypasses the Win32 exclusive lock on the active journal file.
# Output file is always overwritten with the current session's full journal.

from System.IO import File, Directory
from System import DateTime

OUTPUT_PATH = r"C:\Temp\re_journal_export.txt"

Directory.CreateDirectory(r"C:\Temp")

lines = []
try:
    entries = Journal.JournalEntries
    for entry in entries:
        try:
            ts = entry.Timestamp.ToString("[MM/dd/yyyy HH:mm]")
            name = entry.Name if entry.Name else "System"
            text = entry.Text if entry.Text else ""
            lines.append("{} {}: {}".format(ts, name, text))
        except:
            pass
except Exception as e:
    lines.append("# JournalEntries error: {}".format(str(e)))
    # Fallback: try index-based access
    try:
        i = 0
        while True:
            line = Journal.GetLineFromIndex(i)
            if line is None:
                break
            lines.append(line)
            i += 1
    except Exception as e2:
        lines.append("# Fallback also failed: {}".format(str(e2)))

File.WriteAllLines(OUTPUT_PATH, lines)
Misc.SendMessage("Journal: {} lines -> {}".format(len(lines), OUTPUT_PATH), 88)
