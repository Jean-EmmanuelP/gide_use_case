from smolagents import Tool
import os
import pickle
import string
from collections import Counter
import math
from itertools import groupby
import nltk

class Document:
    def __init__(self, chunk_content, metadata):
        self.chunk_content = chunk_content
        self.metadata = metadata
        self.clean_terms = self.precompute_clean_terms()
        self.term_freq = self.precompute_term_freq()
        self.doc_len = len(self.clean_terms)

    def precompute_clean_terms(self):
        return self.clean_text(self.chunk_content).split()

    def precompute_term_freq(self):
        return Counter(self.clean_terms)

    @staticmethod
    def clean_text(text):
        text = text.lower()
        text = text.translate(str.maketrans('','', string.punctuation))
        return text

class BM25RetrieverTool(Tool):
    name = "bm25_retriever"
    description = "A tool that retrieves the most relevant part of a document"
    input = {
        "query": {
            "type": "string",
            "description": "The search query to find relevant document sections and snippets."
        },
        "num_snippets": {
            "type": "integer",
            "description": "The number of relevant snippets to return",
            "default": 5,
            "nullable": True
        }
    }

    output_type = "string"

    def __init__(self, output_dir='docs/output', retriever_file='bm25_retriever.pkl'):
        super().__init__()
        self.output_dir = output_dir
        self.retriever_file = retriever_file
        self.documents = []
        self.avgdl = 0
        self.N = 0
        self.term_document_freq = {}
        self.k1 = 1.5
        self.b = 0.75
        self.is_initialized = False
        self.load_retrieve_state()
        self.is_initialized = True

    def load_retriever_state(self):
        if os.path.exists(self.retriever_file):
            with open(self.retriever_file, 'rb') as f:
                state = pickle.load(f)
                self.documents = state.get('documents', [])
                self.avgdl = state.get('avgdl', 0)
                self.N = state.get('N', 0)
                self.term_document_freq = state.get('term_document_freq', {})

    def forward(self, query: str, num_snippets: int = 5):
        num_snippets = min(num_snippets, 5)
        if not query:
            return ""
        results = self.bm25_score(query, self.documents)[:num_snippets]
        results.sort(key=lambda doc: doc[0].metadata['filename'])
        grouped_results = groupby(results, key=lambda doc: doc[0].metadata['filename'])
        
        output = []
        for doc_name, group in grouped_results:
            output.append(f"========== {doc_name} ==========")
            toc_file_path = os.path.join(self.output_dir, doc_name.rsplit('.', 1)[0] + '_toc.md')
            
            if os.path.exists(toc_file_path):
                with open(toc_file_path, 'r') as toc_file:
                    toc_content = toc_file.read()
                    output.append("Table of Contents:")
                    output.append(toc_content)
                    output.append("\n------\n")
            
            for doc, score in group:
                section_title = doc.metadata.get('section', 'Unknown Section')
                output.append(f"Section: {section_title}")
                snippet_content = '\n'.join(doc.chunk_content.split('\n')[3:])
                output.append(f"\nRelevant Snippet:\n{snippet_content}\nScore: {score:.1f}")
                output.append("\n------\n")
        
        output.append("\n==========\n")
        return "\n".join(output)

    def bm25_score(self, query, documents):
        query_terms = self.clean_text(query).split()
        doc_scores = []

        for doc in documents:
            score = 0
            for term in query_terms:
                if term in doc.term_freq:
                    # Use precomputed document frequency
                    df = self.term_document_freq.get(term, 1)  # Default to 1 to avoid division by zero
                    idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
                    tf = doc.term_freq[term]
                    score += idf * ((tf * (self.k1 + 1)) / 
                                    (tf + self.k1 * (1 - self.b + self.b * (doc.doc_len / self.avgdl))))
            doc_scores.append((doc, score))

        return sorted(doc_scores, key=lambda x: x[1], reverse=True)

    @staticmethod
    def clean_text(text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

#example usage
bm25_tool = BM25RetrieverTool()
results = bm25_tool.forward("Quel est le nom du bailleur ?")
print (results)