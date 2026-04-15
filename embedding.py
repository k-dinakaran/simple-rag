import logging
import numpy as np
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class EmbeddingModel:
    """
    A lightweight embedding module that converts text chunks and user queries 
    into vector embeddings using the sentence-transformers library.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the EmbeddingModel and loads the specified sentence-transformer model.

        Args:
            model_name (str): The name of the model to load from Hugging Face.
        """
        self.model_name = model_name
        logger.info(f"Loading embedding model '{self.model_name}'...")
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Successfully loaded model '{self.model_name}'.")
        except Exception as e:
            logger.error(f"Failed to load model '{self.model_name}'. Error: {e}")
            raise e

    def embed_text(self, text: str) -> list[float]:
        """
        Converts a single text string into a vector embedding.

        Args:
            text (str): The input text to embed.

        Returns:
            list[float]: The vector embedding as a list of floats.

        Raises:
            TypeError: If the input text is not a string.
            ValueError: If the input text is empty or only whitespace.
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string.")
        
        text = text.strip()
        if not text:
            raise ValueError("Input text cannot be empty.")

        # SentenceTransformer.encode returns a numpy array by default
        embedding: np.ndarray = self.model.encode(text)
        return embedding.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Converts multiple text chunks into a list of vector embeddings.

        Args:
            texts (list[str]): A list of input text chunks to embed.

        Returns:
            list[list[float]]: A list containing vector embeddings for each document.

        Raises:
            TypeError: If the input is not a list.
            ValueError: If the input list is empty or contains invalid/empty strings.
        """
        if not isinstance(texts, list):
            raise TypeError("Input must be a list of strings.")
            
        if not texts:
            raise ValueError("Input documents list cannot be empty.")
            
        for t in texts:
            if not isinstance(t, str) or not t.strip():
                 raise ValueError("All elements in the input list must be non-empty strings.")

        embeddings: np.ndarray = self.model.encode(texts)
        logger.info(f"Successfully embedded {len(texts)} documents.")
        
        return [emb.tolist() for emb in embeddings]

    def embed_query(self, query: str) -> list[float]:
        """
        Converts a user query into a vector embedding.

        Args:
            query (str): The user query string.

        Returns:
            list[float]: The vector embedding of the query.

        Raises:
            TypeError: If the query is not a string.
            ValueError: If the query is empty or only whitespace.
        """
        if not isinstance(query, str):
            raise TypeError("Query must be a string.")
            
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty.")

        embedding: np.ndarray = self.model.encode(query)
        logger.info(f"Successfully embedded query: '{query}'")
        
        return embedding.tolist()

if __name__ == "__main__":
    # Example Usage Flow
    try:
        model = EmbeddingModel()

        chunks = ["This is the first text chunk.", "This is the second text chunk about leave policy."]
        embeddings = model.embed_documents(chunks)
        print(f"Generated {len(embeddings)} document embeddings. First embedding size: {len(embeddings[0])}")

        query_embedding = model.embed_query("What is leave policy?")
        print(f"Generated query embedding of size: {len(query_embedding)}")

    except Exception as e:
        logger.error(f"Error during example execution: {e}")
