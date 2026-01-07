import { Zap, Brain, Clock, TrendingUp } from 'lucide-react';

export default function OptimizationBadge({ optimization }) {
  if (!optimization) return null;

  const { cache_hit, complexity, final_steps, estimated_time, quality_tier } = optimization;

  const complexityColors = {
    simple: 'text-green-400',
    moderate: 'text-blue-400',
    complex: 'text-yellow-400',
    very_complex: 'text-red-400'
  };

  const complexityIcons = {
    simple: '🟢',
    moderate: '🔵',
    complex: '🟡',
    very_complex: '🔴'
  };

  return (
    <div className="flex flex-wrap gap-2 mt-2">
      {/* Cache Hit */}
      {cache_hit && (
        <div className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/10 border border-green-500/20 rounded text-xs text-green-400">
          <Zap className="w-3 h-3" />
          Cache Hit
        </div>
      )}

      {/* Complexity */}
      {complexity && (
        <div className={`inline-flex items-center gap-1 px-2 py-1 bg-dark-hover border border-dark-border rounded text-xs ${complexityColors[complexity]}`}>
          <Brain className="w-3 h-3" />
          {complexityIcons[complexity]} {complexity}
        </div>
      )}

      {/* Steps */}
      {final_steps && (
        <div className="inline-flex items-center gap-1 px-2 py-1 bg-dark-hover border border-dark-border rounded text-xs text-gray-400">
          <TrendingUp className="w-3 h-3" />
          {final_steps} steps
        </div>
      )}

      {/* Estimated Time */}
      {estimated_time && (
        <div className="inline-flex items-center gap-1 px-2 py-1 bg-dark-hover border border-dark-border rounded text-xs text-gray-400">
          <Clock className="w-3 h-3" />
          ~{estimated_time}min
        </div>
      )}

      {/* Quality Tier */}
      {quality_tier && quality_tier !== 'auto' && (
        <div className="inline-flex items-center gap-1 px-2 py-1 bg-purple-500/10 border border-purple-500/20 rounded text-xs text-purple-400">
          {quality_tier === 'preview' ? '⚡' : quality_tier === 'premium' ? '💎' : '⚖️'}
          {quality_tier}
        </div>
      )}
    </div>
  );
}
