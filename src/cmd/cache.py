from src import paths, helper
from fnmatch import fnmatch
import os

# Functions
def search(pattern):
	if not pattern: return None
	result = []
	for f in os.listdir(paths.cache_dir):
		fn = os.path.join(paths.cache_dir, f)
		if not os.path.exists(fn): continue
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
		print("Error: no pattern is given.")
		return 1
	totalsize = 0
	c = 0
	for x in search(pattern):
		f = x["name"]
		fn = x["path"]
		size = x["size"]
		if not args.silent:
			print(f"Removing {fn if args.fullpath else f}, {helper.convert_size(size)}...")
		os.remove(fn)
		totalsize += size
		c += 1
	
	if c == 0:
		print("No files to remove with this pattern.")
		return 0
	print(f"Removed {c} {"file" if c == 1 else "files"}, {helper.convert_size(totalsize)}.")
	return 0

def register(p):
	bp = p.add_parser("cache", help="Manage cache", description="Manage cache files")
	s = bp.add_subparsers(dest="subcommand", title="Available Commands:")
	rm = s.add_parser("rm", description="Remove one or more cache files", help="Remove cache")
	rm.add_argument("pattern", help="A pattern to remove cache")
	rm.add_argument("-s", "--silent", help="Do not print what files are being removed", action="store_true")
	rm.add_argument("-fp", "--fullpath", help="Read full paths", action="store_true")
	rm.set_defaults(func=remove)
