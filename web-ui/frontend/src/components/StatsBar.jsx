import { Activity, Video, Clock, TrendingUp, Zap, Brain } from 'lucide-react';
import { useStats } from '../hooks/useApi';

export default function StatsBar() {
  const stats = useStats();

  if (!stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-8">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="card skeleton h-24" />
        ))}
      </div>
    );
  }

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const optimization = stats.optimization || {};

  const statCards = [
    {
      icon: Video,
      label: 'Total Generated',
      value: stats.completed,
      subtext: `${stats.total_generations} total`,
      color: 'text-primary-500',
      bgColor: 'bg-primary-500/10'
    },
    {
      icon: Activity,
      label: 'In Progress',
      value: stats.in_progress + stats.queued,
      subtext: stats.in_progress > 0 ? 'Active now' : 'Idle',
      color: 'text-green-500',
      bgColor: 'bg-green-500/10'
    },
    {
      icon: Clock,
      label: 'Avg Duration',
      value: formatTime(stats.avg_duration),
      subtext: 'per video',
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10'
    },
    {
      icon: TrendingUp,
      label: 'Total GPU Time',
      value: formatTime(stats.total_duration),
      subtext: `$${(stats.total_duration / 3600 * 3.39).toFixed(2)} cost`,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10'
    },
    {
      icon: Zap,
      label: 'Cache Hit Rate',
      value: optimization.cache_enabled ? `${optimization.cache_hit_rate || 0}%` : 'N/A',
      subtext: optimization.cache_enabled ? `${optimization.cache_hits || 0} hits` : 'Disabled',
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10'
    },
    {
      icon: Brain,
      label: 'Avg Steps',
      value: optimization.avg_steps ? Math.round(optimization.avg_steps) : '--',
      subtext: optimization.adaptive_enabled ? 'Adaptive' : 'Fixed',
      color: 'text-cyan-500',
      bgColor: 'bg-cyan-500/10'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
      {statCards.map((stat, idx) => (
        <div key={idx} className="card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">{stat.label}</p>
              <p className="text-3xl font-bold mb-1">{stat.value}</p>
              <p className="text-xs text-gray-500">{stat.subtext}</p>
            </div>
            <div className={`p-3 rounded-lg ${stat.bgColor}`}>
              <stat.icon className={`w-6 h-6 ${stat.color}`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
