# micro:bit Class Kit

Two small prototypes for running micro:bit classes with less lost time.

| Folder | What it is | Status |
|---|---|---|
| `reset-station/` | Plug micro:bits into a laptop and each one is reset to a standard program, checked and logged | Works on a test folder. Not yet tried on a real board |
| `tutorials/night-light/` | One lesson rewritten as a self-paced MakeCode tutorial, with a wiring picture | Written. Not yet opened in MakeCode |

## Reset station

Before class, instructors reset boards one at a time. This does it for every board that is plugged in.

```bash
cd reset-station
./station.py            # keep running: reset each board as it is plugged in
./station.py --once     # reset the boards plugged in now, then stop
./station.py --check    # only read each board's details, change nothing
```

One line per board, also saved to `log/resets.csv`:

```
Kit zavet      V2.00  firmware 0255  reset OK
Board 96990b   V2.00  firmware 0255  FAILED: The transfer timed out.
```

How it works:

1. A micro:bit shows up as a USB drive called `MICROBIT`. The script finds every one (`lsblk`) and mounts it (`udisksctl`).
2. It reads `DETAILS.TXT` on the drive: the board's unique ID, model (V1 or V2) and firmware version.
3. It copies `class-ready.hex` onto the drive. That is how a micro:bit is programmed.
4. The board restarts. If `FAIL.TXT` appears on the drive, the flash failed and the reason is in that file.
5. The class-ready program scrolls the board's own 5-letter name and sends it down the cable, so the log links each board to its name with no typing.

With a powered USB hub, several boards can be done at once. Linux only for now.

The source of the standard program is `class-ready/main.ts`. To rebuild the hex after a change:

```bash
cd reset-station/class-ready
npx makecode build && cp built/binary.hex ../class-ready.hex
```

### Still to test on a real board

- [ ] Does the drive mount and the flash finish?
- [ ] Does the kit name arrive over the cable?
- [ ] Does resetting a board this way remove its Bluetooth pairing with a tablet?
- [ ] How many boards can one hub do at once?

## Self-paced tutorial

`tutorials/night-light/README.md` is a full lesson in MakeCode's tutorial format. Each student sees one step at a time, with only the blocks that step needs and a hint if they are stuck. It has a "predict first" step, a "change it" step and an open challenge, so students do more than copy.

To open it, once this repo is on GitHub:

```
https://makecode.microbit.org/#tutorial:https://github.com/bitxHunt/microbit-classkit/tutorials/night-light
```

Without GitHub: make a new project at makecode.microbit.org, switch to JavaScript, open Explorer, paste the tutorial text into `README.md`, share the project, then open `https://makecode.microbit.org/#tutorial:<the share link>`. The wiring picture only shows once the repo is public, because the tutorial loads it from GitHub.

### Still to test

- [ ] Does the tutorial open and do all steps show correctly?
- [ ] Does it work in Chrome on a phone or tablet?
- [ ] On an iPad: does Download in Chrome hand the code to the micro:bit app?

## Note

The lesson text here is my own. It does not copy any course provider's slides.
