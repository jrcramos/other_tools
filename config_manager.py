"""
Configuration manager for other_tools.
Persists user preferences such as custom download directories and theme settings in config.json.
"""
import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "download_dir": os.path.expanduser(r"~\Videos") if os.path.exists(os.path.expanduser(r"~\Videos")) else os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads"),
    "theme": "dark"
}

def load_config() -> dict:
    """Loads config from config.json with fallbacks."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure required keys exist
            for k, v in DEFAULT_CONFIG.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config_dict: dict):
    """Saves config dictionary to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[-] Failed to save config: {e}")

def get_download_dir() -> str:
    """Gets the persistent user download directory."""
    cfg = load_config()
    download_dir = cfg.get("download_dir", "")
    if not download_dir or not os.path.exists(download_dir):
        # Fallback to Videos or root downloads folder
        fallback = os.path.expanduser(r"~\Videos")
        if not os.path.exists(fallback):
            fallback = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        os.makedirs(fallback, exist_ok=True)
        return fallback
    return download_dir

def set_download_dir(path: str):
    """Sets and persists the user download directory."""
    if not path:
        return
    clean_path = os.path.abspath(path.strip().strip('"').strip("'"))
    os.makedirs(clean_path, exist_ok=True)
    cfg = load_config()
    cfg["download_dir"] = clean_path
    save_config(cfg)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--get-download-dir":
            print(get_download_dir())
        elif sys.argv[1] == "--set-download-dir" and len(sys.argv) > 2:
            set_download_dir(sys.argv[2])
            print(f"Download directory set to: {get_download_dir()}")
    else:
        print(f"Current Config: {load_config()}")
