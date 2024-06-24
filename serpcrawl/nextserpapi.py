import streamlit as st
from serpapi.search import GoogleSearch
from urllib.parse import urlparse
import random
import requests

# streamlit run nextserpapi.py     commans

# Function to validate the SerpAPI key
def validate_api_key(api_key):
    params = {
        "engine": "google",
        "q": "test",
        "api_key": api_key
    }
    response = requests.get("https://serpapi.com/search", params=params)
    return response.status_code == 200

# Function to search for keywords and compare results
def compare_keywords(keyword1, keyword2, api_key):
    # Define search parameters
    params = {
        "engine": "google",
        "q": keyword1,
        "gl": "in",  # Location set to India
        "api_key": api_key  # Use the provided API key
    }

    # Perform search for the first keyword
    search = GoogleSearch(params)
    results1 = search.get_dict()

    # Perform search for the second keyword
    params["q"] = keyword2
    search = GoogleSearch(params)
    results2 = search.get_dict()

    # Extract URLs from search results
    urls1 = [result.get("link") for result in results1.get("organic_results", [])]
    urls2 = [result.get("link") for result in results2.get("organic_results", [])]

    # Define color codes
    colors = ["#FFAAAA", "#AEBCFF", "#E2FFBD", "#F3C8FF", "#FFBD59", "#D9D9D9", "#FF904C", "#FF6D6D", "#68E9FF", "#4EFF03"]

    # Find common URLs and domains
    exact_matches = set(urls1) & set(urls2)
    common_domains = {}
    for url1 in urls1:
        domain1 = urlparse(url1).netloc
        for url2 in urls2:
            domain2 = urlparse(url2).netloc
            if domain1 == domain2 and url1 != url2:
                if domain1 not in common_domains:
                    common_domains[domain1] = set()
                common_domains[domain1].add(url1)
                common_domains[domain1].add(url2)

    # Assign colors to exact matches and common domains
    color_map = {}
    domain_color_map = {}
    for url in exact_matches:
        color = colors.pop(0) if colors else f'#{random.randint(0, 0xFFFFFF):06x}'
        color_map[url] = color

    for domain in common_domains:
        color = colors.pop(0) if colors else f'#{random.randint(0, 0xFFFFFF):06x}'
        for url in common_domains[domain]:
            domain_color_map[url] = color

    # Highlight URLs
    highlighted_urls1 = []
    highlighted_urls2 = []
    for url1 in urls1:
        if url1 in exact_matches:
            highlighted_urls1.append(f'<span style="background-color: {color_map[url1]};">{url1}</span>')
        elif url1 in domain_color_map:
            highlighted_urls1.append(f'<span style="background-color: {domain_color_map[url1]}; border: 2px solid darkred;">{url1}</span>')
        else:
            highlighted_urls1.append(url1)

    for url2 in urls2:
        if url2 in exact_matches:
            highlighted_urls2.append(f'<span style="background-color: {color_map[url2]};">{url2}</span>')
        elif url2 in domain_color_map:
            highlighted_urls2.append(f'<span style="background-color: {domain_color_map[url2]}; border: 2px solid darkred;">{url2}</span>')
        else:
            highlighted_urls2.append(url2)

    # Calculate similarity percentage
    similarity = round(100 * len(exact_matches) / len(urls1), 2) if urls1 else 0

    # Create a table to display URLs with enhanced UI
    table = f'''
    <style>
        .serp-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .serp-table th, .serp-table td {{
            border: 1px solid #ddd;
            padding: 8px;
        }}
        .serp-table th {{
            background-color: #f2f2f2;
            text-align: center;
        }}
        .serp-similarity {{
            font-weight: bold;
            font-size: 20px;
            margin: 20px 0;
            padding: 10px;
            background-color: #68E9FF;
            border: 2px solid #4EFF03;
            display: inline-block;
        }}
        .matched-line {{
            text-align: center;
            font-weight: bold;
        }}
    </style>
    <div class="serp-similarity">SERP Similarity: <span>{similarity}%</span></div>
    <table class="serp-table">
        <tr><th>{keyword1}</th><th>{keyword2}</th></tr>
    '''
    for url1, url2 in zip(highlighted_urls1, highlighted_urls2):
        table += f'<tr><td>{url1}</td><td>{url2}</td></tr>'
        if url1 in exact_matches and url2 in exact_matches:
            table += f'<tr><td colspan="2" style="text-align:center;"><span style="color:{color_map[url1]};">&#x2194; Matched URL</span></td></tr>'
    table += '</table>'

    return table

# Streamlit app
st.title("SERP Keyword Comparison")

with st.expander("Instructions"):
    st.subheader("Sample Results:")
    st.image("serpcrawl/Screenshot 2024-06-24 111449 (3).png")
# Get API key from the user
api_key = st.text_input("Enter your SerpAPI key:", type="password")

# Provide a link to create a SerpAPI key
st.markdown("Don't have a SerpAPI key? [Create one here](https://serpapi.com/users/sign_up)")

# Get keywords from the user
keyword1 = st.text_input("Enter the first keyword:")
keyword2 = st.text_input("Enter the second keyword:")

if st.button("Compare"):
    if api_key and keyword1 and keyword2:
        if validate_api_key(api_key):
            url_table = compare_keywords(keyword1, keyword2, api_key)
            st.markdown(url_table, unsafe_allow_html=True)
        else:
            st.warning("SerpAPI key is missing or invalid.")
    else:
        st.warning("Please enter the API key and both keywords to compare.")
