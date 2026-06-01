from query_processing import query_process
import math

#tf vals is valid
def safe_number(value):
    if isinstance(value, int) or isinstance(value, float):
        return max(value, 0)
    return 0

#build doc scores
#tf + (important_tf * 2)
def build_document_scores(query, retrieved_doc_ids, inverted_index):
    #took out cause causing errors
    #if not isinstance(inverted_index, dict):
        #index correct
        #raise TypeError("index must be a dict")
    if inverted_index is None:
        raise ValueError("index cannot be None")
    
    if retrieved_doc_ids is None:
        return {}

    #lowercase, tokenize, stem
    processed_terms = query_process(query)

    #no dupes
    processed_terms = list(set(processed_terms))

    #convert to set
    valid_docs = set(retrieved_doc_ids)

    #doc_is -> score
    document_scores = {}
    matched_terms = {}

    #go through everthing
    for term in processed_terms:
        if term not in inverted_index:
            continue

        #get posting
        postings_list = inverted_index.get(term)

        #document frequency
        doc_frequency = len(postings_list)

        #idf score
        idf = math.log(
            1 + (1 / max(doc_frequency, 1))
        )

        #checks
        if not isinstance(postings_list, list):
            continue
        #loop
        for posting in postings_list:
            if not isinstance(posting, dict):
                continue
                #get doc id
            current_doc_id = posting.get("doc_id")

            if current_doc_id not in valid_docs:
                continue

             #count matched query terms
            if current_doc_id not in matched_terms:
                matched_terms[current_doc_id] = 0

            matched_terms[current_doc_id] += 1

            #get tf score
            tf_value = safe_number(
                posting.get("tf", 0)
            )
            #importantt tf score
            important_value = safe_number(
                posting.get("important_tf", 0)
            )
            #final score
            combined_score = (tf_value * idf) + (important_value * 5)

            if current_doc_id not in document_scores:
                document_scores[current_doc_id] = 0

            document_scores[current_doc_id] += combined_score

    #bonus for matching multiple query terms
    for doc_id in document_scores:
        document_scores[doc_id] += matched_terms.get(doc_id, 0) * 5

    #return doc id: score
    return document_scores

#ranking
#high to low
def rank_documents(query, retrieved_doc_ids, inverted_index, limit = 5):
    if not retrieved_doc_ids:
        return []

    #get score
    scores = build_document_scores(query, retrieved_doc_ids, inverted_index
    )

    sortable_results = []
    #convert dict into list
    for doc_id, score in scores.items():
        sortable_results.append((doc_id, score))
    #hiher score first lower doc_id wins tie
    sortable_results.sort(key=lambda item: (-item[1], item[0]))

    #get top scores, final doc ids only
    top_ranked = sortable_results[:limit]

    final_doc_ids = []

    for doc_id, _ in top_ranked:
        final_doc_ids.append(doc_id)

    return final_doc_ids

#test
if __name__ == "__main__":
    sample_index = {
        "learn": [
            {
                "doc_id": 1,
                "tf": 4,
                "important_tf": 1
            },
            {
                "doc_id": 3,
                "tf": 8,
                "important_tf": 3
            }
        ]
    }
    retrieved_docs = [1]

    rank_docs = rank_documents("machine learning", retrieved_docs, sample_index)

    print ("ranked docs IDS:")
    print(rank_docs)
