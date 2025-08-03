import os
import subprocess

def install_pz_mods(steamcmd_path, steam_user, game_id, mod_ids, steamcmd_mods_dir):
    """
    Download Project Zomboid mods using SteamCMD
    
    Args:
        steamcmd_path: Path to steamcmd.exe
        steam_user: Steam username (usually "anonymous")
        game_id: Steam game ID (108600 for Project Zomboid)
        mod_ids: List of Steam Workshop mod IDs
        steamcmd_mods_dir: Where SteamCMD should download mods
    """
    os.makedirs(steamcmd_mods_dir, exist_ok=True)

    for mod_id in mod_ids:
        print(f"⬇️ Downloading mod {mod_id}...")
        
        cmd = [
            steamcmd_path,
            "+force_install_dir", steamcmd_mods_dir,
            "+login", steam_user,
            "+workshop_download_item", game_id, mod_id,
            "+quit"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Downloaded mod {mod_id}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to download mod {mod_id}: {e}")