"""
Caching layer for HunyuanVideo generation optimization.

Features:
- Text embedding cache (LLaVA + CLIP)
- Latent state caching for variations
- Motion template library
"""
import hashlib
import json
import pickle
from pathlib import Path
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)


class GenerationCache:
    """Cache for expensive generation operations."""
    
    def __init__(self, cache_dir: str = "/opt/hunyuan-video/cache"):
        self.cache_dir = Path(cache_dir)
        self.embeddings_dir = self.cache_dir / "embeddings"
        self.latents_dir = self.cache_dir / "latents"
        
        # Create cache directories
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        self.latents_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Cache initialized at {self.cache_dir}")
    
    def _get_prompt_hash(self, prompt: str) -> str:
        """Generate unique hash for a prompt."""
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    def _get_cache_key(self, prompt: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from prompt and parameters."""
        key_data = {"prompt": prompt}
        if params:
            # Only cache based on parameters that affect embeddings
            relevant_params = {
                k: v for k, v in params.items() 
                if k in ["cfg_scale", "flow_reverse"]
            }
            key_data.update(relevant_params)
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]
    
    def get_embedding(self, prompt: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Retrieve cached text embeddings if available."""
        cache_key = self._get_cache_key(prompt, params)
        cache_file = self.embeddings_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    logger.info(f"Cache HIT for prompt: {prompt[:50]}...")
                    return data
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                return None
        
        logger.info(f"Cache MISS for prompt: {prompt[:50]}...")
        return None
    
    def set_embedding(self, prompt: str, embedding_data: Any, params: Optional[Dict] = None):
        """Store text embeddings in cache."""
        cache_key = self._get_cache_key(prompt, params)
        cache_file = self.embeddings_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding_data, f)
            logger.info(f"Cached embeddings for: {prompt[:50]}...")
        except Exception as e:
            logger.warning(f"Failed to cache embeddings: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "embeddings_cached": len(list(self.embeddings_dir.glob("*.pkl"))),
            "latents_cached": len(list(self.latents_dir.glob("*.pkl"))),
            "total_size_mb": sum(
                f.stat().st_size for f in self.cache_dir.rglob("*.pkl")
            ) // (1024 * 1024)
        }
    
    def clear(self):
        """Clear all caches."""
        for cache_file in self.embeddings_dir.glob("*.pkl"):
            cache_file.unlink()
        for cache_file in self.latents_dir.glob("*.pkl"):
            cache_file.unlink()
        logger.info("Cache cleared")


# Global cache instance
_cache_instance = None


def get_cache() -> GenerationCache:
    """Get or create global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = GenerationCache()
    return _cache_instance
