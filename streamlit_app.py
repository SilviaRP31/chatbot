import streamlit as st
import pandas as pd
import re

# Load the CSV file into a Pandas DataFrame
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Handle input to classify and determine processing method
def handle_input(input_string):
    # Check for date and/or amount
    month_match = re.search(r"\b(january|february|march|april|may|june|july|august|september|october|november|december|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|año|year)\b", input_string.lower())
    number_match = re.search(r'\d+', input_string)

    # Check for Tag and City mentions in the input
    tag_keywords = ["tag1", "tag2", "tag3"]  # List of possible tag columns
    city_keywords = ["city"]  # List for city
    merchant_keywords = ["merchant"]  # List for merchants

    # Check if any tag or city keywords are in the input
    tags_detected = any(tag in input_string.lower() for tag in tag_keywords)
    city_detected = any(city in input_string.lower() for city in city_keywords)
    merchant_detected = any(merchant in input_string.lower() for merchant in merchant_keywords)

    # If multiple columns or patterns detected, classify as NL2Q
    if (tags_detected and merchant_detected and city_detected) or (tags_detected and city_detected) or (tags_detected and merchant_detected) or (city_detected and merchant_detected) or number_match or month_match:
        return "NL2Q"
    else:
        return "StringMatching"

# Filter input to match known categories
def filter_input(input_string, merchants, tags, cities):
    words = input_string.split()
    filtered_words = [
        word for word in words
        if word in merchants or word in tags or word in cities
    ]
    return filtered_words

# Generate query and run it on the DataFrame
def run_query(data, user_input, filtered_words, method):
    if method == "StringMatching" and filtered_words:
        # Create filtering conditions
        conditions = []
        for word in filtered_words:
            condition = (
                f"(Merchant.str.contains('{word}', case=False, na=False) | "
                f"Tag1.str.contains('{word}', case=False, na=False) | "
                f"Tag2.str.contains('{word}', case=False, na=False) | "
                f"Tag3.str.contains('{word}', case=False, na=False) | "
                f"City.str.contains('{word}', case=False, na=False))"
            )
            conditions.append(condition)

        # Combine conditions
        query = " & ".join(conditions)

        # Filter DataFrame based on the query
        filtered_data = data.query(query, engine='python')
        return filtered_data
    elif method == "NL2Q":
        st.warning("Complex NL2Q queries are not yet supported for CSV.")
        return None
    else:
        st.warning("No matching records found.")
        return None

# Main Streamlit app
def main():
    st.title("Transaction Query App")
    st.write("Enter a query about transactions and get results.")

    # File path to the transaction.csv
    file_path = "transaction.csv"  # Ensure this file is in the same directory

    # Load data
    data = load_data(file_path)

    # Sample merchants, tags, and cities for filtering
    merchants = data['Merchant'].unique().tolist()
    tags = data[['Tag1', 'Tag2', 'Tag3']].stack().unique().tolist()
    cities = data['City'].unique().tolist()

    # User input
    user_input = st.text_input("Enter your query:", "")

    if st.button("Process Query"):
        if user_input.strip():
            # Determine processing method
            processing_method = handle_input(user_input)
            st.write(f"Processing method: {processing_method}")

            # Filter words based on known merchants, tags, and cities
            filtered_words = filter_input(user_input, merchants, tags, cities)
            st.write(f"Filtered words: {filtered_words}")

            # Run the query on the data
            result = run_query(data, user_input, filtered_words, processing_method)

            if result is not None and not result.empty:
                st.write("Query Results:")
                st.dataframe(result)
            else:
                st.write("No results found. Try refining your query.")
        else:
            st.write("Please enter a query.")

# Run the app
if __name__ == "__main__":
    main()
