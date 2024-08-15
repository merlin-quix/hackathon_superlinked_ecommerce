import streamlit as st
import duckdb
import time
import os
import pandas as pd
import time
from datetime import datetime
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.tools import HoverTool
from bokeh.embed import components
table_name = "user_events"

mdtoken = os.environ['MOTHERDUCK_TOKEN']
mddatabase = os.environ['MOTHERDUCK_DATABASE']

# initiate the MotherDuck connection through a service token through
conn = duckdb.connect(f'md:{mddatabase}?motherduck_token={mdtoken}')

table_name = "user_events"

## Function to get data from MotherDuck
def get_data():
    """
    Runs a SQL query to retrieve data from a database table, sorts the results by
    `page_id`, and returns the data as a Pandas DataFrame. The query execution
    time is also printed to the console with the current timestamp.

    Returns:
        pandasDataFrame: A tabular structure with rows and columns of data, where
        each row represents a single observation or sample, and each column
        represents a variable or feature of the sample.

    """
    print(f"[{datetime.now()}] Running query...")
    query = f"SELECT page_id, count FROM {table_name} ORDER BY page_id ASC"
    df = conn.execute(query).fetchdf()
    return df

# Function to get data and cache it
@st.cache_data
def get_cached_data():
    """
    Caches the result of calling the `get_data` function and returns it instead
    of recomputing it, improving performance by reducing the number of times
    `get_data` is executed.

    Returns:
        Any: A result from calling `get_data` function, either cached data or new
        computation if it's not cached yet.

    """
    return get_data()

# Streamlit UI
st.title("Real-time Dashboard Example Using Streamlit and Quix")
st.markdown("This dasboard reads from a table in MotherDuck which is being continuously updated by a sink process in Quix Cloud. It then displays a dynamically updating Bokeh chart and table underneath.")
st.markdown("In Quix Cloud, we are:\n * Generating synthetic user logs\n * Streaming the data to kafka\n * Reading from Kafka and aggregating the actions per page\n * Sinking the page view counts (which are continuously updating) to MotherDuck\n\n ")
st.markdown("What users could learn: How to read from a real-time source and apply some kind of transformation to the data before bringing it into Streamlit (using only Python)")

# Placeholder for the bar chart and table
chart_placeholder = st.empty()
table_placeholder = st.empty()

# Placeholder for countdown text
countdown_placeholder = st.empty()

# Main loop
while True:
    # Get the data
    df = get_cached_data()

    # Check that data is being retrieved and passed correctly
    if df.empty:
        st.error("No data found. Please check your data source.")
        break

    # Calculate dynamic min and max scales
    min_count = df['count'].min()
    max_count = df['count'].max()
    min_scale = min_count * 0.99
    max_scale = max_count * 1.01

    # Prepare Bokeh data source
    source = ColumnDataSource(df)

    # Create a Bokeh figure without specifying height
    p = figure(x_range=df['page_id'], height=400, title="Page Counts",
               y_range=Range1d(start=min_scale, end=max_scale))

    # Add a hover tool
    hover = HoverTool()
    hover.tooltips = [("Page ID", "@page_id"), ("Count", "@count")]
    p.add_tools(hover)

    # Add bars to the figure
    p.vbar(x='page_id', top='count', width=0.9, source=source)

    # Style the chart
    p.xgrid.grid_line_color = None
    p.yaxis.axis_label = "Count"
    p.xaxis.axis_label = "Page ID"
    p.xaxis.major_label_orientation = "vertical"  # Vertical label orientation

    # Display the Bokeh chart in Streamlit using st.bokeh_chart
    chart_placeholder.bokeh_chart(p, use_container_width=True)

    # Display the dataframe as a table
    table_placeholder.table(df)

    # Countdown
    for i in range(1, 0, -1):
        countdown_placeholder.text(f"Refreshing in {i} seconds...")
        time.sleep(1)

    # Clear the countdown text
    countdown_placeholder.empty()

    # Clear the cache to fetch new data
    get_cached_data.clear()