import os
import shutil
import sys
user_home = os.path.expanduser("~")
nvgtpm_dir = os.path.join(user_home, "nvgtpm")
cache_dir = os.path.join(nvgtpm_dir, "cache")
buckets_root = os.path.join(nvgtpm_dir, "buckets")
buckets_tracking_file = os.path.join(nvgtpm_dir, "buckets.json")
main_bucket_url = os.environ.get("nvgtpm_main_bucket_url", "")
if main_bucket_url == "":
	main_bucket_url = "https://github.com/harrymkt/nvgtpm_bucket_main"

known_buckets = {
	"main": main_bucket_url
}
default_buckets = {
	"main": main_bucket_url
}

def get_nvgt_include_dir():
	nvgt_path = shutil.which("nvgt")
	if not nvgt_path:
		print("Error: Could not locate 'nvgt' executable on system PATH.")
		sys.exit(1)
	return os.path.join(os.path.dirname(nvgt_path), "include")

def init_environment():
	os.makedirs(cache_dir, exist_ok=True)
	os.makedirs(buckets_root, exist_ok=True)
	import json
	cbuckets = {}
	try:
		with open(buckets_tracking_file, "r") as f:
			cbuckets = json.load(f)
	except:
		pass
	
	if not os.path.exists(buckets_tracking_file) or len(cbuckets) == 0:
		with open(buckets_tracking_file, "w") as f:
			json.dump(default_buckets, f, indent=2)
