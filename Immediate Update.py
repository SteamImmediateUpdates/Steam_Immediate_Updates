"""
===========================================================
    Steam .acf AutoUpdateBehavior Modifier Script
===========================================================

Version: 1.0.0
Date: 2025-11-02
Author: Some anonymous wannabe coder who leaned on ChatGPT to do most of the coding for this. But it works.
Permissions: I can hardly take credit for this. I suck at coding. Do whatever you like with it. Pretend that you coded it for all I care. Go nuts.

Description:

    Short version: 
    Makes all of your Steam games update as soon as 
    there is an update available, rather than updated being scheduled
    hours or even days into the future.


    Long versiob:
    This script scans specified directories for Steam's .acf 
    (App Configuration) files and modifies the "AutoUpdateBehavior" 
    setting from 0 (Let Steam decide) to 2 (Immediately Download 
    Updates). Optionally (Default on), it can back up all the .acf files to a 
    specified backup directory before modifying them. The script 
    also automatically detects all of Steam's installation 
    directories on the system.

Features:
    - Search and replace specific values in Steam .acf files. (configurable)
    - Option to back up the .acf files before modification. (togglable)
    - Automatic detection of Steam installation directories.
    - Log file creation for tracking script execution. (togglable)
    - Keeps only a specified number of most recent log files. (configurable)

Requirements:
    - Python 3.x
    - Python modules: os, sys, shutil, re, subprocess
    - Dependency check at runtime with routine to acquire uninstalled modules

Usage:
    1. Place the script in a directory.
    2. Run the script. It will either find or create a configuration file 
       (config.txt) and automatically scan for Steam's installation directories.
    3. It will modify the "AutoUpdateBehavior" setting in the relevant .acf files.
    4. Optionally, you can enable backups for all the .acf files.

Notes:
    - The script will automatically back up the files if the 'backup_enabled'
      option is set to true in config.txt. (default true)
    - Logs are stored in a 'logs' directory and older logs are cleaned up
      based on the 'max_log_files' configuration. (dafault on, max. 3 logs)

===========================================================
"""

import os
import sys
import shutil
import re
from datetime import datetime
import subprocess

# --- Dependency check ---
required_modules = ["re"]
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        print(f"[INFO] Module '{module}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

# --- Configuration ---
CONFIG_FILE = "config.txt"
directories_to_scan = []
modified_files = []

# Default values
SEARCH_STR = '"AutoUpdateBehavior"\t\t"0"'
REPLACE_STR = '"AutoUpdateBehavior"\t\t"2"'
backup_enabled = False
backup_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
max_log_files = 3  # default number of logs to keep

print("=== Steam .acf AutoUpdateBehavior Modifier ===")

# --- Check config file ---
config_was_created = False
if not os.path.exists(CONFIG_FILE):
    print('Config file doesn\'t exist! Creating default config file "config.txt"...')
    config_was_created = True

    default_config_template = """# Directories to scan (one per line)
{steamapps_dirs}

# Backup settings
backup_enabled = true
backup_directory = backups

# Number of log files to keep
max_log_files = 3

# Strings to search and replace ("AutoupdateBehavior" and "x" strings are separated by two tabs, which are represented by "\\t\\t". Keep this in mind if you need to make modifications.
# AutoUpdateBehavior flags are: 0 - "Let Steam decide when to update" 2 - "Immediately Download Updates"
# You should not need to modify these unless Valve changes the way flags are handled in .acf files.
search_string = "AutoUpdateBehavior"\\t\\t"0"
replace_string = "AutoUpdateBehavior"\\t\\t"2"
"""

    # Create the config immediately with empty directories
    steamapps_dirs = ""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(default_config_template.format(steamapps_dirs=steamapps_dirs))

    print("[INFO] Default config created. The script will now automatically search for steamapps directories.")

    # --- Auto-detect directories ---
    found_dirs = []

    def find_steamapps_on_drive(drive_letter):
        found = [None]

        def scan_directory_tree(current_dir):
            if found[0]:
                return
            try:
                for entry in os.scandir(current_dir):
                    if entry.is_dir():
                        name_lower = entry.name.lower()
                        if entry.name.lower() in ("program files (x86)",) or "steam" in name_lower or "games" in name_lower:
                            scan_directory_tree(entry.path)
                        if entry.name.lower() == "steamapps":
                            found[0] = entry.path
                            print(f"[FOUND] Steamapps folder: {found[0]}")
                            return
            except PermissionError:
                return

        root = f"{drive_letter}:\\"  # Start from the root of the drive
        scan_directory_tree(root)
        return found[0]

    # Scan each drive for steamapps folder
    for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = f"{drive}:\\"  # Check if the drive exists
        if os.path.exists(drive_path):
            result = find_steamapps_on_drive(drive)
            if result:
                found_dirs.append(result)

    steamapps_dirs = "\n".join(found_dirs)

    # Check if directories were found, if none were found, add error message
    if not found_dirs:
        print("\nNo steamapps directories found! You will need to add the directory paths manually to config.txt.")

    # Update config file with discovered directories
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(default_config_template.format(steamapps_dirs=steamapps_dirs))

    if found_dirs:
        print("Quick Scan finished! Directories added to config.txt.")

# --- Read config file and collect directories ---
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("backup_enabled"):
            value = line.split("=", 1)[1].strip().lower()
            backup_enabled = value in ("true", "yes", "1")
        elif line.lower().startswith("backup_directory"):
            backup_directory = line.split("=", 1)[1].strip()
        elif line.lower().startswith("max_log_files"):
            try:
                max_log_files = int(line.split("=", 1)[1].strip())
            except ValueError:
                pass
        elif line.lower().startswith("search_string"):
            SEARCH_STR = line.split("=", 1)[1].strip().encode('utf-8').decode('unicode_escape')
        elif line.lower().startswith("replace_string"):
            REPLACE_STR = line.split("=", 1)[1].strip().encode('utf-8').decode('unicode_escape')
        else:
            directories_to_scan.append(line)

print(f"\nBackup Enabled: {backup_enabled}")
print(f"Backup Directory: {backup_directory}")
print(f"Directories to Scan: {directories_to_scan}")
print(f"Search String: {SEARCH_STR}")
print(f"Replace String: {REPLACE_STR}")
print(f"Max Log Files: {max_log_files}\n")

# --- Logging setup ---
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file_path = os.path.join(LOG_DIR, f"{timestamp}.log")

class Logger:
    def __init__(self, logfile):
        self.terminal = sys.stdout
        self.log = open(logfile, "w", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger(log_file_path)

# --- Keep only most recent log files ---
all_logs = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".log")])
while len(all_logs) > max_log_files:
    old_log = all_logs.pop(0)
    try:
        os.remove(os.path.join(LOG_DIR, old_log))
    except Exception:
        pass

