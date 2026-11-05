from flask import Flask, render_template, request
from services.ocr_service import extract_articles
from models.article import db, ExpectedArticle
from flask import Flask, render_template, request, redirect
from models.scanned_article import ScannedArticle
from barcode import Code128
from barcode.writer import ImageWriter
from models.article import ExpectedArticle
from models.scanned_article import ScannedArticle
import shutil
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# MySQL Connection
app.config["SQLALCHEMY_DATABASE_URI"] = \
    "mysql+pymysql://root:Tirth%401507@localhost/spbvs"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return "No File Selected"

    file = request.files["file"]

    if file.filename == "":
        return "Please Select File"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    articles = extract_articles(filepath)

    # Save Articles to Database
    for article in articles:

        existing = ExpectedArticle.query.filter_by(
            article_number=article
        ).first()

        if not existing:

            new_article = ExpectedArticle(
                article_number=article
            )

            db.session.add(new_article)

    db.session.commit()

    return render_template(
        "result.html",
        articles=articles
    )


@app.route("/articles")
def articles():

    all_articles = ExpectedArticle.query.order_by(
        ExpectedArticle.id
    ).all()

    return render_template(
        "articles.html",
        articles=all_articles
    )

@app.route("/scan")
def scan():

    scanned_count = ScannedArticle.query.count()

    return render_template(
        "scan.html",
        scanned_count=scanned_count
    )

@app.route("/add_scan", methods=["POST"])
def add_scan():

    article_number = request.form["article_number"].strip().upper()

    existing = ScannedArticle.query.filter_by(
        article_number=article_number
    ).first()

    if not existing:

        scan = ScannedArticle(
            article_number=article_number
        )

        db.session.add(scan)
        db.session.commit()

    return redirect("/scan")

@app.route("/verify")
def verify():

    expected = {
        article.article_number
        for article in ExpectedArticle.query.all()
    }

    scanned = {
        article.article_number
        for article in ScannedArticle.query.all()
    }

    received = expected.intersection(scanned)

    missing = expected - scanned

    expected_count = len(expected)

    scanned_count = len(received)

    completion = 0

    if expected_count > 0:
        completion = round(
            (scanned_count / expected_count) * 100,
            2
        )

    return render_template(
        "verify.html",
        expected_count=expected_count,
        scanned_count=scanned_count,
        missing_count=len(missing),
        completion=completion,
        received=sorted(list(received)),
        missing=sorted(list(missing))
    )

@app.route("/reset")
def reset():

    ScannedArticle.query.delete()

    db.session.commit()

    return redirect("/verify")

@app.route("/bulk-scan")
def bulk_scan():
    return render_template("bulk_scan.html")

@app.route("/bulk-add", methods=["POST"])
def bulk_add():

    data = request.form["articles"]

    article_list = data.splitlines()

    added_count = 0

    for article in article_list:

        article = article.strip().upper()

        if article == "":
            continue

        existing = ScannedArticle.query.filter_by(
            article_number=article
        ).first()

        if not existing:

            scan = ScannedArticle(
                article_number=article
            )

            db.session.add(scan)

            added_count += 1

    db.session.commit()

    return f"{added_count} Articles Added Successfully <br><br> <a href='/verify'>View Verification</a>"

@app.route("/barcodes")
def show_barcodes():

    barcode_folder = os.path.join(
        "static",
        "barcodes"
    )

    print("Folder:", barcode_folder)

    files = os.listdir(barcode_folder)

    print("Files Found:", files)

    files.sort()

    return render_template(
        "barcodes.html",
        files=files
    )

@app.route("/delete-barcodes")
def delete_barcodes():

    barcode_folder = os.path.join(
        "static",
        "barcodes"
    )

    files = os.listdir(barcode_folder)

    for file in files:

        filepath = os.path.join(
            barcode_folder,
            file
        )

        os.remove(filepath)

    return redirect("/barcodes")

@app.route("/generate-barcodes")
def generate_barcodes():

    articles = ExpectedArticle.query.all()

    barcode_folder = os.path.join(
        "static",
        "barcodes"
    )

    os.makedirs(
        barcode_folder,
        exist_ok=True
    )

    count = 0

    for article in articles:

        article_number = article.article_number

        code128 = Code128(
            article_number,
            writer=ImageWriter()
        )

        filepath = os.path.join(
            barcode_folder,
            article_number
        )

        code128.save(filepath)

        count += 1

    return f"""
    <h2>✅ {count} Barcodes Generated Successfully</h2>
    <a href='/barcodes'>View Barcodes</a>
    """

@app.route("/reset-system")
def reset_system():

    # Delete Expected Articles
    ExpectedArticle.query.delete()

    # Delete Scanned Articles
    ScannedArticle.query.delete()

    db.session.commit()

    # Delete Barcodes
    barcode_folder = "static/barcodes"

    if os.path.exists(barcode_folder):

        for file in os.listdir(barcode_folder):

            filepath = os.path.join(
                barcode_folder,
                file
            )

            os.remove(filepath)

    # Delete Uploaded Images
    upload_folder = "uploads"

    if os.path.exists(upload_folder):

        for file in os.listdir(upload_folder):

            filepath = os.path.join(
                upload_folder,
                file
            )

            os.remove(filepath)

    return """
    <h2>✅ System Reset Successfully</h2>
    <a href='/'>Go Home</a>
    """

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )