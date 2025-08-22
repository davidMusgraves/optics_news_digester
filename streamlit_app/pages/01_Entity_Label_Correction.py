import streamlit as st
from db.article_model import get_session, ArticleEntity, Article
from sqlalchemy.orm import joinedload
import pandas as pd
import os
import re

# Load DB session
session = get_session()

st.set_page_config(page_title="Entity Label Correction", layout="wide")
st.title("🧠 Named Entity Label Correction Tool")


# ----------- Utility to highlight NE in context from text ----------- #
def extract_context(entity_text, full_text, window=20):
    # Escape for regex
    pattern = re.escape(entity_text)
    match = re.search(pattern, full_text, re.IGNORECASE)
    if not match:
        return "Not found in text"

    start = max(match.start() - 200, 0)
    end = min(match.end() + 200, len(full_text))
    context = full_text[start:end]

    return context.replace(entity_text, f"**🟡{entity_text}**")


# ----------- Load entities + articles ----------- #
@st.cache_data
def load_entities():
    results = (
        session.query(ArticleEntity, Article)
        .join(Article)
        .options(joinedload(ArticleEntity.article))
        .all()
    )
    return results


pairs = load_entities()

# ----------- Build DataFrame ----------- #
entity_data = []
for entity, article in pairs:
    full_text = f"{article.title} {article.summary}"
    entity_data.append({
        "Entity ID": entity.id,
        "Entity Name": entity.name,
        "Predicted Label": entity.type,
        "Corrected Label": entity.type,
        "Entity Context": extract_context(entity.name, full_text),
        "Title": article.title,
        "Source": article.source,
        "Link": article.link,
        "Published": article.published
    })

df = pd.DataFrame(entity_data)

# ----------- Sidebar filters ----------- #
st.sidebar.title("Filters")
filter_types = st.sidebar.multiselect(
    "Entity Type Filter",
    df["Predicted Label"].unique(),
    default=df["Predicted Label"].unique()
)
df = df[df["Predicted Label"].isin(filter_types)]

# ----------- Editable Data Table ----------- #
edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "Corrected Label": st.column_config.SelectboxColumn(
            options=["ORG", "PERSON", "GPE", "FAC", "NORP", "MISC", "IGNORE"]
        ),
        "Link": st.column_config.LinkColumn()
    },
    disabled=[
        "Entity ID", "Entity Name", "Predicted Label",
        "Entity Context", "Title", "Source", "Link", "Published"
    ]
)

# ----------- Save to CSV ----------- #
if st.button("💾 Save Corrections to CSV"):
    output_path = "data/label_corrections.csv"
    edited_df.to_csv(output_path, index=False)
    st.success(f"Saved to {output_path}")
