import streamlit as st
import requests
import pandas as pd
import time
import os
from datetime import datetime

host = os.environ["superlinked_host"]
port = os.environ["superlinked_port"]

# Define the URL and headers
url = f'http://{host}:{port}/api/v1/search/query'
headers = {
    'Accept': '*/*',
    'Content-Type': 'application/json'
}


# Function to get data from the API
def get_data(user_id):
    """
    Retrieves data based on a given user ID by sending a POST request to a specified
    URL, parses the response JSON, extracts relevant information into a pandas
    DataFrame, and returns it. If the request fails, it displays an error message
    and returns an empty DataFrame.

    Args:
        user_id (int | str): Used to construct a payload that contains information
            about the user for which data needs to be retrieved. It is required
            as part of the payload.

    Returns:
        pdDataFrame|pdDataFrame: A DataFrame object if the request to the server
        is successful and it returns an empty DataFrame otherwise, indicating that
        the request failed or no data was extracted.

    """
    print(f"[{datetime.now()}] Running query...")
    payload = {
        "user_id": user_id,
        "query_text": "",
        "description_weight": 1,
        "category_weight": 1,
        "name_weight": 1,
        "price_weight": 1,
        "review_count_weight": 1,
        "review_rating_weight": 1,
        "limit": 10
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        extracted_data = [result['obj'] for result in results]
        df = pd.DataFrame(extracted_data)
        return df
    else:
        st.error(f"Request failed with status code {response.status_code}: {response.text}")
        return pd.DataFrame()


# Streamlit UI
st.title("Real-time Recommendations Query with Streamlit and Superlinked")

# Dropdown for user selection
user_id = st.selectbox("Select User ID", ["user_1", "user_2"])

# Input fields for weights
col1, col2 = st.columns([1, 3])
with col1:
    st.write("Description Weight")
with col2:
    description_weight = st.number_input("", min_value=0.0, max_value=10.0, value=1.0, key="description_weight")

col1, col2 = st.columns([1, 3])
with col1:
    st.write("Category Weight")
with col2:
    category_weight = st.number_input("", min_value=0.0, max_value=10.0, value=1.0, key="category_weight")

col1, col2 = st.columns([1, 3])
with col1:
    st.write("Name Weight")
with col2:
    name_weight = st.number_input("", min_value=0.0, max_value=10.0, value=1.0, key="name_weight")

col1, col2 = st.columns([1, 3])
with col1:
    st.write("Price Weight")
with col2:
    price_weight = st.number_input("", min_value=0.0, max_value=10.0, value=1.0, key="price_weight")

col1, col2 = st.columns([1, 3])
with col1:
    st.write("Review Count Weight")
with col2:
    review_count_weight = st.number_input("", min_value=0.0, max_value=10.0, value=1.0, key="review_count_weight")

col1, col2 = st.columns([1, 3])
with col1:
    st.write("Review Rating Weight")
with col2:
    review_rating_weight = st.number_input("", min_value=0.0, max_value=10.0, value=1.0, key="review_rating_weight")

# Placeholder for the dataframe
data_placeholder = st.empty()

# Placeholder for countdown text
countdown_placeholder = st.empty()

# Function to get data and cache it
@st.cache_data
def get_cached_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight):
    """
    Retrieves and returns cached data for a given set of input parameters. It calls
    another function `get_data` with the same parameters, likely to fetch new data
    if it's not already cached or outdated.

    Args:
        user_id (any): Used as input to retrieve cached data from the user's
            profile. Its value determines which user's data will be retrieved.
        description_weight (float): Used to specify the relative importance or
            weight of product description when calculating a weighted average score.
        category_weight (int): Used to determine the weightage given to category
            information when calculating similarity scores for filtering data based
            on user preferences.
        name_weight (float): Used as a weight for the name attribute when retrieving
            data using the `get_data` function. It specifies how important the
            name attribute is relative to other attributes in the calculation.
        price_weight (float): Used to weight the importance of the product's price
            when calculating its overall score. It represents the relative
            significance of price compared to other factors.
        review_count_weight (int): Used to determine the weight given to the number
            of reviews when calculating the weighted average score for a product.
        review_rating_weight (float): 7th in sequence among other weights, likely
            representing the weightage given to review ratings in a data retrieval
            process.

    Returns:
        Any: Cached result from a call to `get_data`. This caching allows for
        faster execution when the same inputs are provided again.

    """
    return get_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight)

# Function to get data from the API
def get_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight):
    """
    Runs a POST request to a specified URL with a payload containing various weights
    and returns a pandas DataFrame containing extracted data if the response is
    successful, otherwise it displays an error message and returns an empty DataFrame.

    Args:
        user_id (int): Likely used to filter or retrieve data based on a specific
            user's ID from an external database or API.
        description_weight (float): Used to specify the relative importance or
            relevance of the product description in the query. It is one of the
            factors considered when processing the user's request.
        category_weight (float): Part of the payload sent to the requests.post
            method. It represents the weightage given to category in the query.
        name_weight (float): Part of the payload being sent to the server as JSON.
            It represents the weight assigned to the name field in the query.
        price_weight (int): 6th in the list of parameters passed to the function.
            It represents the weight assigned to price when calculating a score
            for search results.
        review_count_weight (int): Part of the payload sent with the POST request
            to the specified URL. It represents the weight given to review count
            while evaluating query results.
        review_rating_weight (float): Used to determine the weight given to review
            ratings when calculating the overall score for a query result.

    Returns:
        pdDataFrame|pdDataFrame: Empty if the request fails otherwise, it contains
        extracted data from a response.

    """
    print(f"[{datetime.now()}] Running query...")
    payload = {
        "user_id": user_id,
        "query_text": "",
        "description_weight": description_weight,
        "category_weight": category_weight,
        "name_weight": name_weight,
        "price_weight": price_weight,
        "review_count_weight": review_count_weight,
        "review_rating_weight": review_rating_weight,
        "limit": 10
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        extracted_data = [result['obj'] for result in results]
        df = pd.DataFrame(extracted_data)
        return df
    else:
        st.error(f"Request failed with status code {response.status_code}: {response.text}")
        return pd.DataFrame()

# Main loop
while True:
    # Get the data
    df = get_cached_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight)

    # Display the dataframe
    data_placeholder.dataframe(df)

    # Countdown
    for i in range(10, 0, -1):
        countdown_placeholder.text(f"Refreshing in {i} seconds...")
        time.sleep(1)

    # Clear the countdown text
    countdown_placeholder.empty()

    # Clear the cache to fetch new data
    get_cached_data.clear()