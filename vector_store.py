import logging
import uuid

import chromadb

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class VectorStore:
    """
    A lightweight vector store module utilizing ChromaDB to manage embeddings
    and execute semantic similarity searches.
    """

    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "rag_documents"):
        """
        Initializes the ChromaDB client and creates or resolves the targeted collection.

        Args:
            persist_directory (str): The persistent directory map for the database.
            collection_name (str): The designated name of the vector collection.
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            logger.info(f"Initialized ChromaDB instance at '{self.persist_directory}'. Collection: '{self.collection_name}'.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client or collection: {e}")
            raise e

    def add_embeddings(self, texts: list[str], embeddings: list[list[float]]) -> None:
        """
        Adds text chunks and their respective embeddings directly to the ChromaDB collection.

        Args:
            texts (list[str]): The plain text chunks to be archived.
            embeddings (list[list[float]]): The equivalent 1:1 vector embeddings.

        Raises:
            TypeError: If input signatures are disjointed and not lists.
            ValueError: If item iterations or lengths conflict.
        """
        if type(texts) is not list or type(embeddings) is not list:
            raise TypeError("Both texts and embeddings structures must be standard lists.")
            
        if not texts or not embeddings:
            raise ValueError("The provided texts and embeddings lists cannot be empty structures.")

        if len(texts) != len(embeddings):
            raise ValueError(f"Input mismatch: Counted {len(texts)} document chunks against {len(embeddings)} corresponding embeddings.")

        # Generate completely unique string UUIDs for every inserted chunk as obliged
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                ids=ids
            )
            logger.info(f"Successfully processed and added {len(texts)} embeddings into the collection.")
        except Exception as e:
            logger.error(f"Crash failure while attempting to build and append array to ChromaDB: {e}")
            raise e

    def similarity_search(self, query_embedding: list[float], top_k: int = 3) -> list[str]:
        """
        Executes a localized dense semantic similarity search against the DB.

        Args:
            query_embedding (list[float]): Formatted float arrays identifying the targeted query.
            top_k (int): Number denoting precision cap return limits.

        Returns:
            list[str]: Array list exposing only the most mathematically contiguous matching text chunks.

        Raises:
            ValueError: On formatting, argument checks, or parameter failure exceptions.
            RuntimeError: If query operates against a currently un-persisted or empty data store.
        """
        if not isinstance(query_embedding, list) or len(query_embedding) == 0:
            raise ValueError("Query embedding must strictly follow format as a populated list of floats representing a vector array.")

        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError(f"Target count limit top_k={top_k} is inherently illegal; specify a positive integer index.")

        current_total = self.count()
        if current_total == 0:
            raise RuntimeError("Unable to complete similarity query: The target Vector Store represents an empty graph mapping.")

        # Safeguard limit against data structure size overflow exceptions
        if top_k > current_total:
            logger.warning(f"Constricting dynamic top_k scope to mapping ceiling limit ({current_total}).")
            top_k = current_total

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            # Reformat to only target explicit document text responses 
            matched_documents = results.get("documents", [])[0] if results.get("documents") else []
            
            logger.info(f"Similarity search performed successfully. Retrieved {len(matched_documents)} result chunk(s).")
            return matched_documents
            
        except Exception as e:
            logger.error(f"Internal calculation or matrix processing errors isolated during standard semantic mapping check: {e}")
            raise e

    def delete_collection(self) -> None:
        """
        Deletes the ChromaDB storage cache and active graph mapping. 
        Extremely useful for iteration cycles, automated teardowns, and unit pipeline testing.
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"The targeted mapping collection '{self.collection_name}' has been definitively erased.")
            
            # Immediately re-establish safe reference state formatting mappings to prevent null pointer calls
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
        except ValueError:
             logger.warning(f"Could not cleanly purge and reset '{self.collection_name}'. Map may exhibit non-existent signatures.")
        except Exception as e:
            logger.error(f"System crash during core destruction sequences: {e}")
            raise e

    def count(self) -> int:
        """
        Gets the absolute structural quantity of node entities held physically or in cache layout.

        Returns:
            int: The positive number item index block.
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Metadata calculation mismatch exceptions prevented index reading: {e}")
            return 0


if __name__ == "__main__":
    # Example testing sequences to confirm structural dependencies and logic maps
    try:
        store = VectorStore()
        
        # Test teardown function to prove persistent states refresh
        store.delete_collection()

        # Hardcode small dummy vector space chunks for runtime tests
        texts = [
            "We cover employee time off logic.", 
            "Neural matrices form dynamic spatial awareness nodes."
        ]
        embeddings = [
            [0.15, 0.22, 0.17], 
            [0.85, 0.90, -0.65]
        ]
        
        store.add_embeddings(texts=texts, embeddings=embeddings)
        print(f"State Graph - Internal Index Validations: {store.count()}")

        # Target Query
        query_val = [0.16, 0.23, 0.16]
        
        results = store.similarity_search(query_embedding=query_val, top_k=1)
        print(f"\nMatrix Processing Match Execution:")
        for idx, rank_result in enumerate(results, 1):
             print(f"Top [{idx}] - {rank_result}")
        
    except Exception as e:
        logger.error(f"Global exceptions caught during execution runs. Check dependencies or signatures: {e}")
