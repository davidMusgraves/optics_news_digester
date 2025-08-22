from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    link = Column(String, unique=True, index=True)
    summary = Column(Text)
    published = Column(String)
    source = Column(String)
    tags = Column(String)  # store as comma-separated for now

    # One-to-many relationship: an article has many named entities
    entities = relationship("ArticleEntity", back_populates="article", cascade="all, delete-orphan")


class ArticleEntity(Base):
    __tablename__ = "article_entities"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    name = Column(String)
    type = Column(String)  # e.g., ORG, PERSON, GPE, etc.

    article = relationship("Article", back_populates="entities")


def get_session(db_path="sqlite:///data/articles.db"):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
