import json
import random
import spacy
import streamlit as st
from tqdm import tqdm
from annotated_text import annotated_text

@st.cache(show_spinner=False, allow_output_mutation=True, suppress_st_warning=True)
def load_models():
    train_data = [ ]
    patterns = [
                {
                    "label": "EMAIL", "pattern": [ {"TEXT": {"REGEX": "^((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)$"}} ]
                },
                {
                    "label": "PHONE", "pattern": [ {"TEXT": {"REGEX": "^((9[1-36]\s*[0-9]\s*|2[12]\s*[0-9]\s*|2[35]\s*[1-689]\s*|24[1-59]\s*|26[1-35689]\s*|27[1-9]\s*|28[1-69]\s*|29[1256])([0-9]{6}|[0-9]{3}\s*[0-9]{3}|[0-9]{1}\s*[0-9]{5}|[0-9]{2}\s*[0-9]{4}|[0-9]{4}\s*[0-9]{2}|[0-9]{5}\s*[0-9]{1}|[0-9]{2}\s*[0-9]{2}\s*[0-9]{2}))$"}} ]
                }
    ]
    portuguese_model = spacy.load("pt_core_news_lg")
    portuguese_model.add_pipe("entity_ruler", config={ 'validate': True, 'overwrite_ents': True }).add_patterns(patterns)
    with open("./tests/training-data.json", "r") as f: train_data = json.load(f)
    ner = portuguese_model.get_pipe('ner')
    for _, annotations in train_data:
        for ent in annotations.get('entities'): ner.add_label(ent[2])
    other_pipes = [ pipe for pipe in portuguese_model.pipe_names if pipe != 'ner' ]
    with portuguese_model.disable_pipes(*other_pipes):
        optimizer = portuguese_model.create_optimizer()
        for itn in range(5):
            random.shuffle(train_data)
            losses = { }
            for text, annotations in tqdm(train_data): portuguese_model.update( [text], [annotations], drop=0.5,  sgd=optimizer, losses=losses )        
    models = { "pt": portuguese_model }
    return models

def read_text(filename="./tests/test1.txt"):
    f = open(filename, 'r')
    output = f.read()
    f.close()
    return output

def process_text(doc, selected_entities, anonymize=False):
    tokens = []
    for token in doc:
        if (token.ent_type_ in ["PERSON", "PER"]) & ("PER" in selected_entities):
            tokens.append((token.text, "Person", "#faa"))
        elif (token.ent_type_ in ["GPE", "LOC"]) & ("LOC" in selected_entities):
            tokens.append((token.text, "Location", "#fda"))
        elif (token.ent_type_ == "ORG") & ("ORG" in selected_entities):
            tokens.append((token.text, "Organization", "#afa"))
        elif (token.ent_type_ == "EMAIL") & ("EMAIL" in selected_entities):
            tokens.append((token.text, "Email", "#aaf"))
        elif (token.ent_type_ == "PHONE") & ("PHONE" in selected_entities):
            tokens.append((token.text, "Phone", "#faf"))
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

selected_language = st.sidebar.selectbox("Select a language", options=[ "pt" ])
selected_entities = st.sidebar.multiselect(
    "Select the entities you want to detect",
    options=["LOC", "PER", "ORG", "EMAIL", "PHONE"],
    default=["LOC", "PER", "ORG", "EMAIL", "PHONE"],
)
selected_model = models[selected_language]

text_input = st.text_area("Type a text to anonymize", value=read_text())

uploaded_file = st.file_uploader("or Upload a file", type=[ "txt" ])
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
