def write_mod_list_to_file(mod_ids, output_file='mod_list.txt', delimiter=', '):
    """
    Writes ONLY UNIQUE mod IDs to a text file
    """
    try:
        unique_ids = list({str(int(float(mod_id))) for mod_id in mod_ids})

        with open(output_file, 'w') as f:
            f.write(delimiter.join(unique_ids))
        
        print(f"✅ Wrote {len(unique_ids)} UNIQUE mod IDs to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error writing mod list: {str(e)}", file=sys.stderr)
        return False