from tokenizer import tokenize, stem_tokens

def query_process(query):
    tokens = tokenize(query)

    stemmed_tokens = stem_tokens(tokens)

    return stemmed_tokens


#testing
if __name__ == "__main__":
    query = input("Type query: ")

    processed_query = query_process(query)

    print("Processed tokens:")
    print(processed_query)