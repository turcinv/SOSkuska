"""Isolated CSV job process; never imports Tk or handles UI objects."""
import argparse
import json
import sqlite3
from pathlib import Path
from csv_import import ImportValidationError
from flashcard_csv_import import read_csv, template_text
from csv_import_worker import publish_template
from storage import Store


def run(kind, active, selected, deck_id, deck_name):
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
                    preview['errors'].extend(store.check_flashcard_import(deck_id,preview['rows'],expected_deck_name=deck_name))
                except ImportValidationError as exc:
                    preview['errors'].extend(exc.errors)
            finally:store.close()
        preview['errors']=list(dict.fromkeys(preview['errors']))
        return preview
    with Path(selected).open(encoding='utf-8') as source:
        payload=json.load(source)
    store=Store.open_existing(active)
    try:
        result=store.import_flashcards(deck_id,payload,expected_deck_name=deck_name)
    except BaseException:
        store.close()
        raise
    # Preserve a known committed result even if connection cleanup fails.
    try:store.close()
    except (OSError,sqlite3.Error):pass
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind',choices=['parse','save','template']);parser.add_argument('active',type=Path);parser.add_argument('selected',type=Path)
    parser.add_argument('--deck-id',type=int);parser.add_argument('--deck-name',default='')
    args=parser.parse_args(argv)
    try:
        result={'state':'done','value':run(args.kind,args.active,args.selected,args.deck_id,args.deck_name)}
    except ImportValidationError as exc:
        result={'state':'invalid','errors':exc.errors,'value':str(exc)}
    except Exception as exc:
        result={'state':'error','value':str(exc).encode('utf-8',errors='replace').decode('utf-8')[:2000]}
    print(json.dumps(result,ensure_ascii=True),flush=True)


if __name__=='__main__':main()
