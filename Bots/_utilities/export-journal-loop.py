# export-journal-loop.py
# Continuously exports the in-memory journal to C:\Temp\re_journal_export.txt every 30s.
# Set to Auto Start in RazorEnhanced Scripts panel — runs in background alongside the bot.
# No overhead spam. File is always fresh when Claude asks to read it.

from System.IO import File, Directory

OUTPUT_PATH = r"C:\Temp\re_journal_export.txt"
INTERVAL_MS = 30000

Directory.CreateDirectory(r"C:\Temp")

while True:
    lines = []
    try:
        for entry in Journal.JournalEntries:
            try:
                ts = entry.Timestamp.ToString("[MM/dd/yyyy HH:mm:ss]")
                name = entry.Name if entry.Name else "System"
                text = entry.Text if entry.Text else ""
                lines.append("{} {}: {}".format(ts, name, text))
            except:
                pass
    except Exception as e:
        lines.append("# Error: {}".format(str(e)))

    File.WriteAllLines(OUTPUT_PATH, lines)
    Misc.Pause(INTERVAL_MS)
