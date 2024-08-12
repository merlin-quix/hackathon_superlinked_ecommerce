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
    Retrieves data from a URL using a POST request with JSON payload, containing
    parameters such as user ID and weights for different categories. It processes
    the response, extracting relevant data into a Pandas DataFrame, which is then
    returned if the request is successful, or an empty DataFrame otherwise.

    Args:
        user_id (int | str): Required for making a POST request to a specified URL
            with the provided payload, which includes the user ID and other query
            parameters.

    Returns:
        pdDataFrame: A two-dimensional labeled data structure with columns of
        potentially different types. If an error occurs during API call, it returns
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
    Retrieves cached data for a given user ID and set of weights, passing these
    parameters to the `get_data` function and returning its result.

    Args:
        user_id (any): Used to retrieve data. It seems that this value corresponds
            to a unique identifier for each user in the system.
        description_weight (int | float): Used as an input to the internal `get_data`
            function along with other parameters to retrieve data related to user
            ID.
        category_weight (int | float): Used as an input to the `get_data` function.
            Its purpose is not explicitly defined, but based on its name and usage
            alongside other weights, it likely represents the relative importance
            or relevance of a product's category in the calculation.
        name_weight (float): Used to weight the importance of name attribute in
            the data retrieved by the `get_data` function.
        price_weight (float | int): Used to specify the relative importance of
            price when calculating the weighted average score for a product.
        review_count_weight (int): Used to control how much weight should be given
            to the review count while ranking products for a user.
        review_rating_weight (float): Part of the input data to calculate weighted
            scores for user profiles.

    Returns:
        object: Returned from calling `get_data(user_id, description_weight,
        category_weight, name_weight, price_weight, review_count_weight, review_rating_weight)`.

    """
    return get_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight)

# Function to get data from the API
def get_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight):
    """
    Retrieves data from a server using a POST request, based on user-provided
    weights for different attributes. It returns a pandas DataFrame containing the
    extracted data if the request is successful; otherwise, it displays an error
    message and returns an empty DataFrame.

    Args:
        user_id (int): Used as part of the payload when making an HTTP POST request
            to a specified URL. It represents the unique identifier of a user.
        description_weight (float): Used to specify the weight of the description
            attribute when querying data. It represents how important the description
            field is for the query results.
        category_weight (float): Part of a payload to be sent in a POST request
            to an unspecified URL (`url`). Its value determines the weightage given
            to the category while processing data.
        name_weight (float): Assigned to a key-value pair in the `payload` dictionary
            with a default value "name_weight". Its purpose is likely to indicate
            the relative importance of product name in search query.
        price_weight (float): Used to specify the weightage given to price while
            generating the query.
        review_count_weight (int): Used to specify the weight given to review count
            when querying data.
        review_rating_weight (float): Used to specify the weightage given to review
            ratings while calculating the ranking of search results.

    Returns:
        pdDataFrame: A two-dimensional table of data (similar to an Excel spreadsheet)
        that can be used for analysis and manipulation. The DataFrame contains
        extracted data from the response, if the request was successful. Otherwise,
        it returns an empty DataFrame.

    """
    print(f"[{datetime.now()}] Running query...")
    payload = {
        "user_id": str(user_id),
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
        print(f"Request failed with status code {response.status_code}: {response.text}")
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