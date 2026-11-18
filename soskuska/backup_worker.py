"""Isolated database-job process: no Tk imports or UI object finalizers."""
import argparse
import json
import shutil
from pathlib import Path
from types import SimpleNamespace
from backup import PreparedBackup, create_backup, restore_backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=['backup','validate','restore'])
    parser.add_argument('active', type=Path)
    parser.add_argument('selected', type=Path)
    parser.add_argument('--staging', type=Path)
    args = parser.parse_args()
    try:
        if args.kind == 'backup':
            result = str(create_backup(args.active,args.selected))
        elif args.kind == 'validate':
            prepared = PreparedBackup(args.selected,args.active)
            try:
                shutil.copyfile(prepared.path,args.staging)
                result = prepared.counts
            finally:
                prepared.close()
        else:
            result = str(restore_backup(args.active,SimpleNamespace(path=args.selected)))
    except Exception as exc:
        result = ['error',str(exc).encode('utf-8',errors='replace').decode('utf-8')[:2000]]
    else:
        result = ['done',result]
    print(json.dumps(result,ensure_ascii=True),flush=True)


if __name__ == '__main__':
    main()
