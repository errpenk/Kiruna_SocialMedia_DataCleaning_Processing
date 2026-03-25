#Massive semantic search
import pandas as pd
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  # Multilingual model

df = pd.read_excel("EXAMPLE.xlsx")

# Batch encoding (batch_size controls memory usage)
embeddings = model.encode(
    df["content"].tolist(),
    batch_size=64,
    show_progress_bar=True,
    convert_to_tensor=True
)

print(f"Embedding shape: {embeddings.shape}")

# Save
import numpy as np
np.save("embeddings.npy", embeddings.cpu().numpy())
