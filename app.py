import streamlit as st
import spacy
from annotated_text import annotated_text

@st.cache(show_spinner=False, allow_output_mutation=True, suppress_st_warning=True)
def load_models():
    # patterns = [
    #            {
    #                "label": "EMAIL", "pattern": [ {"TEXT": {"REGEX": "\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b"}} ]
    #            }
    #]
    french_model = spacy.load("fr_dep_news_trf")
    english_model = spacy.load("en_core_web_trf")
    portuguese_model = spacy.load("pt_core_news_lg")
    #french_model.add_pipe("entity_ruler").add_patterns(patterns)
    #english_model.add_pipe("entity_ruler").add_patterns(patterns)
    #portuguese_model.add_pipe("entity_ruler").add_patterns(patterns)
    models = {"pt": portuguese_model, "en": english_model, "fr": french_model }
    return models

def process_text(doc, selected_entities, anonymize=False):
    tokens = []
    for token in doc:
        if (token.ent_type_ == "PERSON") & ("PER" in selected_entities):
            tokens.append((token.text, "Person", "#faa"))
        elif (token.ent_type_ in ["GPE", "LOC"]) & ("LOC" in selected_entities):
            tokens.append((token.text, "Location", "#fda"))
        elif (token.ent_type_ == "ORG") & ("ORG" in selected_entities):
            tokens.append((token.text, "Organization", "#afa"))
        elif (token.ent_type_ == "EMAIL") & ("EMAIL" in selected_entities):
            tokens.append((token.text, "Email", "#aaf"))
        else:
            tokens.append(" " + token.text + " ")
    if anonymize:
        anonmized_tokens = []
        for token in tokens:
            if type(token) == tuple:
                anonmized_tokens.append(("X" * len(token[0]), token[1], token[2]))
            else:
                anonmized_tokens.append(token)
        return anonmized_tokens
    return tokens

models = load_models()

selected_language = st.sidebar.selectbox("Select a language", options=["pt", "en", "fr"])
selected_entities = st.sidebar.multiselect(
    "Select the entities you want to detect",
    options=["LOC", "PER", "ORG", "EMAIL"],
    default=["LOC", "PER", "ORG", "EMAIL"],
)
selected_model = models[selected_language]

text_input = st.text_area("Type a text to anonymize")

uploaded_file = st.file_uploader("or Upload a file", type=["doc", "docx", "pdf", "txt"])
if uploaded_file is not None:
    text_input = uploaded_file.getvalue()
    text_input = text_input.decode("utf-8")

anonymize = st.checkbox("Anonymize")
doc = selected_model(text_input)
tokens = process_text(doc, selected_entities)

annotated_text(*tokens)

if anonymize:
    st.markdown("**Anonymized text**")
    st.markdown("---")
    anonymized_tokens = process_text(doc, selected_entities, anonymize=anonymize)
    annotated_text(*anonymized_tokens)
