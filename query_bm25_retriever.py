import os
import sys
import pickle
import re
from itertools import groupby  # Correction orthographique si besoin
import string
from collections import Counter
import math
import nltk
from typing import Dict, List, Tuple

# Définir le répertoire contenant les fichiers Markdown
output_dir = 'docs/output'

# Définir le fichier pour sauvegarder l'état du retriever
retriever_file = 'bm25_retriever.pkl'

# Flag pour forcer la régénération de l'état du retriever (mettre True pour actualiser)
refresh = False

# Taille maximale d'un chunk (en nombre de caractères)
CHUNK_SIZE = 2000

# Fonction pour découper le contenu en sections
# NOTE : Cette fonction dépend de votre logique de TOC et n'est pas finalisée ici.
def split_into_sections(content):
    # TODO: Implémenter le découpage en sections basé sur votre TOC.
    # Pour l'instant, on retourne tout le contenu comme une seule section.
    return [("Titre Unique", content)]

# Fonction pour découper une section en chunks en respectant les limites de taille et les bornes de phrase
def split_into_chunks(section, metadata):
    section_title, section_content = section
    sentences = nltk.sent_tokenize(section_content)
    chunks = []
    current_chunk = []
    current_length = 0
    for sentence in sentences:
        if current_length + len(sentence) > CHUNK_SIZE:
            chunk_content = f"Document: {metadata['filename']}\nSection: {section_title}\nSnippet: {' '.join(current_chunk)}"
            chunks.append(Document(chunk_content, metadata=metadata))
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += len(sentence)
    if current_chunk:
        chunk_content = f"Document: {metadata['filename']}\nSection: {section_title}\nSnippet: {' '.join(current_chunk)}"
        chunks.append(Document(chunk_content, metadata=metadata))
    return chunks

# Fonction basique de nettoyage du texte
def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

# Classe représentant un document (ou un chunk) avec ses métadonnées
class Document:
    def __init__(self, chunk_content, metadata):
        self.chunk_content = chunk_content
        self.metadata = metadata
        self.clean_terms = self.precompute_clean_terms()
        self.term_document_freq = self.precompute_term_freq()
        
    def precompute_clean_terms(self):
        return clean_text(self.chunk_content).split()
    
    def precompute_term_freq(self):
        return Counter(self.clean_terms)

# Chargement de l'état du retriever s'il existe et si on ne force pas la régénération
if os.path.exists(retriever_file) and not refresh:
    with open(retriever_file, 'rb') as f:
        state = pickle.load(f)
        N = state.get('N', 0)
        term_document_freq = state.get('term_document_freq', {})
        documents = state.get('documents', [])
else:
    term_document_freq = {}
    N = 0  # Nombre total de chunks traités
    documents = []  # Liste de tous les chunks (documents)
    file_path = os.path.join(output_dir, 'Bail Bureau.md')
    metadata = {'filename': os.path.basename(file_path)}
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        sections = split_into_sections(content)
        for section in sections:
            section_title, section_content = section
            # Mettre à jour les métadonnées avec le titre de la section
            section_metadata = metadata.copy()
            section_metadata['section'] = section_title
            chunks = split_into_chunks(section, section_metadata)
            N += len(chunks)
            documents.extend(chunks)
            # Calcul de la fréquence des termes pour chaque chunk
            for chunk in chunks:
                clean_terms = clean_text(chunk.chunk_content).split()
                unique_terms = set(clean_terms)
                for term in unique_terms:
                    term_document_freq[term] = term_document_freq.get(term, 0) + 1
                    
    # Création de l'état du retriever et sauvegarde dans le fichier pickle
    state = {'N': N, 'term_document_freq': term_document_freq, 'documents': documents}
    with open(retriever_file, 'wb') as f:
        pickle.dump(state, f)
