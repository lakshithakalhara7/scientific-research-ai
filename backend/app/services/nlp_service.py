import string
import nltk

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# --------------------------------------------------
# Download required NLTK resources
# --------------------------------------------------

required_resources = {
    "tokenizers/punkt_tab": "punkt_tab",
    "corpora/stopwords": "stopwords",
    "corpora/wordnet": "wordnet",
    "corpora/omw-1.4": "omw-1.4",
}


for resource_path, resource_name in required_resources.items():
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(resource_name)


# --------------------------------------------------
# Load NLP tools
# --------------------------------------------------

stop_words = set(
    stopwords.words("english")
)

lemmatizer = WordNetLemmatizer()


# --------------------------------------------------
# Main preprocessing function
# --------------------------------------------------

def preprocess_text(text: str):
    """
    Preprocess research document text or user queries.

    Steps:
    1. Convert text to lowercase
    2. Tokenize text
    3. Remove punctuation
    4. Remove stopwords
    5. Apply lemmatization

    Returns:
        List of processed tokens
    """

    # Step 1 - Convert to lowercase
    text = text.lower()

    # Step 2 - Tokenization
    tokens = word_tokenize(text)

    processed_tokens = []

    for token in tokens:

        # Step 3 - Remove punctuation-only tokens
        if all(
            character in string.punctuation
            for character in token
        ):
            continue

        # Remove empty tokens
        if not token.strip():
            continue

        # Step 4 - Remove stopwords
        if token in stop_words:
            continue

        # Keep tokens that contain at least
        # one letter or number
        if not any(
            character.isalnum()
            for character in token
        ):
            continue

        # Step 5 - Lemmatization
        #
        # First treat the word as a verb.
        # Example:
        # running -> run
        #
        # Then treat it as a noun.
        # Example:
        # children -> child

        token = lemmatizer.lemmatize(
            token,
            pos="v"
        )

        token = lemmatizer.lemmatize(
            token,
            pos="n"
        )

        processed_tokens.append(token)

    return processed_tokens


# --------------------------------------------------
# Optional helper function
# --------------------------------------------------

def preprocess_to_string(text: str):
    """
    Return processed tokens as a single string.

    Useful later for indexing or debugging.
    """

    tokens = preprocess_text(text)

    return " ".join(tokens)