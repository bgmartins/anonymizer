
mkdir -p ~/.streamlit/

python -m spacy download fr_dep_news_trf
python -m spacy download en_core_web_trf
python -m spacy download pt_core_news_lg

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
