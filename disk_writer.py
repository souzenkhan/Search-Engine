import os
import json
import heapq

#directory

#folder, temp partial indexs
PARTIAL_DIR = "partial_indexes"
#folder, final merge index files
FINAL_DIR = "final_index"

#directories
os.makedirs(PARTIAL_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

#check posting before save
def is_valid_posts(posting):
    need_attributes = ["doc_id", "tf", "important_tf"]

    for attr in need_attributes:
        if not hasattr(posting, attr):
            return False

    if not isinstance(posting.doc_id, int):
        return False

    if posting.tf < 0:
        return False

    if posting.important_tf < 0:
        return False

    return True

def serial_posts(posting):
    #posting object into dict, -> json
    return {
        "doc_id": posting.doc_id,
        "tf": posting.tf,
        "important_tf": posting.important_tf
    }

def write_partial_index(index, partial_number):
    #current mim inverted index -> partail json file on disk
    #alphabetical, so merge better
    if not isinstance(index, dict):
        raise TypeError("Error: idx not dict")

    if partial_number < 0:
        raise ValueError("error: partial num is neg")

    output_path = os.path.join(
        PARTIAL_DIR,
        f"partial_index_{partial_number}.json"
    )

    #clean dict saved
    idx_clean = {}

    #debugging help
    total_terms = 0
    total_posts = 0
    skip_terms = 0
    skip_posts = 0

    #alphabetical
    terms_sorts = sorted(index.keys())

    #go through each term
    for term in terms_sorts:
        if not isinstance(term, str):
            skip_terms += 1
            continue

        posts = index.get(term)

        #skip wrong posts
        if posts is None:
            skip_terms += 1
            continue

        if not isinstance(posts, list):
            skip_terms += 1
            continue

        serial_postings = []

        #go thourgh each posting
        for posting in posts:

            #skip bad postings
            if not is_valid_posts(posts):
                skip_posts += 1
                continue

            #posting obj -> dict
            serial_postings.append(serial_postings(posting))

            total_posts += 1

        #save ones that have good postings
        if serial_postings:
            idx_clean[term] = serial_postings
            total_terms += 1

    #clean partial idx to disk
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(
            idx_clean, output_file, indent=2
        )

    #get file size in kb
    file_size_in_kb = round(os.path.getsize(output_path) / 1024, 2)

    #debug
    print(f"info: partial idx save {output_path}")
    print(f"info: uniuq terms {total_terms}")
    print(f"info: total posts {total_posts}")
            




