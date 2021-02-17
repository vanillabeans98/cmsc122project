from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from nltk import FreqDist
import itertools
import csv
import re
import pandas as pd
import unicodedata
import sys
import math
import nltk
nltk.download('wordnet')


STOP_WORDS = ["a", "an", "the", "this", "that", "of", "for", "or",
              "and", "on", "to", "be", "if", "we", "you", "in", "is",
              "at", "it", "rt", "mt", "with"]

STOP_PREFIXES = ("@", "#", "http", "&amp")


def keep_chr(ch):
    '''
    Find all characters that are classifed as punctuation in Unicode
    and combine them into a single string.
    '''
    return unicodedata.category(ch).startswith('P')


PUNCTUATION = " ".join([chr(i) for i in range(sys.maxunicode)
                        if keep_chr(chr(i))])

data = pd.read_csv("./test_data/babareba.csv")
df = pd.DataFrame(data, columns=['Rating', 'Text'])


def processing(text):
    '''
    Converts a text of a review  into a list of strings

    Inputs:
        text (str): text representing one review

    Returns:
        list of words
    '''

    lemmatizer = WordNetLemmatizer()

    # Try to fix spelling errors before splitting
    #textBlb = TextBlob(text)
    #corrected_text = textBlb.correct()

    split_text = text.split()
    new_text = []

    for word in split_text:
        # Handles trailing and inner punctuations
        word = word.strip(PUNCTUATION)
        word = word.replace("&apos;", "'")
        word = word.replace('quot;', '"')
        word = word.replace('&quot', '"')

        word = word.lower()
        lemmatizer.lemmatize(word)

        # Splits words if / present
        if '/' in word:
            words = word.split('/')
            new_text += [word for word in words if not bool(
                re.search(r'\d', word)) and not word.startswith(STOP_PREFIXES)]
        else:
            if (word and not bool(re.search(r'\d', word))
                    and not word.startswith(STOP_PREFIXES)):
                new_text.append(word)

    return new_text


def get_stop_words(tokens):
    '''
    Inputs:
        - tokens (list of list of strings): output of tokenize(df)

    Returns: 
        - list of 10 most common words
    '''
    all_words = list(itertools.chain.from_iterable(tokens))
    freq_dist = FreqDist(all_words)
    stop_words = freq_dist.most_common(10)

    return [word[0] for word in stop_words]


def tokenize(df):
    return [processing(text) for text in df.Text]


def remove_stop(stop_words, tokens):
    pass


# Vectorizing Stage
def count_tokens(tokens):
    '''
    Counts each distinct token (entity) in a list of tokens.

    Inputs:
        tokens: list of tokens (must be immutable)

    Returns: dictionary that maps tokens to counts
    '''
    rv = {}
    for tok in tokens:
        # Initialize entry if unseen; always increment count
        rv[tok] = rv.get(tok, 0) + 1

    return rv


def compute_idf(docs):
    '''
    Calculate the inverse document frequency (idf) for each term (t) in a
    collection of documents (D). By definition,
      idf(t, D) = log(total number of documents in D / number of documents
                      containing t).
    Helper function for find_salient.

    Inputs:
        docs: list of lists of tokens

    Returns: dictionary that maps each term to its idf
    '''
    num_docs = len(docs)

    idf_dict = {}
    docs_set = [set(doc) for doc in docs]
    tokens = set.union(*docs_set)

    for token in tokens:
        docs_with_token = sum([1 for doc in docs_set if (token in doc)])
        idf_dict[token] = math.log(num_docs / docs_with_token)

    return idf_dict


SAMPLE_DOCS = [['i', 'love', 'food', 'so', 'much'],
               ['good', 'service'],
               ['i', 'hate', 'this', 'restaurant']]

# SAMPLE_OUTPUT:
#           i      love      food        so      much      good   service      hate      this  restaurant
# 0  0.405465  1.098612  1.098612  1.098612  1.098612       NaN       NaN       NaN       NaN         NaN
# 1       NaN       NaN       NaN       NaN       NaN  1.098612  1.098612       NaN       NaN         NaN
# 2  0.405465       NaN       NaN       NaN       NaN       NaN       NaN  1.098612  1.098612    1.098612


def tfidf_vectorize(revs):
    '''
    In:
      - list of lists of strings, e.g., [["i", "love", "food"],
                                         ["i", "hate", "food"]]

    Out: pandas DataFrame, e.g.,      i  love  food  hate
                                 0  0.5   0.5   0.5   0.0
                                 1  0.3   0.0   0.4   0.5
    '''
    tok_to_freq_by_rev = [count_tokens(rev) for rev in revs]
    idf = compute_idf(revs)

    for rev in tok_to_freq_by_rev:
        max_freq = max(rev.values())
        for tok in rev:
            tf = 0.5 + 0.5 * (rev[tok] / max_freq)
            rev[tok] = tf * idf[tok]

    return pd.DataFrame(tok_to_freq_by_rev)


def get_final_df(df):
    tokens = tokenize(df)
    stop_words = get_stop_words(tokens)
    cleaned_tokens = remove_stop(stop_words, tokens)

    x_values = tfidf_vectorize(cleaned_tokens)
    y_values = df.Rating

    final_df = x_values.insert(0, y_values)

    return final_df
