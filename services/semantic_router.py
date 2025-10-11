
# This service handles the first stage of orchestration: fast, semantic filtering.
# It creates vector embeddings for all tool descriptions and uses a vector store
# to find the most relevant tools for a given user query.

import logging
from typing import List
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from tools.tool_definitions import Tool
from utils.config import settings

logger = logging.getLogger(__name__)

class SemanticRouter:
    """
    Selects the most relevant tools from a list based on semantic similarity
    to the user's query.
    """
    def __init__(self, tools: List[Tool]):
        self.tools = tools
        self.tool_descriptions = [f"{tool.name}: {tool.description}" for tool in self.tools]
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.index = None # FAISS index

    async def initialize(self):
        """
        Builds the FAISS vector index from the tool descriptions.
        This is an async method to allow for potentially slow I/O or model loading
        without blocking the event loop on startup.
        """
        logger.info("Initializing Semantic Router and building vector index...")
        try:
            embeddings = self.model.encode(self.tool_descriptions, convert_to_tensor=False)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(np.array(embeddings, dtype=np.float32))
            logger.info(f"FAISS index built successfully with {self.index.ntotal} vectors.")
        except Exception as e:
            logger.error(f"Failed to initialize Semantic Router: {e}", exc_info=True)
            raise

    async def select_candidate_tools(self, query: str, top_k: int = 3) -> List[Tool]:
        """
        Finds the top_k most relevant tools for a given query.
        """
        if self.index is None:
            raise RuntimeError("SemanticRouter is not initialized. Call initialize() first.")

        try:
            query_embedding = self.model.encode([query])
            query_embedding_np = np.array(query_embedding, dtype=np.float32)

            # Search the index
            distances, indices = self.index.search(query_embedding_np, k=min(top_k, len(self.tools)))

            # Retrieve the top tools
            candidate_tools = [self.tools[i] for i in indices[0]]
            return candidate_tools
        except Exception as e:
            logger.error(f"Error during candidate tool selection: {e}", exc_info=True)
            return []
