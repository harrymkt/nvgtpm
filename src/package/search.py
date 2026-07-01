import os
import sys
import fnmatch
from src import bucket, package

def search(args):
	term = args.pattern
	search_term = term.lower()
	buckets = bucket.load()
	found = False
	print(f"Search results for '{term}':")
	print("| Name | Version | bucket name | description |")
	print("|---|---|---|---|")
	for b in buckets:
		pkg_dir = b.dir
		if not os.path.isdir(pkg_dir):
			continue
		for filename in b.list:
			p = b.make_path(filename)
			manifest = package.load_manifest_from(p, filename)
			if not manifest:
				continue
			match_pkg = fnmatch.fnmatch(filename.lower(), search_term)
			match_bucket = fnmatch.fnmatch(b.name.lower(), search_term)
			match_desc = fnmatch.fnmatch((manifest.description or "").lower(), search_term)
			if match_pkg or match_bucket or match_desc:
				package.show_package_info(filename, manifest, b.name)
				found = True
	
	if not found:
		print(f"No packages matching '{term}' found.")
		sys.exit(1)
