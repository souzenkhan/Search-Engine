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
            
def merge_partial_idxs():
    #merge all partial idx, k-way heap merge
    
    partial_files = sorted([
        file_name
        for file_name in os.listdir(PARTIAL_DIR)

        if (
            file_name.startswith("partial_index_")
            and file_name.endswith(".json")
            and os.path.isfile(
                os.path.join(PARTIAL_DIR, file_name)
            )
        )
    ])
    #stop if none
    if not partial_files:
        print("no partial inx files")
        return
    
    iterators = []

    for file_name in partial_files:

        file_path = os.path.join(
            PARTIAL_DIR,
            file_name
        )
        try:
            with open(file_path, "r", encoding="utf-8") as partial_file:
                partial_data = json.load(partial_file)

            if not isinstance(partial_data, dict):
                print(f"skipping bad json struct")
                continue

            iterators.append(iter(sorted(partial_data.items())))

        except json.JSONDecodeError:
            print(f"error: coouldnt decode json {file_name}")

        except Exception as error:
            print(f"error:error read {file_name}: {error}")

        
    #heap
    #term, iterators, postings

    min_heap = []
    for iterator_index, iterator in enumerate(iterators):
        try:
            term, postings = next(iterator)
            
            heapq.heappush(min_heap, (term, iterator_index, postings))
        except StopIteration:
            continue

    final_index_path = os.path.join(
        FINAL_DIR, "merged_idx.json"
    )
    total_terms = 0
    total_posts = 0

    #merged idx

    with open(final_index_path, "w", encoding="utf-8") as final_file:
        final_file.write("{\n")
        first_entry = True
        while min_heap:
            current_term, iterator_index, postings = heapq.heappop(min_heap)
            merged_postings = list(postings)

            while min_heap and min_heap [0][0] == current_term:
                _, other_iterators_idx, other_postings = heapq.heappop(min_heap)

                merged_postings.extend(other_postings)

                try:
                    next_term, next_postings = next(
                        iterators[other_iterators_idx]
                    )
                    heapq.heappush(
                        min_heap, (
                            next_term, 
                            other_iterators_idx,
                            next_postings
                        )
                    )
                except StopIteration:
                    pass
            try:
                next_term, next_postings = next(
                    iterators[iterator_index]
                )
                heapq.heappush(
                        min_heap, (
                            next_term, 
                            iterator_index,
                            next_postings
                        )
                    )
            except StopIteration:
                pass

            #merged term into disk
            if not first_entry:
                final_file.write(",\n")

            final_file.write(f'  "{current_term}": ')

            json.dump(
                merged_postings,
                final_file
            )
            first_entry = False
            total_terms += 1
            total_posts += len(merged_postings)

        final_file.write("\n}")
    final_size_kb = round(os.path.getsize(final_index_path) / 1024, 2)

def save_doc_map(doc_map):
    if not isinstance(doc_map, dict):
        raise TypeError("error, doc map has to be a dict")

    output_path = os.path.join(
        FINAL_DIR,
        "doc_map.json"
    )
    cleaned_map = {}

    skip_entries = 0

    for doc_id, url in doc_map.iterms():

        if not isinstance(doc_id, int):
            skip_entries += 1
            continue

        if not isinstance(url, str):
            skip_entries += 1
            continue

        cleaned_map[str(doc_id)] = url

    with open(output_path, "w", encoding="utf-8") as output_file:

        json.dump(
            cleaned_map,
            output_file,
            indent=2
        )

    print(f"info: doc map -> {output_path}")

        



def clear_partial_indexes():

    removed_files = 0
    failed_removals = 0

    for file_name in os.listdir(PARTIAL_DIR):

        file_path = os.path.join(
            PARTIAL_DIR, file_name
        )

        if not os.path.isfile(file_path):
            continue

        try:
            os.remvoe(file_path)
            removed_files += 1

        except Exception:
            failed_removals += 1

        print("info: remove files: {removed_files}")
        print("info fail removals: {failed_removals}")
