"""
Task 4 – Text-based Arithmetic Analyzer
---------------------------------------
Create a text-based analyzer made of small helper functions.

Rules used by all functions:
- Words are pieces of text separated by whitespace (use .split()).
- A NUMBER is a word that is a whole integer, optionally with a leading
  minus sign, e.g. "7", "42", "-3".
  Punctuation at the end of a word is ignored, so "5," "10." "8!" count
  as 5, 10 and 8. Use word.rstrip(".,!?;:") to remove it.
  Decimals ("3.5") and mixed words ("abc123") are NOT numbers.
- You do not need the `re` module; .split(), .rstrip() and .isdigit()
  are enough.

Helper functions:
- count_characters(text) -> int    : characters that are not whitespace
- count_words(text)      -> int    : number of words
- extract_numbers(text)  -> list   : list of ints, in the order they appear
- analyze_text(text)     -> dict   : combines the helpers (see below)

analyze_text() returns a dict with exactly these keys:
    "characters" : int   (from count_characters)
    "words"      : int   (from count_words)
    "numbers"    : list  (from extract_numbers)
    "sum"        : int   (sum of the numbers, 0 if there are none)
    "average"    : float (average of the numbers, 0.0 if there are none,
                          NOT rounded)

In the main block: read a line of text, call analyze_text(), and print a
summary. Round the average to 2 decimals when printing.

Example run:
    Enter text: I have 3 apples and 5 pears
    Characters (no spaces): 21
    Words: 7
    Numbers: [3, 5]
    Sum: 8
    Average: 4.00

Examples (these are also used to check your work):
>>> count_characters("a b  c")
3
>>> count_words("I have 3 apples and 5 pears")
7
>>> extract_numbers("Scores: 10, -4 and 7! but not 3.5 or abc123")
[10, -4, 7]
>>> result = analyze_text("I have 3 apples and 5 pears")
>>> result["characters"], result["words"], result["numbers"]
(21, 7, [3, 5])
>>> result["sum"], result["average"]
(8, 4.0)
>>> analyze_text("no numbers here")["average"]
0.0
"""


def analyze_text(text: str) -> dict:
    """
    Analyze text to count characters, words, and basic arithmetic operators (+, -, *, /).

    >>> analyze_text("Add 5 + 3 and subtract 2.")
    {'chars': 25, 'words': 6, 'operators': 2}
    """
    chars = len(text)
    words = len(text.split())
    operators = sum(1 for char in text if char in "+-*/")
    return {"chars": chars, "words": words, "operators": operators}

if __name__ == "__main__":
    sample_text = input("Enter text to analyze: ")
    results = analyze_text(sample_text)
    print(f"Analysis Results -> Characters: {results['chars']}, Words: {results['words']}, Operators: {results['operators']}")
