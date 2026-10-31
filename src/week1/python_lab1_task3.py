"""
Task 3 – Function with Combined Logic
-------------------------------------
Write a function `analyze_sentence(text)` that returns a tuple of three values,
in this order:
1. total character count of the text exactly as given, spaces included (len)
2. word count, where words are separated by whitespace (.split())
3. True if "python" appears anywhere in the text, ignoring case, else False
   (a simple substring check: "Pythonic" and "PYTHON!" both count)

Return type: (int, int, bool)

In the main block: read a sentence, call the function, and print a summary.

Example run:
    Enter a sentence: I love Python
    Characters: 13
    Words: 3
    Contains 'Python': True

Examples (these are also used to check your work):
>>> analyze_sentence("I love Python")
(13, 3, True)
>>> analyze_sentence("  Hello   world  ")
(17, 2, False)
>>> analyze_sentence("PYTHONIC code!")
(14, 2, True)
>>> analyze_sentence("")
(0, 0, False)
"""


def analyze_sentence(sentence: str, keyword: str) -> tuple:
    """
    Analyze a sentence: return word count and whether the keyword is present (case-insensitive).

    >>> analyze_sentence("Python is a great programming language.", "python")
    (6, True)
    >>> analyze_sentence("Learning C and Python at RTU.", "Java")
    (6, False)
    """
    words = sentence.split()
    word_count = len(words)
    has_keyword = keyword.lower() in sentence.lower()
    return (word_count, has_keyword)

if __name__ == "__main__":
    sent = input("Enter a sentence: ")
    kw = input("Enter a keyword to check: ")
    count, found = analyze_sentence(sent, kw)
    print(f"Word count: {count} | Keyword present: {found}")
