import csv
import pandas as pd
import unicodedata
import sys
import math
import nltk
nltk.download('wordnet')

from nltk.stem import WordNetLemmatizer

STOP_WORDS = ["a", "an", "the", "this", "that", "of", "for", "or",
              "and", "on", "to", "be", "if", "we", "you", "in", "is",
              "at", "it", "rt", "mt", "with"]

def keep_chr(ch):
    '''
    Find all characters that are classifed as punctuation in Unicode
    (except #, @, &) and combine them into a single string.
    '''
    return unicodedata.category(ch).startswith('P') and \
        (ch not in ("#", "@", "&"))

PUNCTUATION = " ".join([chr(i) for i in range(sys.maxunicode)
                        if keep_chr(chr(i))])

STOP_PREFIXES = ("@", "#", "http", "&amp")

data = pd.read_csv("./test_data/babareba.csv")
df = pd.DataFrame(data, columns = ['Rating', 'Text'])

#df[reviews].apply()

def processing(df):
    X_array = [] 
    lemmatizer = WordNetLemmatizer()
    for i, row in df.iterrows():
        processed_review = []
    #this is def wrong need to fix, need to be able to iterate through the paragraph of the review itself
        review = row["Text"]
        #print(review)
        split_review = review.split()
        for word in split_review:
            word = word.strip(PUNCTUATION)
            word = word.lower()
            lemmatizer.lemmatize(word)
            if word not in set(STOP_WORDS) and not word.startswith(STOP_PREFIXES) and len(word) > 0:
                processed_review.append(word)
        X_array.append(processed_review)
    print(X_array)

#def parse_words():
    #pass

# ↓ From PA3 ↓

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
    # Determine total number of documents in total
    num_docs = len(docs)

    # Determine number of documents containing relevant term
    rv = {}
    for doc in docs:
        seen_terms = []
        for term in doc:
            if term not in seen_terms:
                rv[term] = rv.get(term, 0) + 1
            seen_terms.append(term)

    # Calculate idf
    for term, num_with_term in rv.items():
        rv[term] = math.log(num_docs / num_with_term)

    return rv

SAMPLE_DOCS = [['i', 'love', 'food', 'so', 'much'],
               ['good', 'service'],
               ['i', 'hate', 'this', 'restaurant']]

# SAMPLE_OUTPUT:
#           i      love      food        so      much      good   service      hate      this  restaurant
# 0  0.405465  1.098612  1.098612  1.098612  1.098612       NaN       NaN       NaN       NaN         NaN
# 1       NaN       NaN       NaN       NaN       NaN  1.098612  1.098612       NaN       NaN         NaN
# 2  0.405465       NaN       NaN       NaN       NaN       NaN       NaN  1.098612  1.098612    1.098612

def tfidf_vectorize(revs, idf):
    '''
    In:
      - list of lists of strings, e.g., [["i", "love", "food"],
                                         ["i", "hate", "food"]]
      - dictionary (each token -> its IDF)
    
    Out: pandas DataFrame, e.g.,      i  love  food  hate
                                 0  0.5   0.5   0.5   0.0
                                 1  0.3   0.0   0.4   0.5
    '''
    tok_to_freq_by_rev = [count_tokens(rev) for rev in revs]

    for rev in tok_to_freq_by_rev:
        max_freq = max(rev.values())
        for w in rev:
            tf = 0.5 + 0.5 * (rev[w] / max_freq)
            rev[w] = tf * idf[w]            
    
    return pd.DataFrame(tok_to_freq_by_rev)