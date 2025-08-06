import json
from pz_mod_installer import install_pz_mods
from excel_mod_reader import get_mod_ids
from mod_list_writer import write_mod_list_to_file
from flatten_mods_folder import flatten_mod_folders
import os
import time
import sys

# Constants
CONFIG_FILE = "config.json"
REQUIRED_KEYS = {
    "steamcmd_path": "Path to steamcmd.exe",
    "steam_user": "Steam username (anonymous for public)",
    "game_id": "Project Zomboid app ID (108600)",
    "steamcmd_mods_dir": "SteamCMD working directory",
    "zomboid_mods_dir": "Project Zomboid mods directory"
}

def print_header(title):
    """Print a formatted section header with dynamic width."""
    width = max(50, len(title) + 8)
    print(f"\n{'=' * width}")
    print(f"=== {title.upper()} ===")
    print(f"{'=' * width}")

def load_config():
    """Load configuration from JSON file with validation."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            
            # Validate all required keys are present
            missing_keys = [key for key in REQUIRED_KEYS if key not in config]
            if missing_keys:
                print("❌ Missing required configuration keys:")
                for key in missing_keys:
                    print(f"  - {key}: {REQUIRED_KEYS[key]}")
                sys.exit(1)
                
            return config
            
    except FileNotFoundError:
        print(f"❌ Config file not found: {CONFIG_FILE}")
        print("Please create a config.json file with these required keys:")
        for key, desc in REQUIRED_KEYS.items():
            print(f"  - {key}: {desc}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON format in {CONFIG_FILE}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading config: {str(e)}")
        sys.exit(1)

def get_workshop_path(config):
    """Construct the workshop path from configuration."""
    return os.path.join(
        config["steamcmd_mods_dir"],
        "steamapps",
        "workshop",
        "content",
        config["game_id"]
    )

def main():
    print_header("Project Zomboid Mod Installer")
    print(f"Start Time: {time.ctime()}\n")

    flag_input = input("please write your flag to check : ")
    config = load_config()

    # Mod processing
    print_header("Reading Mod List")
    mod_list = get_mod_ids(flag_value=flag_input)
    
    if not mod_list:
        print("⚠️ Error: No mods found to install!")
        print("Please check your Excel file and filter criteria")
        sys.exit(1)
    
    print(f"✅ Found {len(mod_list)} mods to install")
    print(f"Sample IDs: {', '.join(mod_list[:5])}...")

    # File operations
    print_header("Creating Mod List File")
    if not write_mod_list_to_file(mod_list, 'mod_list.txt', ', '):
        print("⚠️ Warning: Failed to create mod list file")
        sys.exit(1)

    # Configuration display
    print_header("Installation Configuration")
    config_display = config.copy()
    config_display["mod_ids"] = f"[list of {len(mod_list)} mods]"
    for key, value in config_display.items():
        print(f"{key.replace('_', ' ').title():>20}: {value}")

    # Installation process
    print_header("Mod Installation")
    try:
        config["mod_ids"] = mod_list
        install_pz_mods(
            steamcmd_path= config["steamcmd_path"],
            steam_user= config["steam_user"],
            game_id= config["game_id"],
            mod_ids= config["mod_ids"],
            steamcmd_mods_dir= config["steamcmd_mods_dir"]

        )

        print(config)
        
        workshop_path = get_workshop_path(config)
        if not os.path.exists(workshop_path):
            raise FileNotFoundError(f"Workshop path not found: {workshop_path}")

        flatten_mod_folders(workshop_path, config["zomboid_mods_dir"])
        print("\n✅ All mods installed and organized successfully!")
    except Exception as e:
        print(f"\n❌ Critical Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        print(f"\n⏱️ Process completed at: {time.ctime()}")

if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    main()