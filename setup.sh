
mkdir -p ~/.streamlit/

python -m spacy download en_core_web_sm-2.2.0
python -m spacy download en_core_web_sm-2.2.0
python -m spacy download en_core_web_sm-2.2.0

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
