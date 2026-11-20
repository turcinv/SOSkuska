"""Bounded flashcard CSV validation; no Tk or database access."""
import csv
import io
from csv_import import MAX_BYTES, MAX_ROWS, ImportValidationError, safe_text, read_csv as read_bounded_csv
from repetition import card_fields

COLUMNS = ('front', 'back')


def canonical_row(record, fields):
    if type(record) is not int or record < 2:
        raise ValueError('Invalid CSV record number.')
    if not isinstance(fields, (list, tuple)) or len(fields) != 2:
        raise ValueError('Expected front and back.')
    return {'record': record, 'fields': list(card_fields(*(safe_text(v) for v in fields)))}


def validate_rows(rows):
    if not isinstance(rows, (list, tuple)) or not 1 <= len(rows) <= MAX_ROWS:
        raise ImportValidationError([f'Choose 1–{MAX_ROWS} flashcard records.'])
    normalized = []; errors = []; seen = {}
    for row in rows:
        try:
            current = canonical_row(row['record'], row['fields'])
        except (ValueError, TypeError, KeyError, UnicodeError) as exc:
            record = row.get('record', '?') if isinstance(row, dict) else '?'
            errors.append(f'CSV record {record}: {exc}')
            continue
        key = tuple(current['fields'])
        if key in seen:
            errors.append(f'CSV record {current["record"]}: Duplicate of record {seen[key]} (front and back).')
        else:
            seen[key] = current['record']
        normalized.append(current)
    return normalized, errors


def parse_csv(text):
    safe_text(text)
    if len(text.encode('utf-8')) > MAX_BYTES:
        raise ValueError('CSV file exceeds 2 MiB.')
    reader = csv.reader(io.StringIO(text, newline=''), strict=True)
    try:
        header = [v.strip().casefold() for v in next(reader)]
    except StopIteration:
        raise ValueError('CSV file is empty.') from None
    except csv.Error as exc:
        raise ValueError(f'Invalid CSV header: {exc}') from None
    if len(header) != 2 or set(header) != set(COLUMNS):
        raise ValueError('Use the comma-separated CSV template headers: front,back (each once).')
    rows = []; errors = []; total = 0
    try:
        for record, cells in enumerate(reader, 2):
            if not cells or not any(v.strip() for v in cells):
                continue
            total += 1
            if total > MAX_ROWS:
                errors.append(f'CSV exceeds {MAX_ROWS} nonblank flashcard records. Split the file.')
                break
            if len(cells) != 2:
                errors.append(f'CSV record {record}: Expected 2 cells, found {len(cells)}.')
                continue
            values = dict(zip(header, cells))
            try:
                rows.append(canonical_row(record, [values['front'], values['back']]))
            except (ValueError, UnicodeError) as exc:
                errors.append(f'CSV record {record}: {exc}')
    except csv.Error as exc:
        errors.append(f'Invalid CSV near physical line {reader.line_num}: {exc}')
    if rows:
        rows, duplicates = validate_rows(rows)
        errors.extend(duplicates)
    elif not errors:
        errors.append('No flashcard records found. Fill in the header-only template first.')
    return {'rows': rows, 'errors': errors, 'total': total}


def read_csv(path):
    return read_bounded_csv(path, parser=parse_csv)


def template_text():
    return 'front,back\n'
