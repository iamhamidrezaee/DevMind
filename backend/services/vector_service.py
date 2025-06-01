"""
Vector Service for DevMind
Handles embeddings and vector similarity search
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class VectorService:
    """Service for handling vector embeddings and similarity search"""
    
    def __init__(self):
        self.model = None
        self.model_name = "all-MiniLM-L6-v2"  # 384 dimensions, fast and good quality
        
    async def initialize(self):
        """Initialize the embedding model"""
        try:
            # Load model in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, 
                lambda: SentenceTransformer(self.model_name)
            )
            logger.info(f"✅ Vector service initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize vector service: {e}")
            # For demo purposes, we'll continue without embeddings
            self.model = None

    async def embed_text(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text"""
        if not self.model:
            logger.warning("Vector model not initialized, skipping embedding")
            return None
        
        try:
            # Run embedding in thread to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.model.encode(text, convert_to_tensor=False)
            )
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    async def embed_texts(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts"""
        if not self.model:
            return [None] * len(texts)
        
        try:
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(texts, convert_to_tensor=False)
            )
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return [None] * len(texts)

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0

    async def search_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[Dict[str, Any]],
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings"""
        if not query_embedding:
            return []
        
        # Calculate similarities
        results = []
        for candidate in candidate_embeddings:
            if candidate.get("embedding"):
                similarity = self.calculate_similarity(
                    query_embedding,
                    candidate["embedding"]
                )
                
                if similarity >= threshold:
                    candidate_with_score = candidate.copy()
                    candidate_with_score["similarity_score"] = similarity
                    results.append(candidate_with_score)
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:limit]

    async def cleanup(self):
        """Cleanup resources"""
        self.model = None
        logger.info("✅ Vector service cleaned up")