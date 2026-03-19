
# from pymongo import MongoClient
# import streamlit as st


# def get_database():
#     client = MongoClient(st.secrets["MONGO_URI"])
#     return client["m3_pediatric_db"]
 

"""
MongoDB connection for the FastAPI backend.
Reads MONGO_URI from the environment (set via .env or system env).
"""

import os
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()  # loads .env if present

_client: MongoClient | None = None


def get_database() -> Database:
    """
    Returns the MongoDB database instance.
    Uses a module-level singleton so the connection is reused across requests.
    """
    global _client
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        raise RuntimeError("MONGO_URI environment variable is not set.")
        
    # FORCE CLEAN THE STRING: remove all spaces, newlines, and literal quotes
    clean_uri = mongo_uri.strip().strip('"').strip("'")
    
    # Adding brackets to the print statement helps visualize if any weird spaces remain
    print(f"DEBUG MONGO_URI: [{clean_uri}]") 

    if _client is None:
        _client = MongoClient(clean_uri)
        
    return _client["m3_pediatric_db"]
