# Journal Logs

When reading journal files from `C:\Outlands\ClassicUO\Data\Client\JournalLogs\`:
- **Only read the most recent file** (sorted by filename timestamp)
- Never read older files unless the user explicitly asks
- If the most recent file is locked, prompt the user to exit the game, then read it once they confirm

# uoo-scripts Repository

All scripts are under `uoo-scripts\` (was `tallisado-boats`). This is the single source of truth.

## Folder Layout

```
uoo-scripts\
├── Boating\          Button scripts: boarding, disembark, cannons, repair, stances, crew heal
│   └── cannon\       Individual cannon slot scripts
├── Bots\
│   ├── PoonerBot\    Main bot loop (base.razor, init.razor)
│   └── _utilities\   Python helpers, cannon-fire-target
├── Boat-PvM\         Older boat PvM bot (Master Background, room-crate, dump-hull)
│   └── heal-crew\    Old crew heal button scripts
├── Chiv\             Chivalry ability scripts
├── Combat\           Standalone combat scripts: auto-heal-loop, ebolt-combo, button-last-target
├── Dex bot\          Dex bot: init, hally
├── Fishing\          Fishing scripts + dump-loot-hold + crew-all-nearest
├── Harvesting\       Harvesting + scavenging: scavenge-loop, scavenge-loop-button, scavenger-summons, auto-harvester, etc.
│   └── scav-recall\  Individual recall-spot scripts for Scavenging.xml (ctrl+1-0 = Regs/Witcher, shift+ctrl+1-5 = Shipwrights)
├── Navigation\       Recall/travel: gate, room, rope-tele, rope-wall
├── Organizers\       Bag management: inn-dropper, move-label-to-bag, scrap-unid-chest
├── Skills\           (future use)
├── Thief\            Thief skills: steal-last
├── Train\            Skill training scripts — run manually, no XML hotkey bindings expected
└── Profiles\         Copies of all RazorEnhanced profile XMLs (reference only — live files in Profiles\)
```

## Profile XML Location

Live profiles: `C:\Outlands\ClassicUO\Data\Plugins\Assistant\Profiles\`
Reference copies: `uoo-scripts\Profiles\`

All hotkeys in all profiles point to `uoo-scripts\*` paths.

## Key Hotkey Profiles

| Profile | Purpose | Bot entry point |
|---------|---------|----------------|
| Pooner.xml | Boating PvM (active) | `uoo-scripts\Bots\PoonerBot\init` |
| BoatPvM.xml | Old boating bot | `uoo-scripts\Boat-PvM\Master Background` |
| Fishing.xml | Fishing bot (Tallis) | `uoo-scripts\Fishing\init` |
| Fishing2.xml | Fishing bot (Tallis Sado) | `uoo-scripts\Fishing\init` |
| Tallis.xml | General PvM/explore | `uoo-scripts\Dex bot\init` |
| MagePVM.xml | Mage PvM | `uoo-scripts\Automation\Mage Bot\init` |
| Lumbering.xml | Lumbering | `uoo-scripts\Gathering\auto-lumbering-jase` |
| Scavenging.xml | Scavenging | `uoo-scripts\Scavenging\scavenge-loop` |
| ScavaGina.xml | Alt scavenger | `uoo-scripts\Scavenging\scavenge-loop` |
| Thief.xml | Thief | `uoo-scripts\Thief\steal-last` |
| PVP.xml | PvP | `uoo-scripts\Dex bot\hally` |

## Characters

| Character | Account | Role | Profile |
|-----------|---------|------|---------|
| Tallis | kane2 | General PvM / explorer | Tallis.xml |
| Tallis Sado | kane2 | Harvester and fisher | Fishing2.xml — F12 runs `Fishing\init` |

## Backup

Old loose scripts and folders archived at:
`C:\Outlands\ClassicUO\Data\Plugins\Assistant\_backup_2026_05_07\`

# RazorEnhanced Scripting Rules

Critical parser/runtime behaviours that cause silent bugs or errors:

## No short-circuit evaluation — ever

RazorEnhanced evaluates **all parts** of `if`, `elseif`, and `or` expressions regardless of earlier results. This applies to both `or` conditions and `elseif` chains.

**Never do this:**
```razor
if not timerexists X or timer X >= CD      # timer X throws if X doesn't exist
if A or not timerexists X or timer X >= CD  # same problem
if not timerexists X
    ...
elseif timer X >= CD                        # still evaluated even if if-branch ran
```

**Always use nested if/else:**
```razor
@setvar! myFlag 0
if timerexists X
    if timer X >= CD
        @setvar! myFlag 1
    endif
else
    @setvar! myFlag 1
endif
if myFlag = 1
    [do the thing]
endif
```

## `{{}}` string interpolation only works for script variables

`overhead "val={{expr}}"` — `{{}}` only interpolates variables set with `@setvar!`. Built-in expressions always return `<not found>`:
- `{{diffhits}}` → `<not found>`
- `{{warmode}}` → `<not found>`
- `{{findbuff 'x'}}` → `<not found>`
- `{{skill 'x'}}` → `<not found>`
- `{{timer X}}` → `<not found>`

`@setvar! myvar diffhits` also does NOT capture the real value — stores `4294967295` (the not-found sentinel). Built-in expressions can only be used directly in `if` conditions.

To display approximate diffhits, use bucket checks:
```razor
@setvar! myvar 0
if diffhits >= 80
    @setvar! myvar 80
