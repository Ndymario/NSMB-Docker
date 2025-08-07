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
import time

scripts_folder = Path("/data/scripts")
include_folder = Path("/data/include")
clean_rom = Path("/data/nsmb.nds")
arm9_json = Path("/data/arm9.json")
ncpatcher_json = Path("/data/ncpatcher.json")
buildrules_txt = Path("/data/buildrules.txt")
sha256_hashes = {"nsmb": "9f67fef1b4c73e966767f6153431ada3751dc1b0da2c70f386c14a5e3017f354",
                "arm9": "c2e5be51945dd863ab611ba144f4b8e792641a3a242c97980db4abc6fce266c3",
                "ncpatcher": "29833ee67f0ffaaa61872c3456ce01eae1733a99c1869b851eff1a2f74176f5c",
                "buildrules": "1e77a9db9625fa88e23230d6ed92956e40882cec10a496f9937344cbf885a957"}

local_scripts_folder = Path("/workspace/scripts")
local_include_folder = Path("/workspace/include")
local_clean_rom = Path("/workspace/nsmb.nds")
local_arm9_json = Path("/workspace/arm9.json")
local_ncpatcher_json = Path("/workspace/ncpatcher.json")
local_buildrules_txt = Path("/workspace/buildrules.txt")

local_code_rom = Path("/workspace/temp.nds")
local_final_rom = Path("/workspace/final.nds")


def calculate_file_sha256(filepath):
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


# If the scripts have not been copied to the data volume, try to now
if not scripts_folder.is_dir():
    if not local_scripts_folder.is_dir():
        raise FileNotFoundError("[!]\tCould not find NSMB-Docker scripts folder (Error Code 1)")
    
    shutil.move(local_scripts_folder, scripts_folder)

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
        raise FileNotFoundError("[!]\tCould not find the NitroSDK/Nitro System includes (Error Code 4)")
    
    convert_sdk_cmd = [
        sys.executable, 'scripts/convert_sdk.py'
    ]

    run_command(convert_sdk_cmd)

    shutil.move(local_include_folder, include_folder)

# If a clean arm9.json has not been copied to the data volume, try to now
if not arm9_json.is_file():
    if not local_arm9_json.is_file():
        raise FileNotFoundError("[!]\tCould not find a useable arm9.json (Error Code 5)")
    
    if calculate_file_sha256(local_arm9_json) != sha256_hashes["arm9"]:
        raise ValueError("[!]\tThe arm9.json provided does not seem to be the NSMB-Docker arm9.json (Error Code 6)")
    
    print("[i]\tarm9.json found: moving to the data volume")

    shutil.move(local_arm9_json, arm9_json)

# If a clean ncpatcher.json has not been copied to the data volume, try to now
if not ncpatcher_json.is_file():
    if not local_ncpatcher_json.is_file():
        raise FileNotFoundError("[!]\tCould not find a useable ncpatcher.json (Error Code 7)")
    
    if calculate_file_sha256(local_ncpatcher_json) != sha256_hashes["ncpatcher"]:
        raise ValueError("[!]\tThe ncpatcher.json provided does not seem to be the NSMB-Docker ncpatcher.json (Error Code 8)")
    
    print("[i]\tncpatcer.json found: moving to the data volume")

    shutil.move(local_ncpatcher_json, ncpatcher_json)

# If a clean buildrules.txt has not been copied to the data volume, try to now
if not buildrules_txt.is_file():
    if not local_buildrules_txt.is_file():
        raise FileNotFoundError("[!]\tCould not find a useable buildrules.txt (Error Code 9)")
    
    if calculate_file_sha256(local_buildrules_txt) != sha256_hashes["buildrules"]:
        raise ValueError("[!]\tThe buildrules.txt provided does not seem to be the NSMB-Docker buildrules.txt (Error Code 10)")
    
    print("[i]\tbuildrules.txt found: moving to the data volume")

    shutil.move(local_buildrules_txt, buildrules_txt)

# Copy the scripts folder into the current workspace if it doesn't already exist
if not local_scripts_folder.is_dir():
    try:
        shutil.copytree(scripts_folder, local_scripts_folder)
    except Exception as e:
        print("[!]\tFailed to copy the scripts folder!")
        exit(1)

# Copy the include folder into the current workspace if it doesn't already exist
if not local_include_folder.is_dir():
    try:
        shutil.copytree(include_folder, local_include_folder)
    except Exception as e:
        print("[!]\tFailed to copy the include folder!")
        exit(1)

# Copy the NCPatcher related files into the current workspace. Otherwise, warn that whatever is in the workspace is being used.
if local_buildrules_txt.is_file() and calculate_file_sha256(local_buildrules_txt) != sha256_hashes["buildrules"]:
    print("[i]\tWarning: the buildrules.txt in this folder is not the NSMB-Docker one. There be dragons!")

else:
    shutil.copyfile(buildrules_txt, local_buildrules_txt)

if local_arm9_json.is_file() and calculate_file_sha256(local_arm9_json) != sha256_hashes["arm9"]:
    print("[i]\tWarning: the arm9.json in this folder is not the NSMB-Docker one. There be dragons!")

else:
    shutil.copyfile(arm9_json, local_arm9_json)

if local_ncpatcher_json.is_file() and calculate_file_sha256(local_ncpatcher_json) != sha256_hashes["ncpatcher"]:
    print("[i]\tWarning: the ncatcher in this folder is not the NSMB-Docker one. There be dragons!")

else:
    shutil.copyfile(ncpatcher_json, local_ncpatcher_json)

# Apply code patches via insert_code.py (Thanks Gamerator!)
insert_code_cmd = [
        sys.executable, '/data/scripts/insert_code.py',
        clean_rom, local_code_rom,
        "--temp-dir", "nsmb"
    ]

run_command(insert_code_cmd, Path("/workspace/"))

# Bundle ROM contents into final .nds via insert_files.py (Thanks Gamerator!)
insert_files_cmd = [
        sys.executable, '/data/scripts/insert_files.py',
        local_code_rom, local_final_rom,
    ]

run_command(insert_files_cmd, Path("/workspace/"))

# Clean up the temp stuff
if local_code_rom.is_file():
    os.remove(local_code_rom)

if Path("/workspace/nsmb").is_dir():
    shutil.rmtree("/workspace/nsmb")

print("[i]\tAll done!")