#imports

import os
import time

from collections import Counter
from parser import parse_document
from tokenizer import (
    tokenize, stem_tokens
)

from inverted_index import InvertedIndex

from disk_writer import (
    write_partial_index,
    merge_partial_idxs,
    save_doc_map,
    clear_partial_indexes #are we using this?
)

#dataset folder
DEV_FOLDER = "DEV"

#we can change later
#maybe 1000 or 5000, lets see
#how many doc to process before flush
FLUSH_THRESHOLD = 3000

def build_index():
    #go throw dev dataset, parse, tokenize, freq maps, posting to inverted index, flush partials to disk, merge partials, save doc map
    #runtime tracking
    start_time = time.time()

    #in-mem inverted index
    inverted_index = InvertedIndex()

    #partial idx counter
    partial_num = 0
    
    #total doc processes
    docs_processed = 0

    skip_files = 0
    failed_files = 0

    print("info: start index ..")

    #go through dataset
    for root, dirs, files in os.walk(DEV_FOLDER):
        for file_name in sorted(files):
            file_path = os.path.join(
                root, file_name
            )
            try:
                #parse
                parsed_doc = parse_document(file_path)

                if not parsed_doc:
                    skip_files += 1
                    continue

                #skip empty txt pg
                if not parsed_doc["text"].strip():
                    skip_files += 1
                    continue

                tokens = tokenize(parsed_doc["text"])

                stemmed_tokens = stem_tokens(tokens)

                tf_map = Counter(stemmed_tokens)

                important_tokens = tokenize(parsed_doc["important_text"])

                important_stemmed = stem_tokens(important_tokens)

                important_tf_map = Counter(important_stemmed)

                #add doc to inverted idx
                inverted_index.add_document(
                    parsed_doc["url"], tf_map, important_tf_map
                )
                docs_processed += 1

                #updates
                if docs_processed % 100 == 0:
                    print(
                        f"info: docs processed: {docs_processed}"
                    )
                
                #flush to disk

                if docs_processed % FLUSH_THRESHOLD == 0:
                    print(
                        f"info: flush partial index  #{partial_num}"
                    )
                    write_partial_index(
                        inverted_index.index,
                        partial_num
                    )

                    inverted_index.index.clear()

                    partial_num += 1

            except Exception as error:

                failed_files += 1

                print(
                    f"error: processing fail {file_path}: {error}"
                )

    #write data
    if inverted_index.index:
        print(
            f"info: writing partial final index #{partial_num}"

        )

        write_partial_index(
            inverted_index.index, partial_num
        )

    #merge partials
    print("info: merge partial idxs")

    merge_partial_idxs()

    #save doc map
    print("info: save doc map")

    save_doc_map(inverted_index.doc_id_map)

    elapsed_time = round(time.time() - start_time, 2)
    #stats

    print("info: index process done")

    print(f"info: total runtime: {elapsed_time} secs")

    print(f"info: docs indexed: {docs_processed}")

    print(f"info: skipped files: {skip_files}")

    print(f"info: failed files: {failed_files}")

#run
if __name__ == "__main__":
    build_index()    