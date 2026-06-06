def normalize_memory(text):

    text = text.strip()

    prefixes = [

        "remember that ",

        "remember ",

        "store that ",

        "store ",

        "save that ",

        "save "

    ]

    lower = text.lower()

    for prefix in prefixes:

        if lower.startswith(prefix):

            text = text[len(prefix):]

            break

    return text.strip().capitalize()

