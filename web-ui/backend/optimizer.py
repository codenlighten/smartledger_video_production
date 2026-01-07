"""
Adaptive inference optimization for HunyuanVideo.

Analyzes prompts to determine optimal inference parameters:
- Step count (20-50 steps)
- Resolution recommendations
- Quality tier suggestions
"""
import re
from typing import Dict, Tuple
from enum import Enum


class ComplexityLevel(Enum):
    """Prompt complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class QualityTier(Enum):
    """Generation quality tiers."""
    PREVIEW = "preview"      # Fast preview: 270p, 15 steps, ~2 min
    STANDARD = "standard"    # Standard: 540p, 25 steps, ~5 min
    PREMIUM = "premium"      # Premium: 720p, 40 steps, ~10 min


def analyze_prompt_complexity(prompt: str) -> ComplexityLevel:
    """
    Analyze prompt to determine complexity level.
    
    Simple: Static scenes, minimal motion
    Moderate: Some motion, simple actions
    Complex: Multiple subjects, complex motion, effects
    """
    prompt_lower = prompt.lower()
    
    # Complexity indicators
    complex_keywords = [
        "action", "fighting", "running", "chase", "explosion",
        "particles", "effects", "transformation", "morphing",
        "multiple", "crowd", "many", "dynamic", "fast",
        "spinning", "rotating", "flying through"
    ]
    
    simple_keywords = [
        "still", "static", "portrait", "close-up", "sunset",
        "landscape", "simple", "minimal", "calm", "peaceful",
        "sitting", "standing", "looking"
    ]
    
    # Count indicators
    complex_count = sum(1 for keyword in complex_keywords if keyword in prompt_lower)
    simple_count = sum(1 for keyword in simple_keywords if keyword in prompt_lower)
    
    # Word count as complexity factor
    word_count = len(prompt.split())
    
    # Multiple subjects
    has_multiple_subjects = any(word in prompt_lower for word in ["and", "with", "multiple"])
    
    # Determine complexity
    if complex_count >= 2 or (complex_count >= 1 and has_multiple_subjects):
        return ComplexityLevel.COMPLEX
    elif simple_count >= 2 or word_count <= 5:
        return ComplexityLevel.SIMPLE
    else:
        return ComplexityLevel.MODERATE


def get_optimal_steps(
    complexity: ComplexityLevel,
    quality_tier: QualityTier = QualityTier.STANDARD
) -> int:
    """
    Determine optimal inference steps based on complexity and quality tier.
    
    Returns:
        Recommended number of inference steps
    """
    step_matrix = {
        QualityTier.PREVIEW: {
            ComplexityLevel.SIMPLE: 12,
            ComplexityLevel.MODERATE: 15,
            ComplexityLevel.COMPLEX: 18,
        },
        QualityTier.STANDARD: {
            ComplexityLevel.SIMPLE: 20,
            ComplexityLevel.MODERATE: 25,
            ComplexityLevel.COMPLEX: 30,
        },
        QualityTier.PREMIUM: {
            ComplexityLevel.SIMPLE: 35,
            ComplexityLevel.MODERATE: 40,
            ComplexityLevel.COMPLEX: 50,
        }
    }
    
    return step_matrix[quality_tier][complexity]


def get_optimal_resolution(quality_tier: QualityTier) -> Tuple[int, int]:
    """
    Get recommended resolution for quality tier.
    
    Returns:
        Tuple of (height, width)
    """
    resolution_map = {
        QualityTier.PREVIEW: (272, 480),   # ~270p
        QualityTier.STANDARD: (544, 960),  # 540p
        QualityTier.PREMIUM: (720, 1280),  # 720p
    }
    
    return resolution_map[quality_tier]


def estimate_generation_time(
    complexity: ComplexityLevel,
    quality_tier: QualityTier,
    video_length: int = 129
) -> float:
    """
    Estimate generation time in seconds.
    
    Args:
        complexity: Prompt complexity level
        quality_tier: Quality tier
        video_length: Number of frames
        
    Returns:
        Estimated time in seconds
    """
    # Base time per step (seconds) - calibrated from H100 performance
    base_time_per_step = {
        QualityTier.PREVIEW: 6,    # Fast
        QualityTier.STANDARD: 11,  # Medium
        QualityTier.PREMIUM: 14,   # Slow (higher res)
    }
    
    steps = get_optimal_steps(complexity, quality_tier)
    base_time = steps * base_time_per_step[quality_tier]
    
    # Frame length adjustment (minor)
    if video_length > 129:
        base_time *= (video_length / 129) * 1.1
    
    # Model loading overhead
    overhead = 30
    
    return base_time + overhead


def get_optimization_recommendations(prompt: str, user_tier: str = "standard") -> Dict:
    """
    Get comprehensive optimization recommendations for a prompt.
    
    Args:
        prompt: User's text prompt
        user_tier: Requested quality tier (preview/standard/premium)
        
    Returns:
        Dictionary with recommendations
    """
    # Parse quality tier
    try:
        quality_tier = QualityTier(user_tier.lower())
    except ValueError:
        quality_tier = QualityTier.STANDARD
    
    # Analyze complexity
    complexity = analyze_prompt_complexity(prompt)
    
    # Get optimal parameters
    steps = get_optimal_steps(complexity, quality_tier)
    height, width = get_optimal_resolution(quality_tier)
    estimated_time = estimate_generation_time(complexity, quality_tier)
    
    return {
        "complexity": complexity.value,
        "quality_tier": quality_tier.value,
        "recommended_steps": steps,
        "recommended_resolution": {
            "height": height,
            "width": width,
            "label": f"{height}p"
        },
        "estimated_time_seconds": int(estimated_time),
        "estimated_time_formatted": f"{int(estimated_time // 60)}m {int(estimated_time % 60)}s",
        "optimization_applied": True,
        "savings_vs_default": f"{int(((450 - estimated_time) / 450) * 100)}%"
    }


def should_use_cache(prompt: str) -> bool:
    """
    Determine if this prompt is a good candidate for caching.
    
    Common/repeated prompts benefit most from caching.
    """
    # Short, common prompts
    if len(prompt.split()) <= 10:
        return True
    
    # Contains common patterns
    common_patterns = ["a cat", "a dog", "sunset", "ocean", "city street"]
    if any(pattern in prompt.lower() for pattern in common_patterns):
        return True
    
    return False
