import json
import os
from src import paths
from . import cmd

class Bucket:
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
		return os.path.join(paths.BUCKETS_ROOT, self.name)
	
	@property
	def is_local(self):
		return self.source and not self.source.startswith(("http://", "https://"))
	
	def make_path(self, module_name):
		if not self.is_local:
			return os.path.join(self.dir, f"{module_name}.json")
		return os.path.join(self.dir, "json", f"{module_name}.json")
	
	def load_manifest(self, module_name):
		from src import module
		p = self.make_path(module_name)
		if not os.path.exists(p): return None
		return module.load_manifest_from(p, module_name)
	
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

def load():
	paths.init_environment()
	buckets = []
	try:
		with open(paths.BUCKETS_TRACKING_FILE, "r", encoding="utf-8") as f:
			data = json.load(f)
			for name, source in data.items():
				b = Bucket()
				b.load({"name": name, "source": source})
				buckets.append(b)
	except:
		pass
	if len(buckets) == 0:
		for name, source in paths.DEFAULT_BUCKETS.items():
			b = Bucket()
			b.load({"name": name, "source": source})
			buckets.append(b)
	return buckets

def save(buckets):
	with open(paths.BUCKETS_TRACKING_FILE, "w", encoding="utf-8") as f:
		json.dump({b.name: b.source for b in buckets}, f, indent=2)

def find_index(buckets, name):
	name = name.lower()
	for i, b in enumerate(buckets):
		if b.name == name:
			return i
	return -1

def find(buckets, name):
	x = find_index(buckets, name)
	if x == -1: return None
	return buckets[x]

def sync_remote_bucket_manifests(bucket_name, source_url):
	bucket_dir = os.path.join(paths.BUCKETS_ROOT, bucket_name)
	print(f"Updating bucket {bucket_name}...")
	from src import github
	github.download_and_extract_manifest_zip(source_url, bucket_dir)
