from geonature.utils.env import db


class Author(db.Model):
    ___tablename__ = "author"
    __table_args__ = {"schema": "{{cookiecutter.db_schema_name}}"}
    id_author = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email_address = db.Column(db.String)
    posts = db.relationship("Post", back_populates="author")


class Post(db.Model):
    ___tablename__ = "post"
    __table_args__ = {"schema": "{{cookiecutter.db_schema_name}}"}

    id_post = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String)
    post_content = db.Column(db.String)
    id_author = db.Column(
        db.Integer,
        db.ForeignKey("{{cookiecutter.db_schema_name}}.author.id_author"),
        nullable=False,
    )
    author = db.relationship(Author, back_populates="posts")
