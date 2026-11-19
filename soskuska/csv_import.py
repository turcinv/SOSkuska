"""Bounded UTF-8 question CSV parsing and canonical row rules; no Tk/SQLite."""
import csv
import io
from pathlib import Path
from content import DIFFICULTIES, question_fields, topic_fields

MAX_BYTES = 2 * 1024 * 1024
MAX_ROWS = 500
COLUMNS = ('topic','prompt','option_a','option_b','option_c','option_d','correct_option','difficulty','explanation')
REQUIRED = set(COLUMNS) - {'topic','explanation'}


class ImportValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('Import was not saved. Resolve the listed validation issues first.')


def safe_text(value):
    if not isinstance(value,str):
        raise ValueError('Expected text.')
    value.encode('utf-8')
    if any(ord(c)<32 and c not in '\t\r\n' for c in value) or '\x7f' in value:
        raise ValueError('Unsupported control character in text.')
    return value


def canonical_row(record, topic, fields):
    if type(record) is not int or record < 2:
        raise ValueError('Invalid CSV record number.')
    if not isinstance(fields,(list,tuple)) or len(fields)!=8:
        raise ValueError('Expected question, four answers, correct answer, difficulty and explanation.')
    topic=safe_text(topic)
    name,key=topic_fields(topic) if topic.strip() else ('','')
    prompt,*rest=fields
    for value in [prompt,*rest[:4],rest[5],rest[6]]:
        safe_text(value)
    values=question_fields(prompt,rest[:4],rest[4],rest[5],rest[6])
    return {'record':record,'topic':name,'fields':list(values)}


def signature(row):
    key=topic_fields(row['topic'])[1] if row['topic'] else ''
    return (key,*row['fields'])


def validate_rows(rows):
    if not isinstance(rows,(list,tuple)) or not 1 <= len(rows) <= MAX_ROWS:
        raise ImportValidationError([f'Choose 1–{MAX_ROWS} question records.'])
    normalized=[];errors=[];seen={}
    for row in rows:
        try:
            current=canonical_row(row['record'],row['topic'],row['fields'])
        except (ValueError,TypeError,KeyError,UnicodeError) as exc:
            errors.append(f'CSV record {row.get("record","?") if isinstance(row,dict) else "?"}: {exc}')
            continue
        key=signature(current)
        if key in seen:
            errors.append(f'CSV record {current["record"]}: Duplicate of record {seen[key]} (all question fields and topic).')
        else:seen[key]=current['record']
        normalized.append(current)
    return normalized,errors


def parse_csv(text):
    safe_text(text)
    if len(text.encode('utf-8')) > MAX_BYTES:
        raise ValueError('CSV file exceeds 2 MiB.')
    reader=csv.reader(io.StringIO(text,newline=''),strict=True)
    try:
        header=next(reader)
    except StopIteration:
        raise ValueError('CSV file is empty.') from None
    except csv.Error as exc:
        raise ValueError(f'Invalid CSV header: {exc}') from None
    header=[name.strip().casefold() for name in header]
    if len(header)!=len(set(header)) or any(not name for name in header):
        raise ValueError('CSV headers must be distinct and nonempty.')
    missing=REQUIRED-set(header);unknown=set(header)-set(COLUMNS)
    if missing or unknown:
        details=[]
        if missing:details.append('missing: '+', '.join(sorted(missing)))
        if unknown:details.append('unknown: '+', '.join(sorted(unknown)))
        raise ValueError('Use the comma-separated CSV template headers ('+'; '.join(details)+').')
    rows=[];errors=[];total=0
    try:
        for record,cells in enumerate(reader,2):
            if not cells or not any(cell.strip() for cell in cells):continue
            total+=1
            if total>MAX_ROWS:
                errors.append(f'CSV exceeds {MAX_ROWS} nonblank question records. Split the file.');break
            if len(cells)!=len(header):
                errors.append(f'CSV record {record}: Expected {len(header)} cells, found {len(cells)}.');continue
            values=dict(zip(header,cells))
            try:
                letter=values['correct_option'].strip().upper()
                if letter not in ('A','B','C','D'):
                    raise ValueError('Correct answer must be A, B, C or D.')
                difficulty=next((d for d in DIFFICULTIES if d.casefold()==values['difficulty'].strip().casefold()),values['difficulty'].strip())
                fields=[values['prompt'],*[values['option_'+k] for k in 'abcd'],'ABCD'.index(letter),difficulty,values.get('explanation','')]
                rows.append(canonical_row(record,values.get('topic',''),fields))
            except (ValueError,UnicodeError) as exc:
                errors.append(f'CSV record {record}: {exc}')
    except csv.Error as exc:
        errors.append(f'Invalid CSV near physical line {reader.line_num}: {exc}')
    if rows:
        rows,duplicates=validate_rows(rows);errors.extend(duplicates)
    elif not errors:errors.append('No question records found. Fill in the header-only template first.')
    return {'rows':rows,'errors':errors,'total':total}


def read_csv(path):
    path=Path(path)
    if not path.is_file():
        raise ValueError('Choose a regular local CSV file.')
    with path.open('rb') as source:
        data=source.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:
        raise ValueError('CSV file exceeds 2 MiB.')
    try:text=data.decode('utf-8-sig')
    except UnicodeError:
        raise ValueError('Save the CSV as UTF-8 (an optional BOM is supported).') from None
    return parse_csv(text)


def template_text():
    output=io.StringIO(newline='');csv.writer(output,lineterminator='\n').writerow(COLUMNS)
    return output.getvalue()