elseif diffhits >= 60
    @setvar! myvar 60
elseif diffhits >= 40
    @setvar! myvar 40
elseif diffhits >= 20
    @setvar! myvar 20
elseif diffhits >= 1
    @setvar! myvar 1
endif
```

## `insysmsg` accumulates until `clearsysmsg`

`insysmsg "X"` checks all messages since the last `clearsysmsg`. If `clearsysmsg` is called mid-loop, messages checked later in the same loop pass will be missing. Capture important flags at the **top** of the loop before any `clearsysmsg` calls.

## `settimer X Y` with Y > 0 starts already-elapsed

`settimer X 30000` starts the timer with 30000ms already elapsed — so `timer X >= 30000` passes immediately. Use this to pre-expire timers during init so abilities are ready on first loop pass.

## `hotkey "Play Script: X"` stops the current script immediately

The line after a `hotkey "Play Script: ..."` call never runs. The script halts and X starts fresh.

## Warmode

`attack X` alone does not reliably set warmode. Use explicit `warmode on` before `attack`. `warmode` is a built-in that cannot be string-interpolated.

## `getlabel` as a server round-trip ping

After sending an action to the server (e.g. `target X`) and calling `clearsysmsg`, the server's response message may not have arrived yet when `insysmsg` is checked. Use `getlabel` on any nearby object as a cheap blocking round-trip to ensure the server has had time to respond:

```razor
target self
clearsysmsg
getlabel backpack pingCheck   # waits one server round-trip; pingCheck is intentionally unused
if insysmsg "you don't see"
    ...
endif
```

Do not remove these `getlabel` ping lines — they are load-bearing synchronisation, not dead code.

## Comment rules

**No inline comments** — `//` after code on the same line breaks the parser. Comments must be on their own line.

**No leading comment block** — do not open a script with a block of `//` comment lines before the first executable statement. The parser chokes on this. Start scripts directly with code (`@setvar!`, `overhead`, etc.).

**Never do this:**
```razor
// Fishing base loop
// Started by boat-startup
// ...
@setvar! MaxSelfHeal 0    // also broken inline
```

**Always do this:**
```razor
@setvar! MaxSelfHeal 0
overhead 'script starting' 88
```

If you need a file description, put it at the bottom or after the first executable line.

## Outlands SmartHarvest — `target self` carves nearest corpse

On UO:Outlands, tools with SmartHarvest (e.g. Elven SpellBlade) use `target self` to auto-carve the nearest corpse in range — you do **not** target the corpse directly. This is intentional Outlands custom behaviour, not a bug:

```razor
dclicktype "Elven Spellblade"
wft 500
target self    # SmartHarvest: server picks nearest corpse automatically
```

Interaction range for skinning is **2 tiles** — use `findtype "corpse" ground -1 -1 2` to match.

## Profile XML Hotkey Management

When adding hotkeys to a profile XML:

1. **Always read the existing `<hotkeys>` block first** to check for conflicts before inserting.
2. **Update both files**: repo copy at `uoo-scripts\Profiles\<Name>.xml` AND live copy at `C:\Outlands\ClassicUO\Data\Plugins\Assistant\Profiles\<Name>.xml`.
3. **Profile updates only take effect after reloading the profile in RazorEnhanced** (or restarting the client). If a change doesn't appear, the game likely overwrote the file on close — edit the live file while the game is not running or immediately after loading.

### Key code reference

| Key | `key=` value |
|-----|-------------|
| 0   | 48          |
| 1–9 | 49–57       |
| A–Z | 65–90 (ASCII uppercase) |

### Modifier (`mod=`) values

| Modifier   | Value |
|------------|-------|
| None       | 0     |
| Alt        | 1     |
| Ctrl       | 2     |
| Shift      | 4     |
| Ctrl+Shift | 6     |
| Alt+Shift  | 5     |

### Scavenging.xml recall spot bindings

`Ctrl+1–9`, `Ctrl+0` → `Harvesting\scav-recall\recall-1` … `recall-9`, `recall-0`
`Shift+Ctrl+1–5` → `Harvesting\scav-recall\recall-s1` … `recall-s5`

| Key        | Script       | Location           |
|------------|--------------|--------------------|
| Ctrl+1     | recall-1     | Anchor Regs        |
| Ctrl+2     | recall-2     | Andaria Regs       |
| Ctrl+3     | recall-3     | Cambria Regs       |
| Ctrl+4     | recall-4     | Horseshoe Regs     |
| Ctrl+5     | recall-5     | Outpost Regs       |
| Ctrl+6     | recall-6     | PrevNorth Regs     |
| Ctrl+7     | recall-7     | PrevSouth Regs     |
| Ctrl+8     | recall-8     | Totem Regs         |
| Ctrl+9     | recall-9     | Terran Regs        |
| Ctrl+0     | recall-0     | Witcher            |
| S+Ctrl+1   | recall-s1    | Anchor Shipwright  |
| S+Ctrl+2   | recall-s2    | Cambria Shipwright |
| S+Ctrl+3   | recall-s3    | Andaria Shipwright |
| S+Ctrl+4   | recall-s4    | Corpse Shipwright  |
| S+Ctrl+5   | recall-s5    | Prev Shipwright    |
