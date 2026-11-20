"""Isolated CSV job process; never imports Tk or handles UI objects."""
import argparse
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from backup import protect_path
from csv_import import ImportValidationError, read_csv, template_text
from storage import Store


def publish_template(active, selected, contents):
    target=protect_path(selected,active)
    if target.exists():
        raise FileExistsError('Choose an unused filename; existing files are never overwritten.')
    with tempfile.TemporaryDirectory(prefix='.soskuska-csv-template-',dir=target.parent) as folder:
        staging=Path(folder)/'template.csv'
        staging.write_bytes(contents.encode('utf-8'))
        if os.name=='nt':os.rename(staging,target)
        else:
            os.link(staging,target)
            staging.unlink()
    return str(target)


def run(kind, active, selected, subject_id, subject_name):
    if kind=='template':
        return publish_template(active,selected,template_text())
    if not Path(active).is_file():
        raise ValueError('The active database file is missing. Reopen the app before importing.')
    if kind=='parse':
        preview=read_csv(selected)
        if preview['rows']:
            store=Store.open_existing(active,readonly=True)
            try:
                try:
                    preview['errors'].extend(store.check_question_import(subject_id,preview['rows'],expected_subject_name=subject_name))
                except ImportValidationError as exc:
                    preview['errors'].extend(exc.errors)
            finally:store.close()
        preview['errors']=list(dict.fromkeys(preview['errors']))
        return preview
    with Path(selected).open(encoding='utf-8') as source:
        payload=json.load(source)
    store=Store.open_existing(active)
    try:
        result=store.import_questions(subject_id,payload,expected_subject_name=subject_name)
    except BaseException:
        store.close()
        raise
    # Preserve a known committed result even if connection cleanup fails.
    try:store.close()
    except (OSError,sqlite3.Error):pass
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind',choices=['parse','save','template']);parser.add_argument('active',type=Path);parser.add_argument('selected',type=Path)
    parser.add_argument('--subject-id',type=int);parser.add_argument('--subject-name',default='')
    args=parser.parse_args()
    try:
        result={'state':'done','value':run(args.kind,args.active,args.selected,args.subject_id,args.subject_name)}
    except ImportValidationError as exc:
        result={'state':'invalid','errors':exc.errors,'value':str(exc)}
    except Exception as exc:
        result={'state':'error','value':str(exc).encode('utf-8',errors='replace').decode('utf-8')[:2000]}
    print(json.dumps(result,ensure_ascii=True),flush=True)


if __name__=='__main__':main()
