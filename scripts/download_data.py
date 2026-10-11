"""
Dataset Downloader & Preparation Script
----------------------------------------
Downloads the Kaggle Book Recommendation Dataset (arashnic/book-recommendation-dataset)
and places Books.csv, Users.csv, and Ratings.csv into data/raw/.
Includes automatic fallback to synthetic Kaggle-formatted data if offline or unavailable.
"""

import os
import sys
import shutil
import glob
import pandas as pd
import numpy as np

DATA_RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")

def ensure_directory():
    os.makedirs(DATA_RAW_DIR, exist_ok=True)

def check_existing_files():
    required = ["Books.csv", "Users.csv", "Ratings.csv"]
    existing = [f for f in required if os.path.exists(os.path.join(DATA_RAW_DIR, f))]
    return len(existing) == 3

def download_via_kagglehub():
    print("Attempting dataset download via kagglehub ('arashnic/book-recommendation-dataset')...")
    try:
        import kagglehub
        path = kagglehub.dataset_download("arashnic/book-recommendation-dataset")
        print(f"Downloaded raw dataset files to: {path}")

        # Find CSV files in path (handling casing differences)
        found_files = glob.glob(os.path.join(path, "*.csv"))
        if not found_files:
            # Check nested folders
            found_files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)

        print(f"Found files: {found_files}")

        mapping = {
            "book": "Books.csv",
            "user": "Users.csv",
            "rating": "Ratings.csv"
        }

        for src in found_files:
            base = os.path.basename(src).lower()
            for key, target_name in mapping.items():
                if key in base:
                    dest = os.path.join(DATA_RAW_DIR, target_name)
                    shutil.copy2(src, dest)
                    print(f"Copied {src} -> {dest}")

        return check_existing_files()
    except Exception as e:
        print(f"kagglehub download failed or unconfigured: {e}")
        return False

def generate_realistic_fallback_dataset():
    print("\nGenerating realistic Kaggle-formatted dataset for testing & offline reproducibility...")
    ensure_directory()

    np.random.seed(42)

    # 1. Generate Books.csv
    genres = ["Fiction", "Fantasy", "Mystery", "Romance", "Science Fiction", "Thriller", "Non-Fiction", "Classics", "Biography", "History"]
    authors = ["J.K. Rowling", "Stephen King", "Agatha Christie", "J.R.R. Tolkien", "George Orwell", "Jane Austen", "Haruki Murakami", "Ernest Hemingway", "F. Scott Fitzgerald", "Gillian Flynn", "Dan Brown", "Neil Gaiman", "Margaret Atwood", "Isaac Asimov", "Gabriel García Márquez"]
    publishers = ["Penguin Books", "HarperCollins", "Random House", "Simon & Schuster", "Macmillan Publishers", "Hachette Book Group", "Vintage", "Oxford University Press"]

    title_prefixes = ["The", "A", "Journey to", "Echoes of", "Secrets of", "Beyond the", "Chronicles of", "The Shadow of", "Tales from", "The Art of"]
    title_words = ["Silence", "Dragon", "Stars", "Empire", "Midnight", "Memory", "Ocean", "Winter", "Whisper", "Alchemist", "Labyrinth", "Storm", "Phoenix", "Solitude", "Grace", "Forest"]

    books = []
    for i in range(1, 801):
        isbn = f"{978000000000 + i:013d}" if i % 2 == 0 else f"{0000000000 + i:010d}"
        prefix = np.random.choice(title_prefixes)
        word1 = np.random.choice(title_words)
        word2 = np.random.choice(title_words)
        title = f"{prefix} {word1} {word2}" if word1 != word2 else f"{prefix} {word1}"
        author = np.random.choice(authors)
        year = int(np.random.randint(1950, 2024))
        publisher = np.random.choice(publishers)
        img_s = f"https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=100&q=80"
        img_m = f"https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80"
        img_l = f"https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80"

        books.append({
            "ISBN": isbn,
            "Book-Title": title,
            "Book-Author": author,
            "Year-Of-Publication": year,
            "Publisher": publisher,
            "Image-URL-S": img_s,
            "Image-URL-M": img_m,
            "Image-URL-L": img_l
        })

    df_books = pd.DataFrame(books)
    df_books.to_csv(os.path.join(DATA_RAW_DIR, "Books.csv"), index=False)
    print(f"Created Books.csv: {len(df_books)} books.")

    # 2. Generate Users.csv
    cities = ["New York, NY, USA", "London, England, UK", "Toronto, ON, Canada", "Sydney, NSW, Australia", "Berlin, Germany", "Paris, France", "Tokyo, Japan", "Chicago, IL, USA", "Austin, TX, USA", "Seattle, WA, USA"]
    users = []
    for uid in range(1, 1201):
        location = np.random.choice(cities)
        age = int(np.random.randint(18, 75)) if np.random.rand() > 0.1 else np.nan
        users.append({
            "User-ID": uid,
            "Location": location,
            "Age": age
        })
    df_users = pd.DataFrame(users)
    df_users.to_csv(os.path.join(DATA_RAW_DIR, "Users.csv"), index=False)
    print(f"Created Users.csv: {len(df_users)} users.")

    # 3. Generate Ratings.csv (power law interaction distribution)
    ratings = []
    user_ids = df_users["User-ID"].values
    isbns = df_books["ISBN"].values

    # Give popular books more ratings
    popular_isbns = np.random.choice(isbns, size=50, replace=False)

    for uid in user_ids:
        # Number of books rated by user (power law)
        num_ratings = int(np.random.negative_binomial(2, 0.1) + 1)
        num_ratings = min(num_ratings, 80)

        # Select books (mix of popular and random)
        pop_count = min(num_ratings, int(np.random.binomial(num_ratings, 0.6)))
        rand_count = num_ratings - pop_count

        chosen_pop = np.random.choice(popular_isbns, size=min(pop_count, len(popular_isbns)), replace=False)
        chosen_rand = np.random.choice(isbns, size=min(rand_count, len(isbns)), replace=False)
        rated_isbns = list(set(list(chosen_pop) + list(chosen_rand)))

        for isbn in rated_isbns:
            # 80% explicit (1-10), 20% implicit (0)
            if np.random.rand() > 0.2:
                # Skewed ratings towards 6-10
                rating = int(np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], p=[0.02, 0.03, 0.05, 0.05, 0.10, 0.15, 0.20, 0.20, 0.10, 0.10]))
            else:
                rating = 0

            ratings.append({
                "User-ID": uid,
                "ISBN": isbn,
                "Book-Rating": rating
            })

    df_ratings = pd.DataFrame(ratings).drop_duplicates(subset=["User-ID", "ISBN"])
    df_ratings.to_csv(os.path.join(DATA_RAW_DIR, "Ratings.csv"), index=False)
    print(f"Created Ratings.csv: {len(df_ratings)} ratings.")

def main():
    ensure_directory()
    if check_existing_files():
        print("Raw dataset files (Books.csv, Users.csv, Ratings.csv) already present in data/raw/.")
    else:
        success = download_via_kagglehub()
        if not success or not check_existing_files():
            print("\nCould not fetch dataset via kagglehub API. Generating high-quality dataset...")
            generate_realistic_fallback_dataset()

    print("\nDataset preparation status:")
    for f in ["Books.csv", "Users.csv", "Ratings.csv"]:
        path = os.path.join(DATA_RAW_DIR, f)
        if os.path.exists(path):
            df = pd.read_csv(path, low_memory=False)
            print(f"  - {f}: {len(df):,} rows, columns: {list(df.columns)}")
        else:
            print(f"  - MISSING: {f}")

if __name__ == "__main__":
    main()
