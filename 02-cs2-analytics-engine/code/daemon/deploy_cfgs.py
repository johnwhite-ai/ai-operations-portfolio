import shutil
from pathlib import Path

CS2_CFG_DIR = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg"
)


def deploy_cfgs() -> dict:
    src_dir = Path(__file__).resolve().parent.parent / "cfg"
    if not src_dir.exists():
        return {"deployed": [], "error": f"source dir missing: {src_dir}"}
    if not CS2_CFG_DIR.exists():
        return {"deployed": [], "error": f"CS2 cfg dir missing: {CS2_CFG_DIR}"}

    deployed = []
    for src in src_dir.glob("*.cfg"):
        shutil.copy2(src, CS2_CFG_DIR / src.name)
        deployed.append(src.name)
    return {"deployed": deployed, "error": None}
