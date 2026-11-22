"""Opt-in, machine-local daily backups. No Tk; file jobs run in a helper process."""
import hashlib
import json
import os
import tempfile
import uuid
from datetime import date
from pathlib import Path
from database_lock import DatabaseLease

MAX_CONFIG_BYTES = 16384
DEFAULT = dict(enabled=False,directory='',last_day=None,last_path='',plan_id='')


def config_path(active):
    return Path(str(Path(active).resolve())+'.backup-plan.json')


class ScheduleBusyError(ValueError):
    pass


def config_lease(active):
    try:return DatabaseLease(Path(str(Path(active).resolve())+'.backup-plan'),exclusive=True)
    except ValueError:raise ScheduleBusyError('Another window is backing up. Retry after it finishes.') from None


def fields(enabled,directory):
    if type(enabled) is not bool:
        raise ValueError('Choose whether daily backups are enabled.')
    if not isinstance(directory,str) or len(directory)>2000 or any(ord(c)<32 or ord(c)==127 for c in directory):
        raise ValueError('Choose an absolute local backup folder.')
    directory.encode('utf-8')
    if directory and not Path(directory).is_absolute():
        raise ValueError('Choose an absolute local backup folder.')
    if enabled and not directory:
        raise ValueError('Choose a backup folder before enabling daily backups.')
    return dict(enabled=enabled,directory=directory)


def load_config(active):
    path=config_path(active)
    if not path.exists():return dict(DEFAULT,token='missing',invalid=False)
    if path.is_symlink() or not path.is_file() or path.stat().st_nlink>1:
        raise ValueError('Use an ordinary local backup settings file.')
    with path.open('rb') as source:raw=source.read(MAX_CONFIG_BYTES+1)
    token=hashlib.sha256(raw).hexdigest()
    try:
        if len(raw)>MAX_CONFIG_BYTES:raise ValueError()
        saved=json.loads(raw)
        if not isinstance(saved,dict) or set(saved)!=set(DEFAULT):raise ValueError()
        fields(saved['enabled'],saved['directory'])
        if not isinstance(saved['plan_id'],str) or len(saved['plan_id'])!=32 or any(c not in '0123456789abcdef' for c in saved['plan_id']):raise ValueError()
        day=saved['last_day'];last=saved['last_path']
        if day is not None and (not isinstance(day,str) or date.fromisoformat(day).isoformat()!=day):raise ValueError()
        if not isinstance(last,str) or len(last)>4096:raise ValueError()
        if last and (not Path(last).is_absolute() or any(ord(c)<32 or ord(c)==127 for c in last)):raise ValueError()
        last.encode('utf-8')
    except (ValueError,TypeError,UnicodeError,KeyError,RecursionError):
        return dict(DEFAULT,token=token,invalid=True)
    return dict(saved,token=saved['plan_id'],invalid=False)


def config_bytes(config):
    raw=json.dumps({key:config[key] for key in DEFAULT},ensure_ascii=False).encode('utf-8')
    if len(raw)>MAX_CONFIG_BYTES:raise ValueError('Backup settings are too large.')
    return raw


def publish_config(active,config):
    path=config_path(active)
    # Never follow a replacement symlink/hardlink when publishing settings.
    if path.is_symlink() or (path.exists() and (not path.is_file() or path.stat().st_nlink>1)):
        raise ValueError('Use an ordinary local backup settings file.')
    raw=config_bytes(config)
    handle=tempfile.NamedTemporaryFile(prefix='.soskuska-plan-',dir=path.parent,delete=False)
    staging=Path(handle.name)
    try:
        with handle:handle.write(raw)
        os.replace(staging,path)
    finally:
        staging.unlink(missing_ok=True)
    return load_config(active)


def save_config(active,enabled,directory,expected_token):
    desired=fields(enabled,directory)
    with DatabaseLease(active),config_lease(active):
        current=load_config(active)
        if current['token']!=expected_token:
            raise ValueError('Backup settings changed in another window. Reload before saving.')
        saved=dict(current,**desired,plan_id=uuid.uuid4().hex)
        return publish_config(active,saved)


def due(config,today):
    return not config['invalid'] and config['enabled'] and (config['last_day'] is None or config['last_day']<today.isoformat())


def perform_backup(active):
    with DatabaseLease(active):
        try:lease=config_lease(active)
        except ScheduleBusyError:return dict(state='busy')
        with lease:return _perform_locked(active)


def _perform_locked(active):
    from backup import create_backup
    config=load_config(active);today=date.today()
    if not due(config,today):return dict(state='skipped')
    directory=Path(config['directory']).resolve()
    fields(True,str(directory))
    if not directory.is_dir():raise ValueError('The daily backup folder is unavailable. Choose an existing local folder and retry.')
    destination=directory/f'SOSkuska-auto-{today.isoformat()}-{uuid.uuid4().hex}.sqlite3'
    config_bytes(dict(config,last_day=today.isoformat(),last_path=str(destination)))
    created=create_backup(active,destination)
    # Publication and its receipt are separate; a crash between them may
    # leave an extra valid backup. Never delete or overwrite that file.
    publish_config(active,dict(config,last_day=today.isoformat(),last_path=str(created)))
    return dict(state='created',path=str(created))
