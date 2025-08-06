import sys

def write_to_txt(data, output_file, delimiter=', '):
    """Writes unique mod IDs to a text file.

    Args:
        data: List of mod IDs (may contain duplicates)
        output_file: Name/path of the output text file
        delimiter: Separator between IDs (default: ', ')
    """
    try:
        with open(output_file, 'w') as f:
            f.write(delimiter.join(data))
        
        print(f"✅ Wrote {len(data)} Datas to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error writing mod list: {str(e)}", file=sys.stderr)
        return False