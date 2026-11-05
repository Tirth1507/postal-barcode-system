from models.article import db

class ScannedArticle(db.Model):

    __tablename__ = "scanned_articles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    article_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    def __repr__(self):
        return f"<Scanned {self.article_number}>"