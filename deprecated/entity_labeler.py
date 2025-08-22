import streamlit as st
from db.article_model import get_session, ArticleEntity, Article
from sqlalchemy.orm import joinedload
import pandas as pd
import os

# Load session and data
session = get_session()

st.set_page_config(page_title="Entity Label Correction", layout="wide")
st.title("🧠 Named Entity Label Correction Tool")


# Fetch entity-article pairs
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

# Create editable table
entity_data = []
for entity, article in pairs:
    entity_data.append({
        "Entity ID": entity.id,
        "Entity Name": entity.name,
        "Predicted Label": entity.type,
        "Corrected Label": entity.type,
        "Title": article.title,
        "Source": article.source,
        "Published": article.published
    })

df = pd.DataFrame(entity_data)

# Filter controls
st.sidebar.title("Filters")
filter_types = st.sidebar.multiselect(
    "Entity Type Filter", df["Predicted Label"].unique(), default=df["Predicted Label"].unique()
)
df = df[df["Predicted Label"].isin(filter_types)]

# Editable table
edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "Corrected Label": st.column_config.SelectboxColumn(
            options=["ORG", "PERSON", "GPE", "FAC", "NORP", "MISC", "IGNORE"]
        )
    },
    disabled=["Entity ID", "Entity Name", "Predicted Label", "Title", "Source", "Published"]
)

# Save corrected labels
if st.button("💾 Save Corrections to CSV"):
    output_path = "data/label_corrections.csv"
    edited_df.to_csv(output_path, index=False)
    st.success(f"Saved to {output_path}")
