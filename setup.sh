mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
[theme]\n\
base = \"dark\"\n\
layout="centered"
initial_sidebar_state="expanded"
page_title="Business Status"
sidebar_title="Business Status"
" > ~/.streamlit/config.toml