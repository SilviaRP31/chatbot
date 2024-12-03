import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load transaction data (CSV file containing transactions)
@st.cache
def load_transaction_data():
    data = pd.read_csv('transactions.csv')  # Make sure to replace this with your actual file path
    return data

# Function to preprocess and vectorize transaction data
def process_transaction_data(data):
    # Convert all column names to lowercase and strip any extra spaces
    data.columns = [col.strip().lower() for col in data.columns]
    
    # Check if all required columns exist
    required_columns = ['merchant', 'tag1', 'tag2', 'tag3', 'city', 'amount', 'date']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        raise ValueError(f"Missing columns in the dataset: {', '.join(missing_columns)}")

    # Convert all relevant columns to lowercase for uniformity
    data = data.applymap(lambda s: s.lower() if isinstance(s, str) else s)
    
    # Combine all relevant columns (Merchant, Tags, Amount, Date, City) into a single text column
    data['combined_text'] = data['merchant'] + ' ' + data['tag1'].fillna('') + ' ' + data['tag2'].fillna('') + ' ' + data['tag3'].fillna('') + ' ' + data['city'].fillna('')
    data['combined_text'] += ' ' + data['amount'].astype(str) + ' ' + data['date'].astype(str)
    
    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(data['combined_text'])
    return data, vectorizer, tfidf_matrix

# Streamlit UI design

st.title('Global Transaction Search')
st.subheader('Search transactions based on various criteria')

# User input for global search
search_input = st.text_input('Enter search query (merchant, amount, tags, city, etc.):')

if st.button('Search Transactions'):
    if search_input:
        # Load and process the transaction data
        data = load_transaction_data()
        try:
            df, vectorizer, tfidf_matrix = process_transaction_data(data)
            
            # Transform the user input (query) using the same vectorizer
            query_vector = vectorizer.transform([search_input.lower()])
            
            # Calculate cosine similarity between user input and the transaction data
            similarity_scores = cosine_similarity(query_vector, tfidf_matrix)
            
            # Filter and sort results based on cosine similarity (greater than 0)
            filtered_scores = [(index, score) for index, score in enumerate(similarity_scores[0]) if score > 0]
            top_matches = sorted(filtered_scores, key=lambda x: x[1], reverse=True)[:5]  # Top 5 matches
            
            # Display the top matching transactions
            if top_matches:
                st.write(f"Top {len(top_matches)} matching transactions:")
                for index, score in top_matches:
                    st.write(f"Transaction ID: {df.iloc[index]['id']} - Similarity: {score:.2f} - Merchant: {df.iloc[index]['merchant']} - Amount: {df.iloc[index]['amount']} - Tags: {df.iloc[index]['tag1']} {df.iloc[index]['tag2']} {df.iloc[index]['tag3']} - City: {df.iloc[index]['city']}")
            else:
                st.write("No matching transactions found.")
        except ValueError as e:
            st.write(f"Error: {e}")
    else:
        st.write("Please enter a search query.")
