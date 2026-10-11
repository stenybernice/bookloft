"""
MongoDB Database Seeding Script
--------------------------------
Loads cleaned books, users, and ratings from data/processed/,
inserts them into MongoDB using efficient bulk operations,
and builds database indexes.
"""

import os
import json
import pandas as pd
import pymongo
from pymongo import MongoClient, UpdateOne, IndexModel, ASCENDING, DESCENDING, TEXT

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PROC_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "book_recommender")

def seed_database():
    print("=" * 60)
    print("STARTING MONGODB SEEDING PIPELINE")
    print(f"Connecting to MongoDB at: {MONGODB_URI} (DB: {DATABASE_NAME})")
    print("=" * 60)

    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("Connected to MongoDB successfully!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Please verify that MongoDB service is running on port 27017.")
        return False

    db = client[DATABASE_NAME]

    books_path = os.path.join(DATA_PROC_DIR, "cleaned_books.csv")
    users_path = os.path.join(DATA_PROC_DIR, "cleaned_users.csv")
    ratings_path = os.path.join(DATA_PROC_DIR, "cleaned_ratings.csv")

    if not (os.path.exists(books_path) and os.path.exists(users_path) and os.path.exists(ratings_path)):
        print("Processed files missing in data/processed/. Running preprocessing first...")
        from preprocess import preprocess_pipeline
        preprocess_pipeline()

    # 1. Seed Books Collection
    print("\n1. Seeding 'books' collection...")
    books_df = pd.read_csv(books_path)
    books_coll = db["books"]
    books_coll.delete_many({})  # Clear previous data

    books_docs = books_df.to_dict(orient="records")
    for doc in books_docs:
        doc["_id"] = str(doc["isbn"])
        doc["year"] = int(doc["year"])
        doc["rating_count"] = int(doc["rating_count"])
        doc["avg_rating"] = float(doc["avg_rating"])
        doc["popularity_score"] = float(doc["popularity_score"])

    # Bulk insert in batches of 1000
    batch_size = 1000
    for i in range(0, len(books_docs), batch_size):
        batch = books_docs[i:i+batch_size]
        books_coll.insert_many(batch)
    print(f"   Inserted {books_coll.count_documents({}):,} books.")

    # 2. Seed Users Collection
    print("\n2. Seeding 'users' collection...")
    users_df = pd.read_csv(users_path)
    users_coll = db["users"]
    users_coll.delete_many({})

    users_docs = users_df.to_dict(orient="records")
    for doc in users_docs:
        doc["_id"] = str(int(doc["user_id"]))
        doc["user_id"] = int(doc["user_id"])
        doc["age"] = int(doc["age"])

    for i in range(0, len(users_docs), batch_size):
        batch = users_docs[i:i+batch_size]
        users_coll.insert_many(batch)
    print(f"   Inserted {users_coll.count_documents({}):,} users.")

    # 3. Seed Ratings Collection
    print("\n3. Seeding 'ratings' collection...")
    ratings_df = pd.read_csv(ratings_path)
    ratings_coll = db["ratings"]
    ratings_coll.delete_many({})

    ratings_docs = ratings_df.to_dict(orient="records")
    for doc in ratings_docs:
        u_id = int(doc["user_id"])
        isbn = str(doc["isbn"])
        doc["_id"] = f"{u_id}_{isbn}"
        doc["user_id"] = u_id
        doc["isbn"] = isbn
        doc["rating"] = int(doc["rating"])

    for i in range(0, len(ratings_docs), batch_size):
        batch = ratings_docs[i:i+batch_size]
        ratings_coll.insert_many(batch)
    print(f"   Inserted {ratings_coll.count_documents({}):,} ratings.")

    # 4. Create MongoDB Indexes
    print("\n4. Building MongoDB Indexes...")

    # Books Indexes
    books_coll.create_index([("isbn", ASCENDING)], unique=True)
    books_coll.create_index([("title", TEXT), ("author", TEXT)])
    books_coll.create_index([("popularity_score", DESCENDING)])
    books_coll.create_index([("avg_rating", DESCENDING)])

    # Users Indexes
    users_coll.create_index([("user_id", ASCENDING)], unique=True)

    # Ratings Indexes
    ratings_coll.create_index([("user_id", ASCENDING), ("isbn", ASCENDING)], unique=True)
    ratings_coll.create_index([("user_id", ASCENDING)])
    ratings_coll.create_index([("isbn", ASCENDING)])
    ratings_coll.create_index([("rating", DESCENDING)])

    print("Successfully built all database indexes!")

    print("\n" + "=" * 60)
    print("MONGODB SEEDING COMPLETE!")
    print(f"  - Books Documents:   {books_coll.count_documents({}):,}")
    print(f"  - Users Documents:   {users_coll.count_documents({}):,}")
    print(f"  - Ratings Documents: {ratings_coll.count_documents({}):,}")
    print("=" * 60)
    return True

if __name__ == "__main__":
    seed_database()
