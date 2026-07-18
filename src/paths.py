import os
import shutil
import sys

USER_HOME = os.path.expanduser("~")
NVGTPM_DIR = os.path.join(USER_HOME, "nvgtpm")
CACHE_DIR = os.path.join(NVGTPM_DIR, "cache")
BUCKETS_ROOT = os.path.join(NVGTPM_DIR, "buckets")
BUCKETS_TRACKING_FILE = os.path.join(NVGTPM_DIR, "buckets.json")
MAIN_BUCKET_URL = os.getenv("nvgtpm_main_bucket_url", "")
if MAIN_BUCKET_URL == "":
	MAIN_BUCKET_URL = "https://github.com/harrymkt/nvgtpm_bucket_main"

KNOWN_BUCKETS = {
	"main": MAIN_BUCKET_URL
}
DEFAULT_BUCKETS = {
	"main": MAIN_BUCKET_URL
}

def get_nvgt_include_dir():
	"""Returns a path to the directory containing NVGT executable."""
	nvgt_path = shutil.which("nvgt")
	if not nvgt_path:
		print("Error: Could not locate 'nvgt' executable on system PATH.")
		sys.exit(1)
		return None
	return os.path.join(os.path.dirname(nvgt_path), "include")

def init_environment():
	"""Initializes the environment of necessary verifications."""
	os.makedirs(CACHE_DIR, exist_ok=True)
	os.makedirs(BUCKETS_ROOT, exist_ok=True)
	import json
	cbuckets = {}
	try:
		with open(BUCKETS_TRACKING_FILE, "r", encoding="utf-8") as f:
			cbuckets = json.load(f)
	except:
		pass
	
	if not os.path.exists(BUCKETS_TRACKING_FILE) or not cbuckets or len(cbuckets) == 0:
		with open(BUCKETS_TRACKING_FILE, "w", encoding="utf-8") as f:
			json.dump(DEFAULT_BUCKETS, f, indent=2)
