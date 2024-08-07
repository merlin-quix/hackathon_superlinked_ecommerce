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
    Retrieves data for a specified `user_id` by sending a POST request to a URL,
    parsing the JSON response, extracting relevant data into a Pandas DataFrame,
    and returning it. If the request fails, it displays an error message and returns
    an empty DataFrame.

    Args:
        user_id (int | str): Required for the function to execute successfully,
            as it forms part of the payload that is sent with the HTTP POST request
            to the specified URL.

    Returns:
        pdDataFrame|pdDataFrame: An empty DataFrame if the request fails, and a
        DataFrame filled with extracted data if the request succeeds.

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
    Retrieves cached data based on user-defined weights for various attributes
    such as user ID, description, category, name, price, and review metrics. It
    caches the result using the `@st.cache_data` decorator to improve performance.

    Args:
        user_id (Any): Used as an input to the `get_data` function. Its value
            represents a unique identifier for a user or item, allowing for data
            retrieval based on this attribute.
        description_weight (float | int): 1 of 7 weights used to calculate the
            overall weight for each data point when fetching data from a database
            using `get_data`.
        category_weight (int | float): Likely used to determine the relative
            importance or weightage given to the category attribute when calculating
            some aggregated value, such as a score.
        name_weight (float): Likely used to indicate the relative importance or
            "weight" of the name attribute in the data retrieval process.
        price_weight (float): Used to determine the importance of the price attribute
            when calculating the weighted sum. Its value represents the relative
            significance of the price in the overall calculation.
        review_count_weight (int): Used as a weight to determine the importance
            or relevance of the review count when calculating the ranking score
            for a user's data.
        review_rating_weight (float): Used to specify the relative importance of
            review ratings in the calculation process, likely for weighting or
            aggregating multiple factors affecting ranking.

    Returns:
        object: The result of calling `get_data` with the specified arguments and
        caching it for future use through the `@st.cache_data` decorator.

    """
    return get_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight)

# Function to get data from the API
def get_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight):
    """
    Retrieves data from a URL via a POST request, using weights to filter results
    by user ID, description, category, name, price, review count, and review rating.
    The response is parsed into a pandas DataFrame if successful, otherwise an
    error message is displayed.

    Args:
        user_id (int | str): Expected to be passed as an input to the function.
            It appears to play a crucial role in constructing the payload sent in
            the POST request, along with other parameters.
        description_weight (int | float): Used to specify the weight of description
            attribute in the query.
        category_weight (float): Part of the JSON payload that is sent to the API
            via a POST request. It likely represents the relative importance of
            the category attribute in the search query.
        name_weight (float): Used to specify the weightage of product name in a
            search query. It determines how much importance should be given to
            product name while searching for data.
        price_weight (float): Used to determine the weight given to price when
            querying data. It appears that this value is used to adjust the
            importance of price in the query results.
        review_count_weight (int): Part of a JSON payload that gets sent to a
            server via an HTTP POST request. It represents the weight given to
            review count in ranking results.
        review_rating_weight (int): 1 of the 8 parameters used to filter and rank
            search results based on their review ratings, along with other weights
            for description, category, name, price, and review count.

    Returns:
        pdDataFrame|pdDataFrame: 0 rows and columns if request fails, otherwise
        it returns a pandas DataFrame containing extracted data. The DataFrame's
        number of rows depends on the 'limit' parameter set to 10 in the payload.

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