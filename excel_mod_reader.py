from excel_reader import get_excel_columns
import sys
from collections import Counter

def get_mod_ids(file_path='Book1.xlsx', value_col='D', flag_col='G', flag_value='1'):
    """
    Enhanced version with detailed debugging output and duplicate detection
    Returns: list of unique mod IDs, reports duplicates
    """
    print(f"\n=== MOD ID EXTRACTION WITH DUPLICATE DETECTION ===")
    print(f"Reading from: {file_path}")
    print(f"Looking for mod IDs in column: {value_col}")
    print(f"Using flag column: {flag_col} (value: '{flag_value}')")
    
    try:
        print("\n[1/3] Reading Excel columns...")
        data = get_excel_columns(
            file_path=file_path,
            desired_columns=[value_col, flag_col]
        )
        print(f"Raw data keys: {list(data.keys())}")
        
        value_key = f'Column_{value_col}'
        flag_key = f'Column_{flag_col}'
        
        if value_key not in data:
            print(f"❌ ERROR: Column {value_col} not found in Excel data")
            print(f"Available columns: {[k.replace('Column_','') for k in data.keys()]}")
            return []
            
        if flag_key not in data:
            print(f"❌ ERROR: Column {flag_col} not found in Excel data")
            return []
        
        print("\n[2/3] Sample data from columns:")
        print(f"{value_col} (first 5): {data[value_key][:5]}")
        print(f"{flag_col} (first 5): {data[flag_key][:5]}")
        
        mod_ids = []
        duplicates = []
        min_length = min(len(data[value_key]), len(data[flag_key]))
        print(f"\n[3/3] Processing {min_length} rows...")
        
        found_count = 0
        for i in range(min_length):
            flag_val = data[flag_key][i]
            mod_val = data[value_key][i]
            
            if i % 20 == 0 and i > 0:
                print(f"  Processed {i} rows... Found {found_count} mods so far")
            
            try:
                if flag_val is not None and str(flag_val).strip() == str(flag_value).strip():
                    if mod_val is not None:
                        try:
                            mod_id = str(int(float(mod_val)))
                            
                            if mod_id in mod_ids:
                                duplicates.append(mod_id)
                                print(f"  ! Duplicate found: {mod_id} (Row {i+1})")
                            else:
                                mod_ids.append(mod_id)
                                found_count += 1
                                
                        except (ValueError, TypeError) as e:
                            print(f"⚠️ Row {i+1}: Invalid mod ID '{mod_val}' - {str(e)}")
            except Exception as e:
                print(f"⚠️ Error processing row {i+1}: {str(e)}")
                continue

        duplicate_report = ""
        if duplicates:
            dup_counts = Counter(duplicates)
            duplicate_report = "\n╔══════════════════════════════╗"
            duplicate_report += "\n║        DUPLICATE REPORT       ║"
            duplicate_report += "\n╠══════════════════════════════╣"
            duplicate_report += "\n║ Mod ID           Occurrences ║"
            duplicate_report += "\n╠══════════════════════════════╣"
            
            for mod_id, count in dup_counts.most_common():
                total = count + 1
                duplicate_report += f"\n║ {mod_id:<16} {total:>11} ║"
            
            duplicate_report += "\n╚══════════════════════════════╝"
        
        print(f"\n✅ Found {len(mod_ids)} unique mod IDs")
        print(f"⚠️  Found {len(duplicates)} duplicates")
        
        if duplicate_report:
            print(duplicate_report)
        
        if len(mod_ids) > 0:
            print(f"\nSample of first 5 unique IDs: {mod_ids[:5]}...")
        
        return mod_ids
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}", file=sys.stderr)
        return []