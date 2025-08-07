import os
import shutil

def flatten_mod_folders(workshop_path, zomboid_mods_dir):
    """
    Flatten the Steam Workshop folder structure by moving mods directly to the Zomboid mods directory.
    
    Args:
        workshop_path: Path to Steam Workshop downloads
        zomboid_mods_dir: Path to Project Zomboid mods directory
    """
    print("\n♻️ Reorganizing mod folders...")
    moved_count = 0
    
    os.makedirs(zomboid_mods_dir, exist_ok=True)
    
    if not os.path.exists(workshop_path):
        raise FileNotFoundError(f"Workshop path not found: {workshop_path}")
    
    for mod_id in os.listdir(workshop_path):
        mod_folder = os.path.join(workshop_path, mod_id, "mods")
        if not os.path.exists(mod_folder):
            print(f"  ⚠️ No mods folder found for {mod_id}")
            continue
        
        for content_folder in os.listdir(mod_folder):
            src = os.path.join(mod_folder, content_folder)
            dest = os.path.join(zomboid_mods_dir, content_folder)
            
            print(f"  Processing: {content_folder}")
            
            if os.path.exists(dest):
                print(f"    Removing existing: {content_folder}")
                shutil.rmtree(dest)
            
            try:
                shutil.move(src, dest)
                moved_count += 1
                print(f"    ➔ Moved to: {dest}")
            except Exception as e:
                print(f"    ❌ Failed to move {content_folder}: {str(e)}")
                continue

    print(f"\n✅ Reorganized {moved_count} mods to {zomboid_mods_dir}")