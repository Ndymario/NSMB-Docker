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
import yaml

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

configuration = Path("/workspace/nsmb.yaml")

workspace_root = Path("/workspace")


def calculate_file_sha256(filepath):
    """Calcaulates the SHA256 hash of the provided file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string value in blocks
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def run_command(cmd, cwd=None, check=True):
    """Run a command and wait for completion"""
    # Explicitly wait for completion by capturing output
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=False)
    if check and result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        sys.exit(1)
    return result


def load_config(path):
    if not path.is_file():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
    except yaml.YAMLError as error:
        print(f"[i] Failed to parse nsmb.yaml: {error}. Using defaults.\n")
        return {}
    if not isinstance(data, dict):
        print("[i] nsmb.yaml must contain a top-level mapping. Using defaults.\n")
        return {}
    return data


def get_config_value(config, *keys):
    current = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def resolve_config_path(value, base_dir, label):
    if value is None or value == "docker":
        return None
    if not isinstance(value, str):
        print(f"[i] Ignoring {label} in nsmb.yaml: expected a string path.\n")
        return None
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return path

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

print("[i] ROM and includes found, begining to patch!\n")

# While it's likely intentional that the user used -v to overwrite these files: give a warning they have changed.
if calculate_file_sha256(arm9_json) != sha256_hashes["arm9"]:
    print("[i] Looks like your arm9.json has been modified. There be dragons!\n")

if calculate_file_sha256(ncpatcher_json) != sha256_hashes["ncpatcher"]:
    print("[i] Looks like your ncpatcher.json has been modified. There be dragons!\n")

config = load_config(configuration)
if config:
    print("[i] nsmb.yaml detected in workspace, applying configuration:")

ncp_ver = get_config_value(config, "settings", "ncp_ver")
code_ref_ver = get_config_value(config, "settings", "code_ref_ver")
if ncp_ver not in (None, "docker") or code_ref_ver not in (None, "docker"):
    print("[i] Note: ncp_ver/code_ref_ver are build-time settings. Rebuild the image to apply them.\n")

# Apply code patches via insert_code.py (Thanks Gamerator!)
insert_code_input = resolve_config_path(
    get_config_value(config, "settings", "insert_code", "input_rom"),
    workspace_root,
    "settings.insert_code.input_rom",
)
insert_code_output = resolve_config_path(
    get_config_value(config, "settings", "insert_code", "output_rom"),
    workspace_root,
    "settings.insert_code.output_rom",
)
insert_code_language = get_config_value(config, "settings", "insert_code", "language")
insert_code_verbose = get_config_value(config, "settings", "insert_code", "verbose")
insert_code_temp_dir = resolve_config_path(
    get_config_value(config, "settings", "insert_code", "temp_dir"),
    workspace_root,
    "settings.insert_code.temp_dir",
)

insert_code_cmd = [
        sys.executable, scripts_folder / "insert_code.py",
        insert_code_input or clean_rom,
        insert_code_output or local_code_rom,
    ]

if isinstance(insert_code_language, str) and insert_code_language != "docker":
    insert_code_cmd.extend(["-l", insert_code_language])
if insert_code_verbose is True:
    insert_code_cmd.append("-v")
insert_code_cmd.extend(["--temp-dir", insert_code_temp_dir or "nsmb"])

print("[i] Launching NCPatcher and inserting your code into the ROM\n")
run_command(insert_code_cmd, Path("/app"))

# Bundle ROM contents into final .nds via insert_files.py (Thanks Gamerator!)
insert_files_input = resolve_config_path(
    get_config_value(config, "settings", "insert_files", "input_rom"),
    workspace_root,
    "settings.insert_files.input_rom",
)
insert_files_output = resolve_config_path(
    get_config_value(config, "settings", "insert_files", "output_rom"),
    workspace_root,
    "settings.insert_files.output_rom",
)
insert_files_language = get_config_value(config, "settings", "insert_files", "language")
insert_files_nitrofs_dir = resolve_config_path(
    get_config_value(config, "settings", "insert_files", "nitrofs_dir"),
    workspace_root,
    "settings.insert_files.nitrofs_dir",
)
insert_files_overrides = resolve_config_path(
    get_config_value(config, "settings", "insert_files", "overrides_file"),
    workspace_root,
    "settings.insert_files.overrides_file",
)
insert_files_fid_output = resolve_config_path(
    get_config_value(config, "settings", "insert_files", "fid_output"),
    workspace_root,
    "settings.insert_files.fid_output",
)

insert_files_cmd = [
        sys.executable, scripts_folder / "insert_files.py",
        insert_files_input or local_code_rom,
        insert_files_output or local_final_rom,
    ]

if isinstance(insert_files_language, str) and insert_files_language != "docker":
    insert_files_cmd.extend(["-l", insert_files_language])
if insert_files_nitrofs_dir:
    insert_files_cmd.extend(["--nitrofs-dir", insert_files_nitrofs_dir])
if insert_files_overrides:
    insert_files_cmd.extend(["--overrides-file", insert_files_overrides])
if insert_files_fid_output:
    insert_files_cmd.extend(["--fid-output", insert_files_fid_output])

print("[i] Inserting custom files from nitrofs.")
run_command(insert_files_cmd, Path("/app"))

print("\n\n[i] All done!\n")

input("Press enter to exit...")
