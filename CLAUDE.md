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
├── Boat-PvM\         Older boat PvM bot (Master Background, cannon, disembark scripts)
│   └── heal-crew\    Old crew heal button scripts
├── Chiv\             Chivalry ability scripts
├── Combat\           Standalone combat scripts: auto-heal-loop, ebolt-combo, button-last-target
├── Dex bot\          Dex bot: init, hally
├── Fishing\          Fishing scripts + dump-loot-hold + crew-all-nearest
├── Gathering\        Harvesting: all-harvester, auto-lumbering-jase, button-skinning, scav-harvester-summon, auto-harvester
├── Navigation\       Recall/travel: gate, room, rope-tele, rope-wall
├── Organizers\       Bag management: inn-dropper, move-label-to-bag, scrap-unid-chest
├── Scavenging\       Scav scripts: scav-buffs, scavenge-loop, society-time
├── Skills\           (future use)
├── Thief\            Thief skills: steal-last
├── Train\            Skill training: train-steal, train-detect
├── Automation\
│   └── Mage Bot\     Mage bot: init
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
| Fishing.xml | Fishing bot | `uoo-scripts\Fishing\boat-startup` |
| Tallis.xml | General PvM/explore | `uoo-scripts\Dex bot\init` |
| MagePVM.xml | Mage PvM | `uoo-scripts\Automation\Mage Bot\init` |
| Lumbering.xml | Lumbering | `uoo-scripts\Gathering\auto-lumbering-jase` |
| Scavenging.xml | Scavenging | `uoo-scripts\Scavenging\scavenge-loop` |
| ScavaGina.xml | Alt scavenger | `uoo-scripts\Scavenging\scavenge-loop` |
| Thief.xml | Thief | `uoo-scripts\Thief\steal-last` |
| PVP.xml | PvP | `uoo-scripts\Dex bot\hally` |

## Backup

Old loose scripts and folders archived at:
`C:\Outlands\ClassicUO\Data\Plugins\Assistant\Scripts\_backup_2026_05_07\`

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
