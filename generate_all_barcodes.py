from app import app
from models.article import ExpectedArticle

import barcode
from barcode.writer import ImageWriter
import os

BARCODE_FOLDER = "barcodes"

if not os.path.exists(BARCODE_FOLDER):
    os.makedirs(BARCODE_FOLDER)

with app.app_context():

    articles = ExpectedArticle.query.all()

    count = 0

    for article in articles:

        article_number = article.article_number

        code128 = barcode.get(
            "code128",
            article_number,
            writer=ImageWriter()
        )

        filepath = os.path.join(
            BARCODE_FOLDER,
            article_number
        )

        code128.save(filepath)

        count += 1

        print("Generated:", article_number)

print(f"\nTotal Barcodes Generated: {count}")