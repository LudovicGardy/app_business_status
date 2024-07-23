mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
[theme]\n\
base = \"dark\"\n\
layout=\"centered\"\n\
initial_sidebar_state=\"expanded\"\n\
page_title=\"Business Status\"\n\
sidebar_title=\"Business Status\"\n\
" > ~/.streamlit/config.toml