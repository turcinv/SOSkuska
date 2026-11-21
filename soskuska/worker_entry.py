"""Bundled console helper; stdout is a file-backed JSON protocol, never a GUI."""
import argparse
from backup_worker import main as backup_main
from csv_import_worker import main as questions_main
from flashcard_csv_import_worker import main as flashcards_main


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('worker', choices=['backup', 'questions', 'flashcards'])
    args, remaining = parser.parse_known_args()
    {'backup': backup_main, 'questions': questions_main, 'flashcards': flashcards_main}[args.worker](remaining)


if __name__ == '__main__':
    main()
