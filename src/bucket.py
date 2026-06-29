import json
import os
import shutil
import sys
from src import paths, github

class bucket:
	def __init__(self):
		self.name = None
		self.source = None
	
	@property
	def json(self):
		d = {}
		d["name"] = self.name
		d["source"] = self.source
		return d
	
	@property
	def dir(self):
		if self.is_local:
			return self.source
		return os.path.join(paths.buckets_root, self.name)
	
	@property
	def is_local(self):
		return self.source and not self.source.startswith(("http://", "https://"))
	
	def make_path(self, package):
		if not self.is_local:
			return os.path.join(self.dir, f"{package}.json")
		return os.path.join(self.dir, "json", f"{package}.json")
	
	def load_manifest(self, package):
		p = self.make_path(package)
		if not os.path.exists(p): return {}
		try:
			with open(p, "r") as f:
				return json.load(f)
		except:
			pass
		return {}
	
	def load(self, data):
		if data:
			if "name" in data:
				self.name = data["name"]
			if "source" in data:
				self.source = data["source"]
	
	@property
	def list(self):
		f = [d for d in os.listdir(self.dir) if os.path.isfile(os.path.join(self.dir, d))]
		l = []
		for x in f:
			ld = x.replace(".json", "")
			l.append(ld)
		return l

def load_buckets():
	paths.init_environment()
	buckets = []
	try:
		with open(paths.buckets_tracking_file, "r") as f:
			data = json.load(f)
			for name, source in data.items():
				b = bucket()
				b.load({"name": name, "source": source})
				buckets.append(b)
	except:
		pass
	if len(buckets) == 0:
		for name, source in paths.default_buckets.items():
			b = bucket()
			b.load({"name": name, "source": source})
			buckets.append(b)
	return buckets

def save_buckets(buckets):
	with open(paths.buckets_tracking_file, "w") as f:
		json.dump({b.name: b.source for b in buckets}, f, indent=2)

def find_bucket_index(buckets, name):
	# Find the index of a bucket by name in the buckets list.
	name = name.lower()
	for i, b in enumerate(buckets):
		if b.name == name:
			return i
	return -1

def find_bucket(buckets, name):
	# Find a bucket by name in the buckets list.
	x = find_bucket_index(buckets, name)
	if x == -1: return None
	return buckets[x]

def sync_remote_bucket_manifests(bucket_name, source_url):
	bucket_dir = os.path.join(paths.buckets_root, bucket_name)
	print(f"Updating bucket {bucket_name}...")
	github.download_and_extract_manifest_zip(source_url, bucket_dir)

def handle_bucket_add(args):
	buckets = load_buckets()
	name = args.name.lower()
	source = args.source
	if not source or source == "":
		if name in paths.known_buckets:
			source = paths.known_buckets.get(name, "")
	if not source or source == "":
		print(f"Error: bucket {name} does not contain a path or a link and is not a known bucket")
		sys.exit(1)
		return
	exist = find_bucket_index(buckets, name)
	b = bucket()
	b.load({"name": name, "source": source})
	if exist > -1:
		buckets[exist] = b
	else:
		buckets.append(b)
	save_buckets(buckets)
	if b.is_local:
		source = os.path.abspath(source)
		if not os.path.exists(os.path.join(source, "json")):
			print(f"Warning: Target folder \"{source}\" does not contain a 'json' subdirectory.")
		print(f"Added local bucket tracking '{name}' -> {source}")
	else:
		sync_remote_bucket_manifests(name, source)

def handle_bucket_remove(name):
	buckets = load_buckets()
	name = name.lower()
	idx = find_bucket_index(buckets, name)
	if idx >= 0:
		del buckets[idx]
		save_buckets(buckets)
		local_bucket_dir = os.path.join(paths.buckets_root, name)
		if os.path.exists(local_bucket_dir):
			shutil.rmtree(local_bucket_dir)
		print(f"Bucket {name} removed successfully.")
	else:
		print(f"Error: bucket {name} is not registered.")

def handle_bucket_list():
	buckets = load_buckets()
	if not buckets:
		print("No active buckets registered.")
		return
	print("Active buckets:")
	for b in sorted(buckets, key=lambda x: x.name):
		print(f"{b.name.ljust(15)} : {b.source}")

def handle_known_bucket_list(args):
	buckets = paths.known_buckets
	if not buckets:
		print("No known buckets.")
		return
	print("Known buckets:")
	for name, source in sorted(buckets.items()):
		print(f"{name.ljust(15)} : {source}")
