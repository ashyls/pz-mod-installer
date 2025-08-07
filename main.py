import json
from pz_mod_installer import install_pz_mods
from excel_mod_reader import get_mod_ids
from write_to_txt import write_to_txt
from flatten_mods_folder import flatten_mod_folders
from find_required_mods import get_mod_dependencies
import os
import time
import sys
from typing import List, Tuple, Set

# Constants
CONFIG_FILE = "config.json"
REQUIRED_KEYS = {
    "steamcmd_path": "Path to steamcmd.exe",
    "steam_user": "Steam username (anonymous for public)",
    "game_id": "Project Zomboid app ID (108600)",
    "steamcmd_mods_dir": "SteamCMD working directory",
    "zomboid_mods_dir": "Project Zomboid mods directory"
}

class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_header(title: str, color: str = Color.CYAN) -> None:
    """Print a formatted section header with dynamic width."""
    width = max(50, len(title) + 8)
    print(f"\n{color}{'=' * width}")
    print(f"=== {title.upper()} ===")
    print(f"{'=' * width}{Color.RESET}")

def print_status(message: str, status: str = "INFO") -> None:
    """Print a status message with colored prefix."""
    status_colors = {
        "INFO": Color.BLUE,
        "SUCCESS": Color.GREEN,
        "WARNING": Color.YELLOW,
        "ERROR": Color.RED
    }
    color = status_colors.get(status.upper(), Color.RESET)
    print(f"{color}[{status.upper()}] {message}{Color.RESET}")

def load_config() -> dict:
    """Load configuration from JSON file with validation."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            
            missing_keys = [key for key in REQUIRED_KEYS if key not in config]
            if missing_keys:
                print_status("Missing required configuration keys:", "ERROR")
                for key in missing_keys:
                    print(f"  - {key}: {REQUIRED_KEYS[key]}")
                sys.exit(1)
                
            return config
            
    except FileNotFoundError:
        print_status(f"Config file not found: {CONFIG_FILE}", "ERROR")
        print("Please create a config.json file with these required keys:")
        for key, desc in REQUIRED_KEYS.items():
            print(f"  - {key}: {desc}")
        sys.exit(1)
    except json.JSONDecodeError:
        print_status(f"Invalid JSON format in {CONFIG_FILE}", "ERROR")
        sys.exit(1)
    except Exception as e:
        print_status(f"Error loading config: {str(e)}", "ERROR")
        sys.exit(1)

def get_workshop_path(config: dict) -> str:
    """Construct the workshop path from configuration."""
    return os.path.join(
        config["steamcmd_mods_dir"],
        "steamapps",
        "workshop",
        "content",
        config["game_id"]
    )

def get_all_dependencies(initial_mods: List[str]) -> Tuple[List[str], List[str]]:
    """Get all dependencies for the given mod IDs."""
    queue = initial_mods.copy()
    visited = set()
    all_deps = set()
    dependency_tree = {}

    print_status(f"Checking dependencies for {len(initial_mods)} mods...")
    
    while queue:
        mod_id = queue.pop()
        if mod_id in visited:
            continue
            
        visited.add(mod_id)
        print_status(f"Processing mod ID: {mod_id}")
        
        try:
            deps = get_mod_dependencies(mod_id)
            if deps:
                dependency_tree[mod_id] = deps
                print_status(f"Found {len(deps)} dependencies for {mod_id}:")
                for dep in deps:
                    print(f"  → {dep} (https://steamcommunity.com/sharedfiles/filedetails/?id={dep})")
                    if dep not in visited and dep not in all_deps:
                        all_deps.add(dep)
                        queue.append(dep)
        except Exception as e:
            print_status(f"Failed to get dependencies for {mod_id}: {str(e)}", "WARNING")

    return list(all_deps), dependency_tree

def print_mod_summary(mod_ids: List[str], dep_mod_ids: List[str], dependency_tree: dict) -> None:
    """Print a summary of mods to be installed."""
    print_header("Installation Summary")
    
    print_status(f"Total mods to install: {len(mod_ids)}")
    if mod_ids:
        print("Primary mods:")
        for mod_id in mod_ids:
            print(f"  - {mod_id}")
    
    print_status(f"Total dependencies to install: {len(dep_mod_ids)}")
    if dep_mod_ids:
        print("Dependencies:")
        for dep_id in dep_mod_ids:
            print(f"  - {dep_id}")
    
    if dependency_tree:
        print("\nDependency tree:")
        for mod_id, deps in dependency_tree.items():
            print(f"{mod_id} depends on: {', '.join(deps) if deps else 'None'}")

def main():
    print_header("Project Zomboid Mod Installer")
    print(f"Start Time: {time.ctime()}\n")

    flag_input = input("Please enter your flag to check: ").strip()
    config = load_config()

    # Mod processing
    print_header("Reading Mod List")
    try:
        mod_names, mod_ids = get_mod_ids(flag_value=flag_input)
    except Exception as e:
        print_status(f"Failed to read mod list: {str(e)}", "ERROR")
        sys.exit(1)
    
    if not mod_ids:
        print_status("No mods found to install! Check your Excel file and filter criteria", "WARNING")
        sys.exit(1)
    
    print_status(f"Found {len(mod_ids)} mods in the list")
    print(f"Sample mod IDs: {', '.join(mod_ids[:5])}{'...' if len(mod_ids) > 5 else ''}")

    print_header("Resolving Dependencies")
    dep_mod_ids, dependency_tree = get_all_dependencies(mod_ids)
    
    dep_mod_ids = [dep for dep in dep_mod_ids if dep not in mod_ids]
    
    print_mod_summary(mod_ids, dep_mod_ids, dependency_tree)
    
    all_mod_ids = mod_ids + dep_mod_ids
    if not all_mod_ids:
        print_status("No mods to install after dependency resolution", "WARNING")
        sys.exit(0)

    time.sleep(2)
    
    # Installation process
    print_header("Mod Installation")
    try:
        print_status(f"Starting installation of {len(all_mod_ids)} mods...")
        
        install_pz_mods(
            steamcmd_path=config["steamcmd_path"],
            steam_user=config["steam_user"],
            game_id=config["game_id"],
            mod_ids=all_mod_ids,
            steamcmd_mods_dir=config["steamcmd_mods_dir"]
        )
        
        workshop_path = get_workshop_path(config)
        if not os.path.exists(workshop_path):
            raise FileNotFoundError(f"Workshop path not found: {workshop_path}")

        print_status("Reorganizing mod folders...")
        flatten_mod_folders(workshop_path, config["zomboid_mods_dir"])
        print_status("All mods installed and organized successfully!", "SUCCESS")

    except Exception as e:
        print_status(f"Installation failed: {str(e)}", "ERROR")
        sys.exit(1)
    finally:
        print(f"\n⏱️ Process completed at: {time.ctime()}")
    
    # File operations
    print_header("Creating Output Files")
    try:
        if not write_to_txt(mod_ids, 'modId.txt', ';'):
            print_status("Failed to create mod list file", "WARNING")
        else:
            print_status(f"Created modId.txt with {len(mod_ids)} entries", "SUCCESS")
            
        if not write_to_txt(mod_names, 'workshop.txt', ';'):
            print_status("Failed to create workshop names file", "WARNING")
        else:
            print_status(f"Created workshop.txt with {len(mod_names)} entries", "SUCCESS")
    except Exception as e:
        print_status(f"Error creating output files: {str(e)}", "ERROR")

if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    try:
        main()
    except KeyboardInterrupt:
        print_status("Process interrupted by user", "WARNING")
        sys.exit(1)