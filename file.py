if os.path.exists(retriever_file) and not refresh:
    with open(retriever_file, 'rb') as f:
        state = pickle.load(f)
    
    # Extract data from the state dictionary, ensuring default values if keys are missing
    documents = state.get('documents', [])  # Ensure documents is initialized as an empty list
    avgdl = state.get('avgdl', 0)          # Average document length, default to 0
    N = state.get('N', 0)                   # Total number of documents, default to 0
    term_document_freq = state.get('term_document_freq', {})  # Term document frequency, default to empty dict

else:
    # If the retriever file doesn't exist or refresh is True, initialize empty structures
    documents = []
    term_document_freq = {}

    filename = "/docs/output/bail.md"
    with open(filename, 'r') as file:
        content = file.read()
        sections = split_into_sections(content)
        for section_title, section_content in sections:
            section_metadata = { 'section': section_title}
            chunks = split_into_chunks(section_title, section_content, section_metadata)
            for chunk in chunks:
                clean_terms = clean_text(chunk.chunk_content).split()
                unique_terms = set(clean_terms)
                for term in unique_terms:
                    term_document_freq[term] = term_document_freq.get(term, 0) + 1