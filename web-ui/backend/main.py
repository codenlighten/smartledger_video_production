"""
HunyuanVideo Web UI - FastAPI Backend
Modern API for video generation with WebSocket support
"""
import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import subprocess

app = FastAPI(title="HunyuanVideo API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
RESULTS_DIR = Path("/opt/hunyuan-video/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# In-memory job queue and status
jobs: Dict[str, dict] = {}
active_connections: List[WebSocket] = []


class VideoRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for video generation")
    video_size: int = Field(720, description="Video resolution (540 or 720)")
    video_length: int = Field(129, description="Number of frames (1-129)")
    infer_steps: int = Field(50, description="Inference steps (30-100)")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    cfg_scale: float = Field(6.0, description="Classifier-free guidance scale")
    flow_reverse: bool = Field(True, description="Enable flow reversal")


class JobStatus(BaseModel):
    job_id: str
    status: str  # queued, processing, completed, failed
    prompt: str
    progress: int  # 0-100
    created_at: str
    completed_at: Optional[str] = None
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None


async def broadcast_status(job_id: str):
    """Broadcast job status to all connected WebSocket clients"""
    if job_id in jobs:
        message = json.dumps({
            "type": "status_update",
            "job": jobs[job_id]
        })
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            active_connections.remove(conn)


async def run_generation(job_id: str, request: VideoRequest):
    """Execute video generation in Docker container"""
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        await broadcast_status(job_id)
        
        # Build command
        cmd = [
            "docker", "exec", "hunyuan-video",
            "python", "sample_video.py",
            "--video-size", str(request.video_size),
            "--video-length", str(request.video_length),
            "--infer-steps", str(request.infer_steps),
            "--prompt", request.prompt,
            "--embedded-cfg-scale", str(request.cfg_scale),
            "--save-path", f"/workspace/HunyuanVideo/results/{job_id}"
        ]
        
        if request.seed is not None:
            cmd.extend(["--seed", str(request.seed)])
        
        if request.flow_reverse:
            cmd.append("--flow-reverse")
        
        # Run generation
        start_time = datetime.now()
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Monitor progress
        async def read_output():
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_str = line.decode().strip()
                
                # Parse progress from output
                if "%" in line_str or "step" in line_str.lower():
                    # Simple progress estimation
                    if jobs[job_id]["progress"] < 90:
                        jobs[job_id]["progress"] += 2
                        await broadcast_status(job_id)
        
        await asyncio.gather(read_output(), process.wait())
        
        duration = (datetime.now() - start_time).total_seconds()
        
        if process.returncode == 0:
            # Find generated video
            result_dir = RESULTS_DIR / job_id
            videos = list(result_dir.glob("*.mp4"))
            
            if videos:
                jobs[job_id]["status"] = "completed"
                jobs[job_id]["progress"] = 100
                jobs[job_id]["video_path"] = str(videos[0])
                jobs[job_id]["completed_at"] = datetime.now().isoformat()
                jobs[job_id]["duration"] = duration
                
                # Generate thumbnail (first frame)
                thumbnail_path = result_dir / "thumbnail.jpg"
                await asyncio.create_subprocess_exec(
                    "docker", "exec", "hunyuan-video",
                    "ffmpeg", "-i", f"/workspace/HunyuanVideo/results/{job_id}/{videos[0].name}",
                    "-vframes", "1", "-f", "image2",
                    f"/workspace/HunyuanVideo/results/{job_id}/thumbnail.jpg",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                jobs[job_id]["thumbnail_path"] = str(thumbnail_path)
            else:
                jobs[job_id]["status"] = "failed"
                jobs[job_id]["error"] = "No video file generated"
        else:
            stderr = await process.stderr.read()
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = stderr.decode()[:500]
        
        await broadcast_status(job_id)
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        await broadcast_status(job_id)


@app.post("/api/generate", response_model=JobStatus)
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """Queue a new video generation job"""
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "prompt": request.prompt,
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "video_path": None,
        "thumbnail_path": None,
        "error": None,
        "duration": None,
        "params": request.dict()
    }
    
    background_tasks.add_task(run_generation, job_id, request)
    
    return JobStatus(**jobs[job_id])


@app.get("/api/jobs", response_model=List[JobStatus])
async def list_jobs():
    """Get all jobs"""
    return [JobStatus(**job) for job in jobs.values()]


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job(job_id: str):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(**jobs[job_id])


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its files"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete files
    result_dir = RESULTS_DIR / job_id
    if result_dir.exists():
        import shutil
        shutil.rmtree(result_dir)
    
    del jobs[job_id]
    return {"message": "Job deleted"}


@app.get("/api/video/{job_id}")
async def get_video(job_id: str):
    """Download generated video"""
    if job_id not in jobs or not jobs[job_id].get("video_path"):
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_path = Path(jobs[job_id]["video_path"])
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"{job_id}.mp4"
    )


@app.get("/api/thumbnail/{job_id}")
async def get_thumbnail(job_id: str):
    """Get video thumbnail"""
    if job_id not in jobs or not jobs[job_id].get("thumbnail_path"):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    thumb_path = Path(jobs[job_id]["thumbnail_path"])
    if not thumb_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found")
    
    return FileResponse(thumb_path, media_type="image/jpeg")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send current jobs on connect
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "jobs": list(jobs.values())
        }))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    # Check if Docker container is running
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", "hunyuan-video"],
            capture_output=True,
            text=True
        )
        container_running = result.stdout.strip() == "true"
    except:
        container_running = False
    
    return {
        "status": "healthy" if container_running else "degraded",
        "container_running": container_running,
        "active_jobs": sum(1 for j in jobs.values() if j["status"] == "processing"),
        "total_jobs": len(jobs)
    }


@app.get("/api/stats")
async def get_stats():
    """Get generation statistics"""
    completed = [j for j in jobs.values() if j["status"] == "completed"]
    
    return {
        "total_generations": len(jobs),
        "completed": len(completed),
        "failed": sum(1 for j in jobs.values() if j["status"] == "failed"),
        "in_progress": sum(1 for j in jobs.values() if j["status"] == "processing"),
        "queued": sum(1 for j in jobs.values() if j["status"] == "queued"),
        "avg_duration": sum(j.get("duration", 0) for j in completed) / len(completed) if completed else 0,
        "total_duration": sum(j.get("duration", 0) for j in completed)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
