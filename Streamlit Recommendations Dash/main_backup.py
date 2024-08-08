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
    Retrieves data for a specified user ID by making a POST request to a URL,
    processing the response, and returning it as a Pandas DataFrame if successful.
    If the request fails, an error message is displayed and an empty DataFrame is
    returned.

    Args:
        user_id (int | str): Used to construct the payload dictionary that is sent
            as JSON in the POST request to the specified URL. It corresponds to
            the "user_id" key in the payload dictionary.

    Returns:
        pdDataFrame: A pandas DataFrame containing data extracted from the response
        if the request is successful and status code is 200, otherwise it returns
        an empty DataFrame.

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
st.title("Real-time API Query with Streamlit")

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
    Retrieves cached data for a user with a given ID and weights for different
    attributes. It calls an underlying function `get_data` with these parameters,
    which is expected to return relevant data. This allows for caching of frequently
    accessed data for improved performance.

    Args:
        user_id (Any): Expected to be passed by the caller of this function. It
            represents an identifier for a user in the system or application being
            used.
        description_weight (int | float): Used to calculate the importance or
            relevance of product description when ranking products for a given
            user ID.
        category_weight (any): Used to represent the importance or relevance of
            the category when calculating the weighted data for the user.
        name_weight (float): Passed to the underlying `get_data` function. It seems
            to represent the relative importance of name when calculating the
            weighted score.
        price_weight (int | float): Used to specify the relative importance of
            price when retrieving data for a specific user ID.
        review_count_weight (int): Likely used to determine how much weight or
            importance should be given to the review count when calculating a
            ranking score for products.
        review_rating_weight (float): Part of the input to the `get_data` function.

    Returns:
        Any: Retrieved from calling `get_data(user_id, description_weight,
        category_weight, name_weight, price_weight, review_count_weight, review_rating_weight)`.

    """
    return get_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight)

# Function to get data from the API
def get_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight):
    """
    Retrieves data from a specified API endpoint, filters it based on given weights
    for different parameters, and returns the results as a pandas DataFrame. It
    also prints a timestamped message when running the query and handles API errors
    by displaying an error message.

    Args:
        user_id (int): Used as part of the payload to be sent in a POST request,
            likely specifying the ID of a user whose data will be retrieved from
            an API.
        description_weight (float): Part of the payload sent to the server via a
            POST request. Its value represents the weightage given to the description
            field when querying data.
        category_weight (float): Part of the payload sent to the API. It represents
            the weight assigned to the category when calculating the relevance
            score of search results.
        name_weight (float): Part of the payload sent in the POST request to the
            specified URL. It represents the weight assigned to the product name
            when filtering results.
        price_weight (float): Part of the payload dictionary sent to the API. It
            represents the weight or importance given to price while processing
            the query.
        review_count_weight (int | float): 7th in the list of parameters passed
            to this function. It represents a weightage for review count while
            processing queries.
        review_rating_weight (int): Used to specify the weightage of review ratings
            while querying for data. Its value determines how much importance is
            given to review ratings during the query execution process.

    Returns:
        pdDataFrame|pdDataFrame: An empty DataFrame if the request fails, otherwise
        it contains data extracted from the API response and formatted into a
        DataFrame with 10 rows.

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