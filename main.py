import subprocess
from digester.rss_fetcher import fetch_articles
from digester.categorizer import categorize_article
from digester.entity_extractor import extract_entities
from db.article_model import get_session, Article, ArticleEntity
from sqlalchemy.exc import IntegrityError


def clear_articles_and_entities(session):
    print("[Reset] Deleting all articles and entities...")
    session.query(ArticleEntity).delete()
    session.query(Article).delete()
    session.commit()
    print("[Reset] Cleared Article and ArticleEntity tables.")


def fetch_and_label_articles():
    print("[Digester] Fetching and categorizing articles...")
    session = get_session()

    raw_articles = fetch_articles()
    new_articles = []

    for article in raw_articles:
        # Categorize and store
        article["tags"] = categorize_article(article)
        article_record = Article(
            title=article["title"],
            link=article["link"],
            summary=article["summary"],
            published=article["published"],
            source=article["source"],
            tags=",".join(article["tags"]),
        )

        # Named entity extraction
        full_text = f"{article['title']} {article['summary']}"
        entities = extract_entities(full_text)
        print(f"  → Extracted {len(entities)} entities from: {article['title'][:60]}")
        for ent in entities:
            article_record.entities.append(ArticleEntity(
                name=ent["text"],
                type=ent["label"]
            ))

        new_articles.append(article_record)

    print(f"[Deduplication] {len(new_articles)} new articles (out of {len(raw_articles)})")

    inserted_count = 0
    for article in new_articles:
        session.add(article)
        try:
            session.commit()
            inserted_count += 1
        except IntegrityError:
            session.rollback()
            print(f"[Duplicate] Skipped: {article.link}")

    print(f"[Database] Inserted {inserted_count} new articles into the database.")


def launch_streamlit_labeler():
    print("[Streamlit] Launching Entity Label Correction UI...")
    subprocess.run(["streamlit", "run", "streamlit_app/pages/01_Entity_Label_Correction.py"])


if __name__ == "__main__":
    session = get_session()
    clear_articles_and_entities(session)
    fetch_and_label_articles()
    launch_streamlit_labeler()
