import json
from pathlib import Path

def main():
    archive_dir = Path('input/archive')
    out_file = Path('input/data.jsonl')
    out_file.parent.mkdir(parents=True, exist_ok=True)

    html_files = sorted(archive_dir.glob('*.html'))
    with out_file.open('w', encoding='utf-8') as fw:
        for fp in html_files:
            obj = {
                "full_model_name": fp.stem,
                "configuration_name": "TBD",
                "country_name": "Australia",
                "year": "2025",
                "data_filename": str(fp)
            }
            fw.write(json.dumps(obj, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    main()
