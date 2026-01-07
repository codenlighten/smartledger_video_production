import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE = '/api';

export const useWebSocket = () => {
  const [ws, setWs] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    const websocket = new WebSocket(wsUrl);
    
    websocket.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      // Reconnect after 3 seconds
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    };
    
    setWs(websocket);
    
    return () => {
      websocket.close();
    };
  }, []);

  return { ws, connected };
};

export const useJobs = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const { ws } = useWebSocket();

  const fetchJobs = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/jobs`);
      console.log('[API] Fetched jobs:', response.data.length);
      setJobs(response.data);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch jobs on mount
  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  // Only listen to status updates from WebSocket, not initial_state
  useEffect(() => {
    if (!ws) return;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'status_update') {
        console.log('[WebSocket] Status update for job:', data.job.job_id, '→', data.job.status);
        setJobs(prev => {
          const index = prev.findIndex(j => j.job_id === data.job.job_id);
          if (index >= 0) {
            // Update existing job
            const updated = [...prev];
            updated[index] = data.job;
            console.log('[WebSocket] Updated existing job at index', index);
            return updated;
          } else {
            // New job from background task
            console.log('[WebSocket] Adding new job');
            return [data.job, ...prev];
          }
        });
      }
    };
  }, [ws]);

  const generateVideo = async (params) => {
    try {
      const response = await axios.post(`${API_BASE}/generate`, params);
      console.log('[API] Generated video:', response.data.job_id);
      // Add to local state immediately
      setJobs(prev => [response.data, ...prev]);
      return response.data;
    } catch (error) {
      console.error('Failed to generate video:', error);
      throw error;
    }
  };

  const deleteJob = async (jobId) => {
    try {
      await axios.delete(`${API_BASE}/jobs/${jobId}`);
      setJobs(prev => prev.filter(j => j.job_id !== jobId));
    } catch (error) {
      console.error('Failed to delete job:', error);
      throw error;
    }
  };

  return {
    jobs,
    loading,
    generateVideo,
    deleteJob,
    refresh: fetchJobs
  };
};

export const useStats = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API_BASE}/stats`);
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  return stats;
};
