from write_to_txt import write_to_txt
import os
import subprocess
import time


def install_pz_mods(steamcmd_path, steam_user, game_id, mod_ids, steamcmd_mods_dir, timeout=300):
    """
    Download Project Zomboid mods using SteamCMD with timeout handling
    
    Args:
        steamcmd_path: Path to steamcmd.exe
        steam_user: Steam username (usually "anonymous")
        game_id: Steam game ID (108600 for Project Zomboid)
        mod_ids: List of Steam Workshop mod IDs
        steamcmd_mods_dir: Where SteamCMD should download mods
        timeout: Maximum time in seconds to wait for a mod download (default: 300s/5min)
    """
    os.makedirs(steamcmd_mods_dir, exist_ok=True)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join( script_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

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
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            start_time = time.time()
            while True:
                if process.poll() is not None:
                    break
                    
                if time.time() - start_time > timeout:
                    process.terminate()
                    raise subprocess.TimeoutExpired(cmd, timeout)
                
                time.sleep(1)
            
            if process.returncode == 0:
                print(f"✅ Successfully downloaded mod {mod_id}")
            else:
                _, stderr = process.communicate()
                error_msg = stderr.decode('utf-8').strip()
                print(f"❌ Failed to download mod {mod_id} (Error {process.returncode})")
                if error_msg:
                    print(f"Error details: {error_msg}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout ({timeout} seconds) reached while downloading mod {mod_id}")
            write_to_txt(f"https://steamcommunity.com/sharedfiles/filedetails/?id={mod_id}", "logs/failed_mods.txt")
        except Exception as e:
            print(f"❌ Unexpected error downloading mod {mod_id}: {str(e)}")