from write_to_txt import write_to_txt
from datetime import datetime
import os
import subprocess
import time
import random

def install_pz_mods(steamcmd_path, steam_user, game_id, mod_ids, steamcmd_mods_dir, timeout=600):
    os.makedirs(steamcmd_mods_dir, exist_ok=True)
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    total_mods = len(mod_ids)
    successful = 0
    failed = []

    print(f"\n📦 Starting download of {total_mods} mods...\n")

    for idx, mod_id in enumerate(mod_ids, 1):
        max_attempts = 3
        attempt = 1
        success = False

        while attempt <= max_attempts and not success:
            print(f"🔹 Mod {idx}/{total_mods} | Attempt {attempt}/{max_attempts} | ID: {mod_id}")
            
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

                while process.poll() is None:
                    if time.time() - start_time > timeout:
                        process.terminate()
                        raise subprocess.TimeoutExpired(cmd, timeout)
                    time.sleep(1)

                if process.returncode == 0:
                    print(f"✅ Success! ({idx}/{total_mods})\n")
                    successful += 1
                    success = True
                else:
                    error = process.stderr.read().decode('utf-8').strip()
                    print(f"⚠️ Attempt {attempt} failed: {error or 'Unknown error'}")
                    attempt += 1
                    if attempt <= max_attempts:
                        time.sleep(random.uniform(2, 5))  # Random delay before retry

            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout after {timeout}s")
                attempt += 1
            except Exception as e:
                print(f"⚠️ Crash: {str(e)}")
                attempt += 1

        if not success:
            failed.append(mod_id)
            with open(os.path.join(logs_dir, "failed_mods.csv"), "a") as f:
                f.write(f"{mod_id},{datetime.now().isoformat()}\n")

        if idx < total_mods:
            time.sleep(random.uniform(1, 3))

    print(f"\n{'='*50}")
    print(f"📊 RESULTS:")
    print(f"✅ Successful: {successful}/{total_mods}")
    print(f"❌ Failed: {len(failed)}/{total_mods}")
    if failed:
        print("\n🔴 Failed mods (saved to logs/failed_mods.csv):")
        for mod in failed:
            print(f"- https://steamcommunity.com/sharedfiles/filedetails/?id={mod}")
    print(f"{'='*50}\n")