# --- Ensure backup directory exists ---
if backup_enabled:
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory, exist_ok=True)
        print(f"[INFO] Backup root directory ready: {backup_directory}")

# --- Helper: extract game name from .acf file ---
def get_game_name_from_acf(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) >= 6:
                match = re.match(r'\s*"name"\s*"\s*(.+?)\s*"', lines[5])
                if match:
                    return match.group(1)
    except Exception:
        pass
    return "Unknown Game"

# --- Backup all .acf files first ---
if backup_enabled:
    for root_dir in directories_to_scan:
        if not os.path.exists(root_dir):
            print(f"[WARN] Directory not found: {root_dir}")
            continue

        print(f"[INFO] Backing up .acf files from: {root_dir}")

        drive_letter = os.path.splitdrive(os.path.abspath(root_dir))[0].replace(":", "")
        if not drive_letter:
            drive_letter = "unknown_drive"

        for file in os.listdir(root_dir):
            if not file.lower().endswith(".acf"):
                continue

            file_path = os.path.join(root_dir, file)
            if not os.path.isfile(file_path):
                continue

            backup_folder = os.path.join(backup_directory, drive_letter)
            os.makedirs(backup_folder, exist_ok=True)

            backup_path = os.path.join(backup_folder, file)
            try:
                shutil.copy2(file_path, backup_path)
                game_name = get_game_name_from_acf(file_path)
                print(f"[BACKUP] {file} → {backup_path} → {game_name}")
            except Exception as e:
                print(f"[WARN] Could not backup {file_path}: {e}")

# --- Modify files ---
for root_dir in directories_to_scan:
    if not os.path.exists(root_dir):
        continue

    print(f"[INFO] Scanning for modifications in: {root_dir}")

    for file in os.listdir(root_dir):
        if not file.lower().endswith(".acf"):
            continue

        file_path = os.path.join(root_dir, file)
        if not os.path.isfile(file_path):
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"[WARN] Could not read {file_path}: {e}")
            continue

        if SEARCH_STR in content:
            new_content = content.replace(SEARCH_STR, REPLACE_STR)
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                modified_files.append(file_path)
                print(f"[OK] Modified: {file_path}")
            except Exception as e:
                print(f"[WARN] Could not modify {file_path}: {e}")

# --- Output list of modified files ---
if modified_files:
    print("\n=== List of modified files ===")
    for file in modified_files:
        # Get the game name for each modified file
        game_name = get_game_name_from_acf(file)
        print(f"{file} → {game_name}")
else:
    print("\nNo files were modified.")
