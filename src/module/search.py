import os
import fnmatch
from src import bucket, module

def search(args):
	term = args.pattern
	search_term = term.lower()
	buckets = bucket.load()
	found = False
	print(f"Search results for '{term}':")
	print("| Name | Version | bucket name | description |")
	print("|---|---|---|---|")
	for b in buckets:
		for filename in b.list:
			p = b.make_path(filename)
			manifest = module.load_manifest_from(p, filename)
			if not manifest:
				continue
			match_mod = fnmatch.fnmatch(filename.lower(), search_term)
			match_bucket = fnmatch.fnmatch(b.name.lower(), search_term)
			match_desc = fnmatch.fnmatch((manifest.description or "").lower(), search_term)
			if match_mod or match_bucket or match_desc:
				module.show_info(filename, manifest, b.name)
				found = True
	
	if not found:
		print(f"No modules matching '{term}' found.")
		return 0
