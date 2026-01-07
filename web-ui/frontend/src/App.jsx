import { useState } from 'react';
import { Film, Github, ExternalLink } from 'lucide-react';
import GenerationForm from './components/GenerationForm';
import VideoCard from './components/VideoCard';
import StatsBar from './components/StatsBar';
import { useJobs } from './hooks/useApi';
import './index.css';

function App() {
  const { jobs, loading, generateVideo, deleteJob } = useJobs();
  const [generating, setGenerating] = useState(false);
  const [filter, setFilter] = useState('all');

  const handleGenerate = async (params) => {
    setGenerating(true);
    try {
      await generateVideo(params);
    } catch (error) {
      alert('Failed to start generation: ' + error.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleDelete = async (jobId) => {
    if (confirm('Delete this video?')) {
      try {
        await deleteJob(jobId);
      } catch (error) {
        alert('Failed to delete: ' + error.message);
      }
    }
  };

  const filteredJobs = jobs.filter(job => {
    if (filter === 'all') return true;
    return job.status === filter;
  });

  // Deduplicate by job_id (should never happen, but safety measure)
  const uniqueJobs = Array.from(new Map(jobs.map(j => [j.job_id, j])).values());
  const dedupFilteredJobs = uniqueJobs.filter(job => {
    if (filter === 'all') return true;
    return job.status === filter;
  });

  const filters = [
    { value: 'all', label: 'All', count: uniqueJobs.length },
    { value: 'completed', label: 'Completed', count: uniqueJobs.filter(j => j.status === 'completed').length },
    { value: 'processing', label: 'Processing', count: uniqueJobs.filter(j => j.status === 'processing').length },
    { value: 'queued', label: 'Queued', count: uniqueJobs.filter(j => j.status === 'queued').length },
    { value: 'failed', label: 'Failed', count: uniqueJobs.filter(j => j.status === 'failed').length }
  ];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-dark-border bg-dark-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl">
                <Film className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-500 to-purple-600 bg-clip-text text-transparent">
                  HunyuanVideo Studio
                </h1>
                <p className="text-sm text-gray-400">AI-Powered Video Generation</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/Tencent-Hunyuan/HunyuanVideo"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
              >
                <Github className="w-5 h-5" />
                <span className="hidden md:inline">GitHub</span>
              </a>
              <div className="px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
                <span className="flex items-center gap-2 text-sm text-green-400">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  Online
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Stats */}
        <StatsBar />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Generation Form - Left Sidebar */}
          <div className="lg:col-span-1">
            <GenerationForm onGenerate={handleGenerate} generating={generating} />
          </div>

          {/* Video Gallery - Main Content */}
          <div className="lg:col-span-2">
            {/* Filter Tabs */}
            <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
              {filters.map(f => (
                <button
                  key={f.value}
                  onClick={() => setFilter(f.value)}
                  className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-all ${
                    filter === f.value
                      ? 'bg-primary-600 text-white'
                      : 'bg-dark-hover text-gray-400 hover:text-white'
                  }`}
                >
                  {f.label}
                  {f.count > 0 && (
                    <span className="ml-2 px-2 py-0.5 bg-dark-card rounded-full text-xs">
                      {f.count}
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Video Grid */}
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="card skeleton h-96" />
                ))}
              </div>
            ) : filteredJobs.length === 0 ? (
              <div className="card text-center py-12">
                <Film className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">No videos yet</h3>
                <p className="text-gray-400 mb-6">
                  {filter === 'all'
                    ? 'Generate your first video to get started'
                    : `No ${filter} videos`}
                </p>
                {filter !== 'all' && (
                  <button
                    onClick={() => setFilter('all')}
                    className="btn-secondary"
                  >
                    Show All Videos
                  </button>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {dedupFilteredJobs.map(job => (
                  <VideoCard
                    key={job.job_id}
                    job={job}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-dark-border mt-16 py-8">
        <div className="container mx-auto px-4 text-center text-gray-400">
          <p className="text-sm">
            Powered by{' '}
            <a
              href="https://github.com/Tencent-Hunyuan/HunyuanVideo"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-500 hover:text-primary-400 inline-flex items-center gap-1"
            >
              HunyuanVideo
              <ExternalLink className="w-3 h-3" />
            </a>
            {' '}• 13B Parameter Text-to-Video Model
          </p>
          <p className="text-xs mt-2">
            GPU: NVIDIA H100 80GB • Cost: $0.29/video • Generation Time: ~5 minutes
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
