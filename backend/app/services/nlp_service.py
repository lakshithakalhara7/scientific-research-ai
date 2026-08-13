import nltk
import string

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


# Download required NLTK resources
nltk.download("punkt_tab")
nltk.download("stopwords")


# Load English stopwords
stop_words = set(stopwords.words("english"))


def preprocess_text(text: str):

    # Step 1 - Convert text to lowercase
    text = text.lower()

    # Step 2 - Remove punctuation
    text = text.translate(
        str.maketrans("", "", string.punctuation)
    )

    # Step 3 - Tokenization
    tokens = word_tokenize(text)

    # Step 4 - Remove stopwords
    filtered_tokens = [
        word
        for word in tokens
        if word not in stop_words
    ]

    return filtered_tokens