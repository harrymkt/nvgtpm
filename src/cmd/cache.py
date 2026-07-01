from src import paths, helper
from fnmatch import fnmatch
import os

# Functions
def search(pattern):
	if not pattern: return None
	result = []
	for f in os.listdir(paths.cache_dir):
		fn = os.path.join(paths.cache_dir, f)
		if not os.path.exist(fn): continue
		if not fnmatch(f, pattern): continue
		d = {
			"name": f,
			"path": fn,
			"size": os.path.getsize(fn)
		}
		result.append(d)
	return result

def remove(args):
	pattern = args.pattern
	if not pattern:
		print("No pattern is given")
		return
	totalsize = 0
	c = 0
	for x in search(pattern):
		f = x["name"]
		fn = x["path"]
		size = f["size"]
		print(f"Removing {f}, {helper.convert_size(size)}...")
		os.remove(fn)
		totalsize += size
		c += 1
	if c == 0:
		print("No files to remove with this pattern")
		return
	print(f"Removed {c} {"file" if c == 1 else "files"}, {helper.convert_size(totalsize)}")

def register(p):
	bp = p.add_parser("cache", help="Manage cache", description="Manage cache files")
	s = bp.add_subparsers(dest="sub")
	rm = s.add_parser("rm", help="Remove one or more cache files")
	rm.add_argument("pattern", help="A pattern to remove cache")
	rm.set_defaults(func=remove)
