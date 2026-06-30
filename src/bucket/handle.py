import json
import os
import shutil
import sys
from src import bucket, paths

def add(args):
	buckets = bucket.load_buckets()
	name = args.name.lower()
	source = args.source
	if not source or source == "":
		if name in paths.known_buckets:
			source = paths.known_buckets.get(name, "")
	if not source or source == "":
		print(f"Error: bucket {name} does not contain a path or a link and is not a known bucket")
		sys.exit(1)
		return
	exist = bucket.find_bucket_index(buckets, name)
	b = bucket.bucket()
	b.load({"name": name, "source": source})
	if exist > -1:
		buckets[exist] = b
	else:
		buckets.append(b)
	bucket.save_buckets(buckets)
	if b.is_local:
		source = os.path.abspath(source)
		if not os.path.exists(os.path.join(source, "json")):
			print(f"Warning: Target folder \"{source}\" does not contain a 'json' subdirectory.")
		print(f"Added local bucket tracking '{name}' -> {source}")
	else:
		bucket.sync_remote_bucket_manifests(name, source)

def remove(name):
	buckets = bucket.load_buckets()
	name = name.lower()
	idx = bucket.find_bucket_index(buckets, name)
	if idx >= 0:
		del buckets[idx]
		bucket.save_buckets(buckets)
		local_bucket_dir = os.path.join(paths.buckets_root, name)
		if os.path.exists(local_bucket_dir):
			shutil.rmtree(local_bucket_dir)
		print(f"Bucket {name} removed successfully.")
	else:
		print(f"Error: bucket {name} is not registered.")

def list():
	buckets = bucket.load_buckets()
	if not buckets:
		print("No active buckets registered.")
		return
	print("Active buckets:")
	for b in sorted(buckets, key=lambda x: x.name):
		print(f"{b.name.ljust(15)} : {b.source}")

def known(args):
	buckets = paths.known_buckets
	if not buckets:
		print("No known buckets.")
		return
	print("Known buckets:")
	for name, source in sorted(buckets.items()):
		print(f"{name.ljust(15)} : {source}")

def homepage(args):
	buckets = bucket.load_buckets()
	b = bucket.find_bucket(buckets, args.name.lower())
	if not b:
		print(f"Bucket {args.name} not found")
		return
	elif b.is_local:
		print(f"Error. Bucket {b.name} is a local bucket and does not have a URL to open")
		return
	import webbrowser as w
	if not w.open(b.source):
		print(f"Error. Failed to open the URL of bucket {b.name}")
		print("---")
		print(b.source)
		sys.exit(1)
		return
	print(f"URL for {b.name} opened successfully in your browser.")
