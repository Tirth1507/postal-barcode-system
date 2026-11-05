import barcode
from barcode.writer import ImageWriter

article_number = "UC538724753IN"

code128 = barcode.get(
    'code128',
    article_number,
    writer=ImageWriter()
)

filename = code128.save(article_number)

print("Barcode Saved:", filename)