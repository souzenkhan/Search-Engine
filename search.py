import os
from retriever import load_index_safe, load_doc_id_map, retrieve
from ranker import rank_documents


def search():
    print("Loading search engine...")

    if (not os.path.exists("final_index/merged_index.json")
        or not os.path.exists("final_index/doc_map.json")):

        print("Index is not found. Running indexer first...")
        import indexer
        indexer.build_index()

    index = load_index_safe()
    doc_id_map = load_doc_id_map()

    print("Search engine ready!")

    while True:
        query = input("\nEnter query (or 'quit'): ").strip()

        if query.lower() == "quit":
            print("Exiting...")
            break

        if not query:
            print("Please enter a query.")
            continue

        # Retrieve matching documents
        retrieved_doc_ids = retrieve(query, index)

        if not retrieved_doc_ids:
            print("No results found.")
            continue

        # Rank the retrieved documents
        ranked_doc_ids = rank_documents(
            query,
            retrieved_doc_ids,
            index
        )

        # Convert doc_ids to URLs
        print("\nTop Results:")

        for i, doc_id in enumerate(ranked_doc_ids, start=1):

            url = doc_id_map.get(
                doc_id,
                "URL not found"
            )

            print(f"{i}. {url}")


if __name__ == "__main__":
    search()