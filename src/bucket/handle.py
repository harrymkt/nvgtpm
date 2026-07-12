import json
import os
import shutil
from src import bucket, paths

def add(args):
	buckets = bucket.load()
	name = args.name.lower()
	source = args.source
	if not source or source == "":
		if name in paths.KNOWN_BUCKETS:
			source = paths.KNOWN_BUCKETS.get(name, "")
	if not source or source == "":
		print(f"Error: bucket {name} does not contain a path or a link and is not in one of the known buckets.")
		return 1
	exist = bucket.find_index(buckets, name)
	b = bucket.Bucket()
	b.load({"name": name, "source": source})
	if exist > -1:
		buckets[exist] = b
	else:
		buckets.append(b)
	bucket.save(buckets)
	if b.is_local:
		source = os.path.abspath(source)
		if not os.path.exists(os.path.join(source, "json")):
			print(f"Warning: Target folder \"{source}\" does not contain a 'json' subdirectory.")
		print(f"Added local bucket tracking '{name}' -> {source}")
	else:
		bucket.sync_remote_bucket_manifests(name, source)
	return 0

def remove(name):
	buckets = bucket.load()
	name = name.lower()
	idx = bucket.find_index(buckets, name)
	if idx >= 0:
		del buckets[idx]
		bucket.save(buckets)
		local_bucket_dir = os.path.join(paths.BUCKETS_ROOT, name)
		if os.path.exists(local_bucket_dir):
			shutil.rmtree(local_bucket_dir)
		print(f"Bucket {name} removed successfully.")
		return 0
	else:
		print(f"Error: bucket {name} is not registered.")
		return 1

def list():
	buckets = bucket.load()
	if not buckets:
		print("No active buckets registered.")
		return 0
	print("Active buckets:")
	for b in sorted(buckets, key=lambda x: x.name):
		print(f"{b.name.ljust(15)} : {b.source}")
	return 0

def known(args):
	buckets = paths.KNOWN_BUCKETS
	if not buckets:
		print("No known buckets.")
		return 0
	print("Known buckets:")
	for name, source in sorted(buckets.items()):
		print(f"{name.ljust(15)} : {source}")
	return 0

def homepage(args):
	buckets = bucket.load()
	b = bucket.find(buckets, args.name.lower())
	if not b:
		print(f"Error: bucket {args.name} not found.")
		return 1
	elif b.is_local:
		print(f"Error: bucket {b.name} is a local bucket and does not have a URL to open.")
		return 1
	import webbrowser as w
	if not w.open(b.source):
		print(f"Error: failed to open the URL of bucket {b.name}")
		print("---")
		print(b.source)
		return 1
	print(f"URL for {b.name} opened successfully in your browser.")
	return 0
