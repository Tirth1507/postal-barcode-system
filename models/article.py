from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ExpectedArticle(db.Model):

    __tablename__ = "expected_articles"

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
        return f"<Article {self.article_number}>"