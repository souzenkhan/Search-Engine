import re 
from nltk.stem import PorterStemmer
from parser import parse_document 
from collections import Counter


def tokenize(text):
    text = text.lower()
    tokens = re.findall(r"[a-z0-9]+", text)
    return tokens

def stem_tokens(text):
    porter_stemmer = PorterStemmer()
    return [porter_stemmer.stem(token) for token in text]

def count_frequencies(tokens):
    return Counter(tokens)

