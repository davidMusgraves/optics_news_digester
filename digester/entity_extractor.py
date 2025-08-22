import spacy

nlp = spacy.load("en_core_web_trf")  # More accurate NER

# Entity types we'll track
TRACKED_ENTITY_LABELS = {"ORG", "PERSON", "GPE", "NORP", "FAC"}

def extract_entities(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ in TRACKED_ENTITY_LABELS:
            print(f"[NER] Found: '{ent.text}' ({ent.label_})")
            entities.append({
                "text": ent.text.strip(),
                "label": ent.label_
            })
    return entities
