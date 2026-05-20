# scripts/main.py

from pathlib import Path             # For cross-platform path handling
# ↓ To support running the script directly (python scripts/main.py),
#   temporarily add the project root directory to sys.path 
#   so that the workload_code package can be imported.
import sys
from pathlib import Path
import logging                       # Logging system
from datetime import datetime        # For generating timestamped log filenames

# ✅ Recommended: Import modules as a package 
#    (run from project root: python -m scripts.main)
#    To maintain compatibility with direct execution, 
#    sys.path.append is used here to add the project root to the module search path.
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Import the console interaction entry point (which internally calls simulation_engine)
from workload_code.user_interface import start_console_app


def _setup_logging() -> None:
    """
    Initialize the logging system:
    - Log files are saved to results/logs/, with filenames including a timestamp
    - Logs are also output to the console (for real-time viewing)
    """
    project_root = Path(__file__).resolve().parents[1]   # Locate project root directory
    log_dir = project_root / "results" / "logs"          # Log directory: results/logs/
    log_dir.mkdir(parents=True, exist_ok=True)           # Create directory if it does not exist

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")        # Timestamp, e.g., 20250108-153045
    log_file = log_dir / f"run_{ts}.log"                 # Log filename

    # Basic configuration: write to file, INFO level, include time/level/module/message in format
    logging.basicConfig(
        filename=str(log_file),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Also output to console (optional): add a StreamHandler to the root logger
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logging.getLogger().addHandler(console)


if __name__ == "__main__":
    # 1) Initialize logging (file + console)
    _setup_logging()
    # 2) Start the interactive console application 
    #    (user chooses default parameters or custom parameters)
    start_console_app()
