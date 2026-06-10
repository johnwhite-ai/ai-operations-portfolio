import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cs2_input import find_cs2_window, send_console_command
from deploy_cfgs import deploy_cfgs

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


@asynccontextmanager
async def lifespan(app: FastAPI):
    result = deploy_cfgs()
    if result["error"]:
        print(f"[deploy_cfgs] WARN: {result['error']}")
    else:
        print(f"[deploy_cfgs] deployed {len(result['deployed'])} file(s): {', '.join(result['deployed'])}")
    yield


app = FastAPI(title="CS2 Training Companion", lifespan=lifespan)


class ExecRequest(BaseModel):
    cmd: str


@app.post("/exec")
def exec_cmd(req: ExecRequest):
    cmd = req.cmd.strip()
    if not cmd:
        raise HTTPException(400, "empty command")
    if not send_console_command(cmd):
        raise HTTPException(503, "CS2 window not found")
    return {"ok": True, "cmd": cmd}


@app.get("/health")
def health():
    return {"cs2_running": find_cs2_window() is not None}


@app.post("/redeploy")
def redeploy():
    return deploy_cfgs()


@app.get("/report")
def latest_report():
    if not REPORTS_DIR.exists():
        raise HTTPException(404, "reports/ dir does not exist")
    json_files = sorted(REPORTS_DIR.glob("weekly-report-*.json"))
    if not json_files:
        raise HTTPException(404, "no weekly report JSON available")
    latest = json_files[-1]
    return json.loads(latest.read_text(encoding="utf-8"))


if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
