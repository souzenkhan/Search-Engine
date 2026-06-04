import json
from query_processing import query_process

#im updating retriever paths to use merged_index.json and doc_map.json
def load_index(index_path: str = "final_index/merged_index.json") -> dict:
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_doc_id_map(map_path: str = "final_index/doc_map.json") -> dict:
    with open(map_path, "r", encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f).items()}


def get_postings(index: dict, term: str) -> list:
    return index.get(term, [])


def retrieve(query: str, index: dict) -> list:
    terms = query_process(query)

    if not terms:
        return []

    # get the set of doc_ids for each query term
    posting_sets = []
    for term in terms:
        postings = get_postings(index, term)
        doc_ids = {p["doc_id"] for p in postings}
        posting_sets.append(doc_ids)
    
    #makes sure smallest posting list is first for efficient intersection
    posting_sets.sort(key=len)

    # AND logic: only keep doc_ids that appear in every term's postings
    result = posting_sets[0]
    for s in posting_sets[1:]:
        result = result & s

    return sorted(result)

# use load_index_safe() instead of load_index() to avoid loading full index into RAM
class IndexHandle:
    def __init__(self, index_path, offsets_path):
        with open(offsets_path, "r", encoding="utf-8") as f:
            self._offsets = json.load(f)
        self._fh = open(index_path, "r", encoding="utf-8")
        self._cache = {}
 
    def get(self, term, default=None):
        postings = self.get_postings(term)
        if postings:
            return postings
        return default if default is not None else []
 
    def __contains__(self, term):
        return term in self._offsets
 
    def get_postings(self, term):
        
        #using cache to avoid disk reads for repeated terms
        if term in self._cache:
            return self._cache[term]

        offset = self._offsets.get(term)

        if offset is None:
            return []

        self._fh.seek(offset)

        buf = []
        depth = 0
        found = False

        while True:
            ch = self._fh.read(1)

            if not ch:
                break

            buf.append(ch)

            if ch == '[':
                depth += 1
                found = True

            elif ch == ']':
                depth -= 1

                if found and depth == 0:
                    break

        if not buf or not found:
            return []

        try:
            postings = json.loads("".join(buf))

            #cache postings so future lookups avoid disk reads
            self._cache[term] = postings

            return postings

        except json.JSONDecodeError:
            return []
 
    def close(self):
        self._fh.close()
 
 
def load_index_safe(index_path: str = "final_index/merged_index.json", offsets_path: str = "final_index/term_offsets.json") -> IndexHandle:
    return IndexHandle(index_path, offsets_path)
 
 


if __name__ == "__main__":
    print("Loading index...")
    index = load_index()
    doc_id_map = load_doc_id_map()

    while True:
        query = input("\nEnter query (or 'quit'): ").strip()
        if query.lower() == "quit":
            break

        doc_ids = retrieve(query, index)

        if not doc_ids:
            print("No results found.")
        else:
            print(f"{len(doc_ids)} result(s):")
            for doc_id in doc_ids:
                print(f"  [{doc_id}] {doc_id_map.get(doc_id, 'unknown')}")
