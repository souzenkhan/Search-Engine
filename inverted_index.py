from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Posting:
    doc_id: int
    tf: int
    important_tf: int


class InvertedIndex:
    def __init__(self):
        self.index: Dict[str, List[Posting]] = {}
        self.doc_id_map: Dict[int, str] = {}  # doc_id -> url
        self._next_id: int = 0

    def _assign_doc_id(self, url: str) -> int:
        doc_id = self._next_id
        self.doc_id_map[doc_id] = url
        self._next_id += 1
        return doc_id

    def add_document(self, url: str, tf_map: Dict[str, int], imp_map: Dict[str, int]) -> None:
        doc_id = self._assign_doc_id(url)
        for term, tf in tf_map.items():
            posting = Posting(doc_id=doc_id, tf=tf, important_tf=imp_map.get(term, 0))
            self.index.setdefault(term, []).append(posting)

    def get_postings(self, term: str) -> List[Posting]:
        return self.index.get(term, [])
