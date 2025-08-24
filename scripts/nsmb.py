"""
This script:
    - Runs convert_sdk.py (if needed)
    - Copies the SDK & a clean ROM to a persistant volume for multi-project use
    - Extracts the contents of your ROM via NDSpy
    - Applies code patches via NCPatcher
    - Bundles back up the contents of your ROM + custom files via NDSpy

Created by: Ndymario
"""
from pathlib import Path
import hashlib
import sys
import subprocess
import shutil
import os

include_folder = Path("/data/include")
scripts_folder = Path("/app/scripts/")
clean_rom = Path("/data/nsmb.nds")
arm9_json = Path("/app/arm9.json")
ncpatcher_json = Path("/app/ncpatcher.json")
sha256_hashes = {"nsmb": "9f67fef1b4c73e966767f6153431ada3751dc1b0da2c70f386c14a5e3017f354",
                "arm9": "036a0996316264fcaaaeb30dbea873da54162c241b8a7c4769617812d14511b0",
                "ncpatcher": "bada73642dace72ada0bb1f945b909c49e2d964c1136c987b4622452697544d0"}

local_include_folder = Path("/workspace/include")
local_clean_rom = Path("/workspace/nsmb.nds")

local_code_rom = Path("/app/temp.nds")
local_final_rom = Path("/workspace/final.nds")


def calculate_file_sha256(filepath):
    """Calcaulates the SHA256 hash of the provided file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string value in blocks
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def run_command(cmd, cwd=None, check=True):
    """Run a command and optionally print it"""

    # Always let stdout/stderr flow to terminal to prevent hanging
    # Tools like ncpatcher may expect live stdout
    result = subprocess.run(cmd, cwd=cwd, text=True)

    if check and result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        sys.exit(1)

    return result

# If a clean ROM has not been copied to the data volume, try to now
if not clean_rom.is_file():
    if not local_clean_rom.is_file():
        raise FileNotFoundError("[!]\tCould not find a clean ROM (Error Code 2)")
    
    if calculate_file_sha256(local_clean_rom) != sha256_hashes["nsmb"]:
        raise ValueError("[!]\tThe ROM provided does not seem to be a clean NSMB ROM (Error Code 3)")
    print("[i]\tClean ROM found: moving to the data volume")

    shutil.move(local_clean_rom, clean_rom)

# If the includes have not been copied to the data volume, convert & try to now
if not include_folder.is_dir():
    if not local_include_folder.is_dir():
        raise FileNotFoundError("[!]\tCould not find the NitroSDK/Nitro System includes folder (Error Code 4)")
    
    convert_sdk_cmd = [
        sys.executable, 'scripts/convert_sdk.py'
    ]

    run_command(convert_sdk_cmd)

    shutil.move(local_include_folder, include_folder)

# While it's likely intentional that the user used -v to overwrite these files: give a warning they have changed.
if calculate_file_sha256(arm9_json) != sha256_hashes["arm9"]:
    print("[i] Looks like you have modified arm9.json using docker run. There be dragons!")

if calculate_file_sha256(ncpatcher_json) != sha256_hashes["ncpatcher"]:
    print("[i] Looks like you have modified ncpatcher.json using docker run. There be dragons!")

# Apply code patches via insert_code.py (Thanks Gamerator!)
insert_code_cmd = [
        sys.executable, scripts_folder / "insert_code.py",
        clean_rom, local_code_rom,
        "--temp-dir", "nsmb"
    ]

run_command(insert_code_cmd, Path("/app"))

# Bundle ROM contents into final .nds via insert_files.py (Thanks Gamerator!)
insert_files_cmd = [
        sys.executable, scripts_folder / "insert_files.py",
        local_code_rom, local_final_rom,
    ]

run_command(insert_files_cmd, Path("/app"))

print("[i]\tAll done!")

input("Press enter to exit...")