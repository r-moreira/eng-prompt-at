import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

def dataframe_to_text_list(df):
    """Convert all columns of a dataframe to a list of text entries."""
    text_list = []
    for _, row in df.iterrows():
        text_entry = ' '.join(row.astype(str).values)
        text_list.append(text_entry)
    return text_list

def write_texts_to_file(texts, file_path):
    """Write a list of texts to a file."""
    with open(file_path, 'w') as f:
        for text in texts:
            f.write(text + '\n')

def read_texts_from_file(file_path):
    """Read texts from a file into a list of strings."""
    with open(file_path, 'r') as file:
        texts = file.readlines()
    return [text.strip() for text in texts]

def create_faiss_index(texts, model_name, index_file_path, cache_folder="../data/bertimbau/", device='cpu'):
    """Create a FAISS index from a list of texts."""
    
    model = SentenceTransformer(model_name, cache_folder=cache_folder, device=device)
    
    embeddings = model.encode(texts)
    embeddings = np.array(embeddings).astype('float32')
    
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    faiss.write_index(index, index_file_path)
    
def search_vector_storage(query, top_k=15):
    """
        Apenas para teste
    """
    
    try:
        model = SentenceTransformer(
            'neuralmind/bert-base-portuguese-cased',
            cache_folder="../data/bertimbau/", 
            device='cpu'
        )
        
        index = faiss.read_index('data/faiss_index.bin')
        text_data_list = read_texts_from_file('data/combined_texts.txt')

        query_embedding = model.encode([query])

        distances, indices = index.search(query_embedding, top_k)
        
        results = []
        for i in range(top_k):
            results.append(text_data_list[indices[0][i]])
            
        return "\n".join(results)
    except Exception as e:
        print(e)
        return None