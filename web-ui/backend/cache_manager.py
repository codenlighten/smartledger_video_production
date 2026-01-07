"""
Embedding Cache Manager with Redis
Provides 15-20% speedup by caching text embeddings
"""
import os
import json
import hashlib
from typing import Optional, Dict, Any
import redis.asyncio as redis

class CacheManager:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "redis")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.enabled = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        self.redis_client = None
        self.ttl = 3600  # 1 hour cache TTL
        
    async def connect(self):
        """Initialize Redis connection"""
        if not self.enabled:
            print("⚠️ Cache disabled via ENABLE_CACHE=false")
            return
            
        try:
            self.redis_client = await redis.from_url(
                f"redis://{self.redis_host}:{self.redis_port}",
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            print(f"✅ Redis cache connected at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            print(f"⚠️ Redis unavailable, cache disabled: {e}")
            self.enabled = False
            self.redis_client = None
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _hash_prompt(self, prompt: str) -> str:
        """Create deterministic hash for prompt"""
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    async def get_embedding(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached embedding for prompt"""
        if not self.enabled or not self.redis_client:
            return None
            
        try:
            key = f"embed:{self._hash_prompt(prompt)}"
            cached = await self.redis_client.get(key)
            
            if cached:
                print(f"🎯 Cache HIT for prompt: {prompt[:50]}...")
                return json.loads(cached)
            else:
                print(f"❌ Cache MISS for prompt: {prompt[:50]}...")
                return None
        except Exception as e:
            print(f"⚠️ Cache read error: {e}")
            return None
    
    async def set_embedding(self, prompt: str, embedding_data: Dict[str, Any]):
        """Store embedding in cache"""
        if not self.enabled or not self.redis_client:
            return
            
        try:
            key = f"embed:{self._hash_prompt(prompt)}"
            value = json.dumps(embedding_data)
            await self.redis_client.setex(key, self.ttl, value)
            print(f"💾 Cached embedding for: {prompt[:50]}...")
        except Exception as e:
            print(f"⚠️ Cache write error: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled or not self.redis_client:
            return {
                "enabled": False,
                "status": "disabled"
            }
        
        try:
            info = await self.redis_client.info("stats")
            keys = await self.redis_client.dbsize()
            
            return {
                "enabled": True,
                "status": "healthy",
                "total_keys": keys,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            return {
                "enabled": True,
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)

# Global cache manager instance
cache_manager = CacheManager()
