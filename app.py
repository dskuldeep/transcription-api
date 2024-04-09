import streamlit as st
from sqlalchemy import create_engine, text, MetaData, Table
import pandas as pd

# Function to create a connection to the PostgreSQL database
def connect_to_db():
    engine = create_engine('postgresql://postgres:password@api.getzetachi.com/db1')
    return engine

# Function to fetch data from the PostgreSQL database
def fetch_data(engine, table_name):
    try:
        # Fetch all records from the specified table
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


def delete_data(engine, table_name):
    try:
        with engine.connect() as connection:
            # Execute the delete query
            connection.execute(text(f"DELETE FROM {table_name};"))
        st.success("Table Reset")
    except Exception as error:
        st.error(f"Error: {error}")

# Main function to run the Streamlit app
def main():
    st.title("PostgreSQL Database Viewer & Reset")

    # Connect to the PostgreSQL database
    engine = connect_to_db()
    if engine:
        st.write("Connected to PostgreSQL database")
    else:
        st.error("Failed to connect to database")

    # User input for table name
    table_name = st.text_input("Enter table name:")

    # Fetch data from the specified table
    if st.button("Fetch Data"):
        if table_name:
            data = fetch_data(engine, table_name)
            if data is not None:
                st.write("Data fetched successfully:")
                st.write(data)
        else:
            st.warning("Please enter a table name.")

    # Button to delete all data from the database
    if st.button("Delete Data and Reset Database"):
        delete_data(engine, table_name)

# Run the Streamlit app
if __name__ == "__main__":
    main()
