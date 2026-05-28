#!/usr/bin/env python3
"""
backup_onedrive.py — Copy quotation.db to OneDrive via rclone. Keeps last 5 backups.

Requirements: rclone configured with a remote named 'onedrive'
Usage: python backup_onedrive.py [--db quotation.db] [--remote onedrive] [--folder SandG-Backups]
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def backup(db_path: Path, remote: str, folder: str, keep: int = 5) -> None:
    if not db_path.exists():
        print(f"ERROR: {db_path} not found")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_name = f"quotation_{timestamp}.db"
    dest = f"{remote}:{folder}/{dest_name}"

    print(f"Copying {db_path} → {dest}")
    rc, out = run(["rclone", "copyto", str(db_path), dest])
    if rc != 0:
        print(f"ERROR: rclone copy failed:\n{out}")
        sys.exit(1)
    print(f"Backup complete: {dest_name}")

    rc, out = run(["rclone", "lsf", f"{remote}:{folder}/", "--files-only"])
    if rc != 0:
        print(f"WARNING: could not list remote files:\n{out}")
        return

    files = sorted(line.strip() for line in out.splitlines() if line.strip().startswith("quotation_"))
    if len(files) > keep:
        to_delete = files[: len(files) - keep]
        for f in to_delete:
            path = f"{remote}:{folder}/{f}"
            print(f"Deleting old backup: {f}")
            rc, out = run(["rclone", "deletefile", path])
            if rc != 0:
                print(f"WARNING: could not delete {f}:\n{out}")
    print(f"Kept {min(len(files), keep)} backup(s)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="quotation.db")
    parser.add_argument("--remote", default="onedrive")
    parser.add_argument("--folder", default="SandG-Backups")
    parser.add_argument("--keep", type=int, default=5)
    args = parser.parse_args()
    backup(Path(args.db), args.remote, args.folder, args.keep)
