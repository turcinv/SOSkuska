"""Validate application domains as well as SQLite's permissive storage types."""
from datetime import date, datetime
from content import topic_fields, question_fields
from repetition import deck_fields, card_fields
from practice import practice_settings
from storage import subject_fields


def validate_records(store, tables, check):
    db = store.db
    for name in tables:
        fields = db.execute(f'PRAGMA table_info("{name}")').fetchall()
        for row in db.execute(f'SELECT * FROM "{name}"'):
            check()
            for field, value in zip(fields, row):
                if value is None:
                    continue
                column, kind = field[1], field[2]
                if kind == 'INTEGER' and type(value) is not int:
                    raise ValueError(f'Invalid integer in {name}.{column}.')
                if kind == 'TEXT':
                    if not isinstance(value, str):
                        raise ValueError(f'Invalid text in {name}.{column}.')
                    value.encode('utf-8')
                    if column == 'day' and date.fromisoformat(value).isoformat() != value:
                        raise ValueError('Invalid calendar day in backup.')
                    if column.endswith('_at'):
                        parsed = datetime.fromisoformat(value)
                        if name not in ('subjects', 'questions') and parsed.utcoffset() is None:
                            raise ValueError('Backup study timestamps must include a time zone.')
            if name == 'subjects':
                _, key, _, _ = subject_fields(row['name'],row['description'],row['exam_date'] or '')
                if key != row['name_key']:
                    raise ValueError('Invalid subject name key.')
            elif name == 'topics':
                if topic_fields(row['name'])[1] != row['name_key']:
                    raise ValueError('Invalid topic name key.')
            elif name in ('questions', 'practice_items'):
                question_fields(row['prompt'],[row['option_'+k] for k in 'abcd'],row['correct_option'],row['difficulty'],row['explanation'])
            elif name == 'decks':
                if deck_fields(row['name'],row['description'])[1] != row['name_key']:
                    raise ValueError('Invalid deck name key.')
            elif name == 'flashcards':
                card_fields(row['front'],row['back'])
            elif name == 'review_events':
                card_fields(row['front'],row['back'])
                if not 0 <= row['interval_days'] <= 365 or row['card_revision'] < 0:
                    raise ValueError('Invalid card review history.')
            elif name == 'tasks' and row['done'] not in (0,1):
                raise ValueError('Invalid checklist value.')
            elif name == 'sqlite_sequence':
                if not isinstance(row['name'],str) or row['name'] not in tables or type(row['seq']) is not int or row['seq'] < 0:
                    raise ValueError('Invalid saved ID sequence.')
    for row in db.execute('SELECT * FROM practice_attempts'):
        check()
        practice_settings(row['question_count'],row['time_limit_minutes'],row['difficulty'])
        positions = [r[0] for r in db.execute('SELECT position FROM practice_items WHERE attempt_id=? ORDER BY position',(row['id'],))]
        if positions != list(range(row['question_count'])):
            raise ValueError('Practice questions do not match their saved attempt.')
        if (row['status']=='completed') != (row['completed_at'] is not None):
            raise ValueError('Practice completion metadata is inconsistent.')
        if (row['time_limit_minutes'] is None) != (row['deadline_at'] is None):
            raise ValueError('Practice deadline metadata is inconsistent.')
    sequences = list(db.execute('SELECT name,seq FROM sqlite_sequence'))
    if len({r[0] for r in sequences}) != len(sequences):
        raise ValueError('Duplicate saved ID sequences.')
    for name, seq in sequences:
        if name not in ('subjects','topics','questions','practice_attempts','decks','flashcards','review_events','tutor_conversations','tutor_turns'):
            raise ValueError('Unexpected saved ID sequence.')
        if seq < db.execute(f'SELECT COALESCE(MAX(id),0) FROM "{name}"').fetchone()[0]:
            raise ValueError('Saved ID sequence is behind existing data.')
    saved = store.preferences()
    if saved['invalid'] or type(saved['revision']) is not int or saved['revision'] < 0:
        raise ValueError('The backup contains invalid preferences.')

    names = {r[0] for r in sequences}
    for name in ('subjects','topics','questions','practice_attempts','decks','flashcards','review_events','tutor_conversations','tutor_turns'):
        if name not in names and db.execute(f'SELECT 1 FROM "{name}" LIMIT 1').fetchone():
            raise ValueError('Missing saved ID sequence.')

    from tutor_history import owner_fields, turn_fields
    from csv_import import safe_text
    for conversation in db.execute('SELECT * FROM tutor_conversations'):
        check()
        if owner_fields(conversation['endpoint'],conversation['model']) != (conversation['endpoint'],conversation['model']):
            raise ValueError('Invalid conversation owner.')
        title = safe_text(conversation['title'])
        if not title or len(title)>80 or ' '.join(title.split())!=title or conversation['revision']<0:
            raise ValueError('Invalid conversation title or revision.')
        turns = list(db.execute('SELECT * FROM tutor_turns WHERE conversation_id=? ORDER BY position',(conversation['id'],)))
        if not 1 <= len(turns) <= 12 or [r['position'] for r in turns]!=list(range(len(turns))):
            raise ValueError('Invalid conversation turn positions.')
        if conversation['revision'] != 2*len(turns)-int(turns[-1]['status']=='pending'):
            raise ValueError('Invalid conversation revision.')
        for index, turn in enumerate(turns):
            check()
            if turn_fields(turn['prompt'],turn['answer'],turn['language'],turn['status']) != (turn['prompt'],turn['answer'],turn['language'],turn['status']):
                raise ValueError('Invalid conversation text.')
            if turn['status']=='pending' and (index!=len(turns)-1 or turn['answer']):
                raise ValueError('Invalid unfinished conversation reply.')
