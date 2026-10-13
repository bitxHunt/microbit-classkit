#!/usr/bin/env python3
"""micro:bit reset station.

Plug micro:bits into this laptop (directly or through a powered USB hub).
Each one gets the standard "class-ready" program, and one line is printed
and logged per board:

    Kit zavet   V2.00  firmware 0255  reset OK

    ./station.py                 keep running, reset every board that is plugged in
    ./station.py --once          reset the boards plugged in right now, then stop
    ./station.py --check         only read each board's details, change nothing
    ./station.py --drive DIR     treat a folder as a micro:bit drive (for testing without a board)

Linux only for now (uses lsblk and udisksctl). Nothing here needs root.
"""
import argparse
import csv
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import termios
import time
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEX = HERE / "class-ready.hex"
LOG = HERE / "log" / "resets.csv"

# The first four digits of a board's Unique ID say which model it is.
BOARDS = {"9900": "V1.3", "9901": "V1.5", "9903": "V2.00", "9904": "V2.00", "9905": "V2.20", "9906": "V2.21"}


@dataclass
class Board:
    device: str          # /dev/sdb, or the folder given with --drive
    mount: Path | None   # where its MICROBIT drive is mounted
    usb_serial: str      # the Unique ID, also in the USB serial port's name

    @property
    def version(self) -> str:
        return BOARDS.get(self.usb_serial[:4], "unknown")


def plugged_in() -> list[Board]:
    """Every drive labelled MICROBIT that the laptop can see right now."""
    out = subprocess.run(["lsblk", "-J", "-o", "PATH,LABEL,MOUNTPOINT,SERIAL"],
                         capture_output=True, text=True, check=True).stdout
    boards = []
    for dev in json.loads(out)["blockdevices"]:
        if dev.get("label") == "MICROBIT":
            mount = Path(dev["mountpoint"]) if dev.get("mountpoint") else None
            boards.append(Board(dev["path"], mount, dev.get("serial") or ""))
    return boards


def mount(board: Board) -> Path | None:
    if board.mount:
        return board.mount
    done = subprocess.run(["udisksctl", "mount", "-b", board.device], capture_output=True, text=True)
    # udisksctl prints: Mounted /dev/sdb at /run/media/harry/MICROBIT
    if done.returncode == 0 and " at " in done.stdout:
        board.mount = Path(done.stdout.strip().rstrip(".").split(" at ", 1)[1])
    return board.mount


def details(drive: Path) -> dict:
    """DETAILS.TXT is a small file every micro:bit drive has: 'Key: value' lines."""
    info = {}
    path = drive / "DETAILS.TXT"
    if path.exists():
        for line in path.read_text(errors="replace").splitlines():
            key, sep, value = line.partition(":")
            if sep and not line.startswith("#"):
                info[key.strip()] = value.strip()
    return info


def failure(drive: Path) -> str:
    """FAIL.TXT only exists when the last flash went wrong. It says why."""
    path = drive / "FAIL.TXT"
    if not path.exists():
        return ""
    lines = [l.strip() for l in path.read_text(errors="replace").splitlines() if l.strip()]
    return next((l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("error:")), lines[0] if lines else "failed")


def flash(drive: Path) -> None:
    """Copying a .hex file onto the drive is how a micro:bit is programmed."""
    target = drive / HEX.name
    with HEX.open("rb") as src, target.open("wb") as dst:
        shutil.copyfileobj(src, dst)
        dst.flush()
        os.fsync(dst.fileno())


def kit_name(usb_serial: str, wait: float = 20) -> tuple[str, str]:
    """The class-ready program sends 'KIT <name> <serial number>' down the cable. Read one line of it."""
    deadline = time.time() + wait
    while time.time() < deadline:
        ports = [p for p in Path("/dev/serial/by-id").glob("*") if usb_serial and usb_serial in p.name]
        for port in ports:
            try:
                fd = os.open(port, os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK)
            except OSError:
                continue
            try:
                attrs = termios.tcgetattr(fd)
                attrs[4] = attrs[5] = termios.B115200
                termios.tcsetattr(fd, termios.TCSANOW, attrs)
                text, stop = "", time.time() + 4
                while time.time() < stop:
                    try:
                        text += os.read(fd, 256).decode(errors="replace")
                    except BlockingIOError:
                        time.sleep(0.1)
                    for line in text.splitlines():
                        parts = line.split()
                        if len(parts) == 3 and parts[0] == "KIT":
                            return parts[1], parts[2]
            finally:
                os.close(fd)
        time.sleep(1)
    return "", ""


def wait_for_return(usb_serial: str, wait: float = 30) -> Board | None:
    """After a flash the drive disappears and comes back. Wait for it."""
    deadline = time.time() + wait
    time.sleep(3)
    while time.time() < deadline:
        for board in plugged_in():
            if board.usb_serial == usb_serial:
                return board
        time.sleep(1)
    return None


def record(row: dict) -> None:
    LOG.parent.mkdir(exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row))
        if new:
            writer.writeheader()
        writer.writerow(row)


def handle(board: Board, check_only: bool, fake: bool = False) -> None:
    drive = board.mount if fake else mount(board)
    if not drive:
        print(f"{board.device}: could not open the MICROBIT drive")
        return
    info = details(drive)
    board.usb_serial = board.usb_serial or info.get("Unique ID", "")
    firmware = info.get("Interface Version", "?")
    before = failure(drive)
    name, serial_number, result = "", "", "checked"

    if not check_only:
        flash(drive)
        if fake:
            result = "reset OK (test folder, nothing was really flashed)"
        else:
            back = wait_for_return(board.usb_serial)
            problem = failure(mount(back)) if back and mount(back) else "board did not come back after the flash"
            result = f"FAILED: {problem}" if problem else "reset OK"
            if not problem:
                name, serial_number = kit_name(board.usb_serial)
    elif before:
        result = f"last flash failed: {before}"

    label = f"Kit {name}" if name else f"Board {board.usb_serial[-6:] or '?'}"
    print(f"{label:<14} {board.version:<6} firmware {firmware:<5} {result}", flush=True)
    record({"time": f"{dt.datetime.now():%Y-%m-%d %H:%M:%S}", "kit_name": name, "serial_number": serial_number,
            "usb_id": board.usb_serial, "board": board.version, "firmware": firmware, "result": result})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--drive", type=Path)
    args = ap.parse_args()

    if args.drive:
        handle(Board(str(args.drive), args.drive, ""), args.check, fake=True)
        return 0
    if not HEX.exists():
        sys.exit(f"Missing {HEX}. Build it first, see README.md.")

    print("Reset station ready. Plug in micro:bits. Ctrl+C to stop.\n", flush=True)
    done: set[str] = set()
    try:
        while True:
            present = plugged_in()
            for board in present:
                key = board.usb_serial or board.device
                if key not in done:
                    done.add(key)
                    handle(board, args.check)
            # A board that was unplugged can be reset again next time it is plugged in.
            done &= {b.usb_serial or b.device for b in plugged_in()}
            if args.once:
                return 0
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped. Log: " + str(LOG))
        return 0


if __name__ == "__main__":
    sys.exit(main())
