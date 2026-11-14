"""Validation for locally authored study content, independent of Tk."""
import unicodedata

DIFFICULTIES = ("Easy", "Medium", "Hard")


def topic_fields(name):
    name = " ".join(name.split())
    if not name or len(name) > 120:
        raise ValueError("Enter a topic name between 1 and 120 characters.")
    return name, unicodedata.normalize("NFKC", name).casefold()


def question_fields(prompt, options, correct_option, difficulty, explanation):
    prompt = prompt.strip()
    explanation = explanation.strip()
    if not prompt or len(prompt) > 2000:
        raise ValueError("Enter a question between 1 and 2,000 characters.")
    if not isinstance(options, (list, tuple)) or len(options) != 4:
        raise ValueError("Provide exactly four answer options.")
    options = tuple(" ".join(option.split()) for option in options)
    if any(not option or len(option) > 500 for option in options):
        raise ValueError("Each answer must contain 1 to 500 characters.")
    keys = {unicodedata.normalize("NFKC", option).casefold() for option in options}
    if len(keys) != 4:
        raise ValueError("The four answer options must be different.")
    if type(correct_option) is not int or correct_option not in range(4):
        raise ValueError("Select the correct answer: A, B, C or D.")
    if difficulty not in DIFFICULTIES:
        raise ValueError("Choose Easy, Medium or Hard difficulty.")
    if len(explanation) > 2000:
        raise ValueError("Keep the explanation within 2,000 characters.")
    return (prompt, *options, correct_option, difficulty, explanation)
