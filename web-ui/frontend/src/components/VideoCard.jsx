import { useState } from 'react';
import { Play, Download, Trash2, Clock, CheckCircle, XCircle, Loader, X } from 'lucide-react';

export default function VideoCard({ job, onDelete }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const getStatusBadge = () => {
    switch (job.status) {
      case 'completed':
        return <span className="badge-success"><CheckCircle className="w-3 h-3 mr-1" />Completed</span>;
      case 'processing':
        return <span className="badge-info"><Loader className="w-3 h-3 mr-1 animate-spin" />Processing</span>;
      case 'queued':
        return <span className="badge-warning"><Clock className="w-3 h-3 mr-1" />Queued</span>;
      case 'failed':
        return <span className="badge-error"><XCircle className="w-3 h-3 mr-1" />Failed</span>;
      default:
        return null;
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleString();
  };

  return (
    <div className="card group">
      {/* Thumbnail or Placeholder */}
      <div className="relative aspect-video bg-dark-hover rounded-lg overflow-hidden mb-4">
        {job.status === 'completed' && job.thumbnail_path ? (
          <img
            src={`/api/thumbnail/${job.job_id}`}
            alt={job.prompt}
            className="w-full h-full object-cover"
          />
        ) : job.status === 'processing' ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Loader className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-2" />
              <p className="text-sm text-gray-400">{job.progress}%</p>
              <div className="w-48 h-2 bg-dark-card rounded-full mt-2 overflow-hidden">
                <div
                  className="h-full bg-primary-500 transition-all duration-300"
                  style={{ width: `${job.progress}%` }}
                />
              </div>
            </div>
          </div>
        ) : job.status === 'failed' ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <XCircle className="w-12 h-12 text-red-500 mx-auto mb-2" />
              <p className="text-sm text-red-400">Generation Failed</p>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <Clock className="w-12 h-12 text-gray-600" />
          </div>
        )}

        {/* Play overlay for completed videos */}
        {job.status === 'completed' && (
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <button
              onClick={() => setIsPlaying(true)}
              className="bg-primary-600 hover:bg-primary-700 p-4 rounded-full transition-transform transform group-hover:scale-110"
            >
              <Play className="w-8 h-8 fill-white" />
            </button>
          </div>
        )}
      </div>

      {/* Status Badge */}
      <div className="mb-3">
        {getStatusBadge()}
      </div>

      {/* Prompt */}
      <p className="text-sm text-gray-300 mb-3 line-clamp-2">
        {job.prompt}
      </p>

      {/* Metadata */}
      <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
        <span>{formatDate(job.created_at)}</span>
        {job.duration && (
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {formatDuration(job.duration)}
          </span>
        )}
      </div>

      {/* Error message */}
      {job.status === 'failed' && job.error && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p className="text-xs text-red-400">{job.error}</p>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        {job.status === 'completed' && (
          <>
            <a
              href={`/api/video/${job.job_id}`}
              download
              className="btn-secondary flex-1 flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
              Download
            </a>
            <button
              onClick={() => onDelete(job.job_id)}
              className="btn-secondary px-3 hover:bg-red-500/10 hover:border-red-500/20 hover:text-red-400"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </>
        )}
        {(job.status === 'failed' || job.status === 'queued') && (
          <button
            onClick={() => onDelete(job.job_id)}
            className="btn-secondary flex-1 flex items-center justify-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </button>
        )}
      </div>
    </div>
  );
}

      {/* Video Player Modal */}
      {isPlaying && (
        <div className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4">
          <div className="relative w-full max-w-4xl">
            <button
              onClick={() => setIsPlaying(false)}
              className="absolute -top-10 right-0 text-white hover:text-gray-300"
            >
              <X className="w-8 h-8" />
            </button>
            <video
              key={job.job_id}
              controls
              autoPlay
              className="w-full rounded-lg"
            >
              <source src={`/api/video/${job.job_id}`} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        </div>
      )}
