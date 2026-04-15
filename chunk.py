import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class SemanticChunker:
    """
    A lightweight semantic text chunker that splits text based on paragraphs 
    and meaning instead of fixed character splitting.
    """

    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        """
        Initializes the SemanticChunker.

        Args:
            chunk_size (int): Maximum character size for a chunk.
            chunk_overlap (int): Target number of overlapping characters between chunks.
        """
        # Validation
        if chunk_size <= 0:
            raise ValueError("chunk_size must be strictly greater than 0")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        """
        Splits the given text into semantic chunks by combining paragraphs.

        Args:
            text (str): The input text to be chunked.

        Returns:
            list[str]: A list of generated text chunks.

        Raises:
            ValueError: If the text is empty or only whitespace.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        text = text.strip()
        
        # 1. Split text into paragraphs based on double and single newlines
        paragraphs = []
        # split first by double newline
        for block in re.split(r'\n\n+', text):
            block = block.strip()
            if not block:
                continue
            
            # If the block itself exceeds chunk_size, we step down to single newline splitting
            if len(block) > self.chunk_size:
                sub_blocks = re.split(r'\n+', block)
                for sb in sub_blocks:
                    sb = sb.strip()
                    if sb:
                        paragraphs.append(sb)
            else:
                paragraphs.append(block)

        if not paragraphs:
            return []

        chunks = []
        current_chunk = []
        current_len = 0

        # 2. Merge paragraphs until chunk_size limit reached
        for para in paragraphs:
            para_len = len(para)
            
            # Plus one account for the newline character connecting the paragraphs
            separator_len = 1 if current_chunk else 0

            if current_len + para_len + separator_len > self.chunk_size and current_chunk:
                # Add current block to chunks as we've hit the limit
                chunk_text = "\n".join(current_chunk)
                chunks.append(chunk_text)

                # 4. Apply overlap between chunks for the next chunk
                overlap_len = 0
                overlap_chunk = []
                
                # Try to fit the last paragraphs strictly within the overlap limit
                for p in reversed(current_chunk):
                    p_sep_len = 1 if overlap_chunk else 0
                    if overlap_len + len(p) + p_sep_len <= self.chunk_overlap:
                        overlap_chunk.insert(0, p)
                        overlap_len += len(p) + p_sep_len
                    else:
                        break
                        
                current_chunk = overlap_chunk
                current_len = overlap_len

            current_chunk.append(para)
            current_len += para_len + (1 if len(current_chunk) > 1 else 0)

        # Append any remaining paragraphs
        if current_chunk:
            chunk_text = "\n".join(current_chunk)
            if chunk_text.strip():
                 chunks.append(chunk_text)

        # 5. Remove empty chunks (handled implicitly above)

        # 6. Logging
        logger.info(f"Chunks created: {len(chunks)}")
        logger.info(f"Configuration - Chunk size: {self.chunk_size}, Overlap: {self.chunk_overlap}")

        return chunks

if __name__ == "__main__":
    # Example Usage Flow
    try:
        sample_text = """Paragraph 1: Background information about the subject. It is quite interesting and informative.

Paragraph 2: Detailed explanation of the methods used. We ensure our chunks are well-formed and semantic.

Paragraph 3: Conclusion and future work, finalizing the document structure."""

        chunker = SemanticChunker(chunk_size=150, chunk_overlap=80)
        chunks = chunker.split_text(sample_text)
        
        print(f"Total chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks, 1):
            print(f"\n--- Chunk {i} ---")
            print(chunk)
            
    except Exception as e:
        logger.error(f"Error: {e}")
