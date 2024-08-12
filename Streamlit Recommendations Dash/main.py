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
    Submits a POST request to a specified URL, passing a JSON payload containing
    user ID and query parameters. If the response is successful (200 status code),
    it extracts data from the response, converts it into a Pandas DataFrame, and
    returns it. Otherwise, it displays an error message.

    Args:
        user_id (int | str): Passed to the payload dictionary, which is used in
            an HTTP POST request to retrieve data based on the provided user ID.

    Returns:
        pdDataFrame: A pandas DataFrame object that contains the extracted data
        from the query results, if the request is successful. If the request fails,
        it returns an empty pandas DataFrame.

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
    Caches the results of a call to `get_data` by using the `@st.cache_data`
    decorator. It takes seven parameters and returns the result of the cached or
    recalculated data based on these parameters.

    Args:
        user_id (any): Used to retrieve cached data for a specific user. It appears
            to be an identifier that corresponds to a user entity, possibly used
            to filter or query data related to that user.
        description_weight (int | float): Used to specify the relative importance
            or weighting factor for the description attribute when retrieving data
            related to a specific user ID.
        category_weight (int | float): Used to weight the importance of the category
            in determining the ranking of items, likely within a machine learning
            model or algorithm.
        name_weight (float): 1 of the input parameters used to calculate the weights
            for the data retrieval process, alongside other weight parameters such
            as `description_weight`, `category_weight`, etc.
        price_weight (float): Used to specify the relative importance or weightage
            of price in calculating the score or ranking for each data item.
        review_count_weight (float): Used to calculate the weighted importance of
            the review count for filtering or sorting purposes, along with other
            parameters such as description weight, category weight, etc.
        review_rating_weight (float): Used to calculate the weightage or importance
            given to the review rating while retrieving data for a user, with
            higher values indicating greater significance.

    Returns:
        Any: Retrieved from the call to `get_data`. This implies that the result
        depends on the actual arguments passed and their corresponding weights,
        but it's not clear without additional context what data is being retrieved.

    """
    return get_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight)

# Function to get data from the API
def get_data(user_id, description_weight, category_weight, name_weight, price_weight, review_count_weight, review_rating_weight):
    """
    Retrieves data from an API using a POST request and converts it to a Pandas
    DataFrame. It takes several weights as parameters, which are likely used for
    filtering or ranking results. The function returns a DataFrame containing the
    extracted data if the request is successful; otherwise, it returns an empty DataFrame.

    Args:
        user_id (str | int): Required for the request payload to fetch data from
            an API based on the provided user ID.
        description_weight (float): Used to weight the importance of the product
            description in the search query. It is passed along with other weights
            for category, name, price, review count, and review rating to influence
            the search results.
        category_weight (float): Used as part of the payload for a POST request
            to a specified URL. It represents a weight value corresponding to the
            category attribute of data records being queried.
        name_weight (float): Used to determine the weightage given to the name
            attribute when querying data from an API. It affects the relevance of
            results based on the importance assigned to this attribute.
        price_weight (float): Part of a JSON payload sent as a POST request to an
            unknown URL (`url`). It appears to be used for filtering or ranking
            search results based on product price.
        review_count_weight (int): Used to specify the weight assigned to the
            review count when calculating the overall relevance score of results
            returned from the query.
        review_rating_weight (float): Part of the payload sent to the API through
            a POST request. It represents the relative importance of review ratings
            when ranking results.

    Returns:
        pdDataFrame: A pandas DataFrame object if the request was successful and
        data could be extracted, otherwise it returns an empty pandas DataFrame.

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