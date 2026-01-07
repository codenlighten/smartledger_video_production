"""
HunyuanVideo Web UI - FastAPI Backend
"""
import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(title="HunyuanVideo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULTS_DIR = Path("/opt/hunyuan-video/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

jobs: Dict[str, dict] = {}
active_connections: List[WebSocket] = []

class VideoRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt")
    video_size: int = Field(720, description="Resolution (540 or 720)")
    video_length: int = Field(129, description="Frames (1-129)")
    infer_steps: int = Field(50, description="Steps (30-100)")
    seed: Optional[int] = Field(None, description="Seed")
    cfg_scale: float = Field(6.0, description="CFG scale")
    flow_reverse: bool = Field(True, description="Flow reversal")

class JobStatus(BaseModel):
    job_id: str
    status: str
    prompt: str
    progress: int
    created_at: str
    completed_at: Optional[str] = None
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None

async def broadcast_status(job_id: str):
    if job_id in jobs:
        message = json.dumps({"type": "status_update", "job": jobs[job_id]})
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        for conn in disconnected:
            active_connections.remove(conn)

async def run_generation(job_id: str, request: VideoRequest):
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        await broadcast_status(job_id)
        
        # Build command - wrap in bash -c with cd
        prompt_escaped = request.prompt.replace("'", "'\"'\"'")
        
        # Map resolution to height/width
        if request.video_size == 540:
            height, width = 544, 960  # 9:16 portrait
        else:  # 720p
            height, width = 720, 1280  # 16:9 landscape
        
        # Reduce steps to save memory if generating 720p
        steps = request.infer_steps
        if request.video_size == 720 and steps > 40:
            steps = 40  # Cap 720p at 40 steps to avoid OOM
        
        cmd_str = f"cd /workspace/repo && python sample_video.py "
        cmd_str += f"--video-size {height} {width} "
        cmd_str += f"--video-length {request.video_length} "
        cmd_str += f"--infer-steps {steps} "
        cmd_str += f"--prompt '{prompt_escaped}' "
        cmd_str += f"--embedded-cfg-scale {request.cfg_scale} "
        cmd_str += f"--use-cpu-offload "
        cmd_str += f"--save-path results/{job_id} "
        
        if request.seed is not None:
            cmd_str += f"--seed {request.seed} "
        if request.flow_reverse:
            cmd_str += "--flow-reverse "
        
        cmd = ["docker", "exec", "hunyuan-video", "bash", "-c", cmd_str]
        
        start_time = datetime.now()
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        async def read_output():
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_str = line.decode().strip()
                print(f"[{job_id[:8]}] {line_str}", flush=True)
                if jobs[job_id]["progress"] < 90:
                    jobs[job_id]["progress"] += 1
                    if jobs[job_id]["progress"] % 5 == 0:
                        await broadcast_status(job_id)
        
        async def read_errors():
            stderr_lines = []
            while True:
                line = await process.stderr.readline()
                if not line:
                    break
                line_str = line.decode().strip()
                stderr_lines.append(line_str)
                print(f"[{job_id[:8]}] ERROR: {line_str}", flush=True)
            return stderr_lines
        
        stdout_task = asyncio.create_task(read_output())
        stderr_task = asyncio.create_task(read_errors())
        await process.wait()
        await stdout_task
        stderr_lines = await stderr_task
        
        duration = (datetime.now() - start_time).total_seconds()
        
        if process.returncode == 0:
            # Find video
            find_cmd = ["docker", "exec", "hunyuan-video", "find", f"/workspace/repo/results/{job_id}", "-name", "*.mp4"]
            find_proc = await asyncio.create_subprocess_exec(*find_cmd, stdout=asyncio.subprocess.PIPE)
            stdout, _ = await find_proc.communicate()
            container_paths = stdout.decode().strip().split("\n")
            
            if container_paths and container_paths[0]:
                container_path = container_paths[0]
                video_name = Path(container_path).name
                host_result_dir = RESULTS_DIR / job_id
                host_result_dir.mkdir(parents=True, exist_ok=True)
                host_video_path = host_result_dir / video_name
                
                copy_cmd = ["docker", "cp", f"hunyuan-video:{container_path}", str(host_video_path)]
                await asyncio.create_subprocess_exec(*copy_cmd)
                
                jobs[job_id]["status"] = "completed"
                jobs[job_id]["progress"] = 100
                jobs[job_id]["video_path"] = str(host_video_path)
                jobs[job_id]["completed_at"] = datetime.now().isoformat()
                jobs[job_id]["duration"] = duration
                
                thumbnail_path = host_result_dir / "thumbnail.jpg"
                await asyncio.create_subprocess_exec(
                    "ffmpeg", "-i", str(host_video_path), "-vframes", "1", "-f", "image2", str(thumbnail_path),
                    stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
                )
                jobs[job_id]["thumbnail_path"] = str(thumbnail_path)
            else:
                jobs[job_id]["status"] = "failed"
                jobs[job_id]["error"] = "No video generated"
        else:
            error_msg = "\n".join(stderr_lines[-10:]) if stderr_lines else "Unknown error"
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = error_msg[:500]
            print(f"[{job_id[:8]}] FAILED with return code {process.returncode}", flush=True)
        
        await broadcast_status(job_id)
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        await broadcast_status(job_id)

@app.post("/api/generate", response_model=JobStatus)
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id, "status": "queued", "prompt": request.prompt,
        "progress": 0, "created_at": datetime.now().isoformat(),
        "completed_at": None, "video_path": None, "thumbnail_path": None,
        "error": None, "duration": None, "params": request.dict()
    }
    background_tasks.add_task(run_generation, job_id, request)
    return JobStatus(**jobs[job_id])

@app.get("/api/jobs", response_model=List[JobStatus])
async def list_jobs():
    return [JobStatus(**job) for job in jobs.values()]

@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(**jobs[job_id])

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    result_dir = RESULTS_DIR / job_id
    if result_dir.exists():
        import shutil
        shutil.rmtree(result_dir)
    del jobs[job_id]
    return {"message": "Job deleted"}

@app.get("/api/video/{job_id}")
async def get_video(job_id: str):
    if job_id not in jobs or not jobs[job_id].get("video_path"):
        raise HTTPException(status_code=404, detail="Video not found")
    video_path = Path(jobs[job_id]["video_path"])
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(
        video_path,
        media_type="video/mp4",
        headers={"Content-Disposition": "inline; filename=video.mp4"}
    )

@app.get("/api/thumbnail/{job_id}")
async def get_thumbnail(job_id: str):
    if job_id not in jobs or not jobs[job_id].get("thumbnail_path"):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    thumb_path = Path(jobs[job_id]["thumbnail_path"])
    if not thumb_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found")
    return FileResponse(thumb_path, media_type="image/jpeg")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        # Don't send initial_state - frontend fetches from /api/jobs
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/api/health")
async def health_check():
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", "hunyuan-video"],
            capture_output=True, text=True
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
