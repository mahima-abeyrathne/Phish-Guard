import nltk
import os
import sys

# Define a custom NLTK data path within your project
NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
if NLTK_DATA_PATH not in nltk.data.path:
    nltk.data.path.append(NLTK_DATA_PATH)
os.makedirs(NLTK_DATA_PATH, exist_ok=True) # Ensure the directory exists
print(f"NLTK data path set to: {NLTK_DATA_PATH}")

def download_nltk_datasets():
    """Download required NLTK data to the specified path."""
    datasets = ['punkt', 'stopwords', 'vader_lexicon']
    
    print("\n--- Downloading NLTK Data ---")
    for dataset in datasets:
        try:
            nltk.data.find(f'corpora/{dataset}')
            print(f"'{dataset}' already downloaded.")
        except nltk.downloader.DownloadError:
            print(f"Downloading '{dataset}'...")
            try:
                nltk.download(dataset, download_dir=NLTK_DATA_PATH, quiet=False)
                print(f"Successfully downloaded '{dataset}'.")
            except Exception as e:
                print(f"ERROR: Failed to download '{dataset}': {e}")
                print("Please check your internet connection or try running this script with administrator privileges.")
                sys.exit(1)
    print("\n--- NLTK Data Download Complete ---")

if __name__ == "__main__":
    download_nltk_datasets()
    print("\nNLTK data download script finished. You can now run your Flask application.")
