import easyocr
import re

reader = easyocr.Reader(['en'])

def fix_article(article):

    article = article.upper().strip()

    # Fix ending
    article = article.replace("1N", "IN")

    if len(article) >= 13:

        chars = list(article)

        # Position 1-2 must be letters
        chars[0] = chars[0].replace("0", "O")
        chars[1] = chars[1].replace("0", "O")

        # Position 3-11 must be digits
        for i in range(2, 11):

            if chars[i] == "O":
                chars[i] = "0"

            if chars[i] == "I":
                chars[i] = "1"

        article = "".join(chars)

    return article


def extract_articles(image_path):

    results = reader.readtext(
        image_path,
        detail=1,
        paragraph=False
    )

    results = sorted(
        results,
        key=lambda x: x[0][0][1]
    )

    articles = []

    print("\n===== RAW OCR OUTPUT =====\n")

    for result in results:

        text = result[1].upper().strip()

        print("RAW :", text)

        text = fix_article(text)

        print("FIX :", text)

        pattern = r'[A-Z]{2}[0-9]{9}IN'

        matches = re.findall(pattern, text)

        for match in matches:

            if match not in articles:
                articles.append(match)

    print("\n===== FINAL ARTICLES =====\n")

    for article in articles:
        print(article)

    print("\nTotal Articles Found:", len(articles))

    return articles