import json
import os
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Use HuggingFace embeddings for stability and offline use
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
persist_directory = "./chroma_db"

def load_data():
    with open("data/schemes_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def populate():
    schemes = load_data()
    documents = []
    for scheme in schemes:
        # Create a rich multilingual text representation for better RAG retrieval
        content = f"Scheme Name: {scheme['name']}\n"
        
        # Add multilingual names for cross-language search
        for lang_key in ['name_hi', 'name_ta', 'name_bn', 'name_mr']:
            if lang_key in scheme:
                content += f"Name ({lang_key}): {scheme[lang_key]}\n"
        
        content += f"Description: {scheme['description']}\n"
        content += f"Benefits: {scheme['benefits']}\n"
        content += f"Eligibility Criteria: {'; '.join(scheme['eligibility_criteria'])}\n"
        content += f"Required Documents: {', '.join(scheme['required_documents'])}\n"
        content += f"Application Process: {scheme['application_process']}\n"
        content += f"Target Persona: {scheme.get('persona', 'general')}\n"
        
        doc = Document(
            page_content=content,
            metadata={
                "id": scheme['id'],
                "name": scheme['name'],
                "persona": scheme.get('persona', 'general')
            }
        )
        documents.append(doc)
    
    print(f"Loaded {len(documents)} schemes.")
    
    # Store in ChromaDB (no explicit .persist() needed in newer versions)
    db = Chroma.from_documents(
        documents,
        embeddings,
        persist_directory=persist_directory
    )
    
    print(f"Database populated successfully at '{persist_directory}'.")
    print(f"Schemes indexed: {[s['id'] for s in schemes]}")

if __name__ == "__main__":
    populate()
