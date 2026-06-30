import argparse
from . import handle

def register(p):
	bp = p.add_parser("bucket", help="Manage buckets where you get modules from", description="Manage buckets")
	bs = bp.add_subparsers(dest="subcommand")
	b_add = bs.add_parser("add", description="add an external workspace path folder or Git repository URL, as a bucket", help="Add a bucket")
	b_add.add_argument("name", help="Bucket shorthand tracking reference name")
	b_add.add_argument("source", nargs="?", default="", help="GitHub repo HTTPS URL or local directory file path. Can be optional if the bucket is in the list of known buckets.")
	b_add.set_defaults(func=handle.add)
	b_rm = bs.add_parser("rm", description="Remove an active registered bucket and delete its manifest directory cache", help="Remove a bucket")
	b_rm.add_argument("name", help="Target bucket alias label")
	b_rm.set_defaults(func=lambda args: handle.remove(args.name))
	bs.add_parser("list", help="List all buckets", description="List all registered remote and local buckets").set_defaults(func=lambda args: handle.list())
	bs.add_parser("known", help="List officially known buckets", description="List all known remote buckets").set_defaults(func=handle.known)
	home = bs.add_parser("home", description="Open the home page, the source, of a given bucket", help="Open the home page of a bucket")
	home.add_argument("name", help="Target bucket")
	home.set_defaults(func=handle.homepage)
