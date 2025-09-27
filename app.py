import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import string

# Page configuration
st.set_page_config(
    page_title="COVID-19 Research Papers Analysis",
    page_icon="🦠",
    layout="wide"
)

# Title and description
st.title("COVID-19 Research Papers Analysis Dashboard")
st.markdown("""
This dashboard analyzes research papers related to COVID-19, showing publication trends,
top journals, and common research topics. The data comes from a comprehensive collection
of scientific papers about COVID-19 and related coronaviruses.
""")

# Load and process data
@st.cache_data
def load_data():
    df = pd.read_csv('metadata.csv', low_memory=False)
    df_cleaned = df.dropna(subset=['title', 'publish_time', 'journal'])
    df_cleaned['publish_time'] = pd.to_datetime(df_cleaned['publish_time'], errors='coerce')
    df_cleaned['publication_year'] = df_cleaned['publish_time'].dt.year
    return df_cleaned

# Load data with a loading spinner
with st.spinner('Loading data...'):
    df_cleaned = load_data()

# Show sample of the data
st.subheader("Sample of Research Papers")
num_samples = st.slider("Number of samples to display", 5, 50, 10)
st.dataframe(df_cleaned[['title', 'journal', 'publish_time', 'authors']].head(num_samples))

# Sidebar filters
st.sidebar.header("Filters")
selected_years = st.sidebar.slider(
    "Select Year Range",
    int(df_cleaned['publication_year'].min()),
    int(df_cleaned['publication_year'].max()),
    (2019, 2023)
)

# Filter data based on year selection
filtered_df = df_cleaned[
    (df_cleaned['publication_year'] >= selected_years[0]) &
    (df_cleaned['publication_year'] <= selected_years[1])
]

# Create two columns for visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("Publications Over Time")
    papers_by_year = filtered_df['publication_year'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    papers_by_year.plot(kind='line', marker='o')
    plt.title('Number of Publications by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Papers')
    plt.grid(True)
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("Top Publishing Journals")
    num_journals = st.slider("Number of top journals to display", 5, 20, 10)
    top_journals = filtered_df['journal'].value_counts().head(num_journals)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top_journals.values, y=top_journals.index)
    plt.title(f'Top {num_journals} Publishing Journals')
    plt.xlabel('Number of Papers')
    st.pyplot(fig)
    plt.close()

# Word Cloud
st.subheader("Word Cloud of Paper Titles")
show_wordcloud = st.checkbox("Show Word Cloud", True)

if show_wordcloud:
    # Prepare text for word cloud
    all_titles = ' '.join(filtered_df['title'].dropna().str.lower())
    all_titles = all_titles.translate(str.maketrans('', '', string.punctuation))
    
    # Create and display word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_titles)
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(fig)
    plt.close()

# Show statistics
st.subheader("Dataset Statistics")
col3, col4 = st.columns(2)

with col3:
    st.metric("Total Papers", len(filtered_df))
    st.metric("Number of Journals", filtered_df['journal'].nunique())

with col4:
    st.metric("Papers with Abstracts", 
              filtered_df['abstract'].notna().sum(),
              f"{(filtered_df['abstract'].notna().sum() / len(filtered_df)) * 100:.1f}%")
    st.metric("Unique Authors", 
              len(set([author for authors in filtered_df['authors'].dropna() for author in authors.split(';')])))