import argparse
import application as app
from src import bucket, package

def main():
	parser = argparse.ArgumentParser(allow_abbrev=False, description=f"NVGTPM version {app.version}: A Package Manager for NVGT Modules known as include scripts")
	subparsers = parser.add_subparsers(dest="command")
	# Command Layout: bucket [add | rm | list]
	bucket_parser = subparsers.add_parser("bucket", help="Manage buckets where you get modules from", description="Manage buckets")
	bucket_sub = bucket_parser.add_subparsers(dest="subcommand")
	b_add = bucket_sub.add_parser("add", description="add an external workspace path folder or Git repository URL, as a bucket", help="Add a bucket")
	b_add.add_argument("name", help="Bucket shorthand tracking reference name")
	b_add.add_argument("source", nargs="?", default="", help="GitHub repo HTTPS URL or local directory file path. Can be optional if the bucket is in the list of known buckets.")
	b_add.set_defaults(func=bucket.handle_bucket_add)
	b_rm = bucket_sub.add_parser("rm", description="Remove an active registered bucket and delete its manifest directory cache", help="Remove a bucket")
	b_rm.add_argument("name", help="Target bucket alias label")
	b_rm.set_defaults(func=lambda args: bucket.handle_bucket_remove(args.name))
	bucket_sub.add_parser("list", help="List all buckets", description="List all registered remote and local buckets").set_defaults(func=lambda args: bucket.handle_bucket_list())
	bucket_sub.add_parser("known", help="List officially known buckets", description="List all known remote buckets").set_defaults(func=bucket.handle_known_bucket_list)
	
	install_parser = subparsers.add_parser("install", description="Install targeted script modules, includes", help="Install script modules, includes")
	install_parser.add_argument("packages", nargs="*", help="Space-separated list of module names to install")
	install_parser.add_argument("-r", "--requirement", help="Install bulk package listings tracked from a plain text file")
	install_parser.set_defaults(func=lambda args: package.handle_install(args.packages, args.requirement))
	
	uninstall_parser = subparsers.add_parser("uninstall", description="Purge an installed package directory completely", help="Uninstall a module")
	uninstall_parser.add_argument("package", help="Name string of the module to uninstall")
	uninstall_parser.set_defaults(func=lambda args: package.handle_uninstall(args.package))
	
	subparsers.add_parser("list", description="List all installed modules inside NVGT's include directory").set_defaults(func=lambda args: package.handle_list())
	
	search = subparsers.add_parser("search", description="Search a specific module", help="Search modules")
	search.add_argument("package", help="Name string of the module to search")
	search.set_defaults(func=package.search)
	
	decl = subparsers.add_parser("decl", description="Retrieve the syntax to use a specific installed module", help="Retrieve the syntax to utilize a module")
	decl.add_argument("name", help="The name of the module that is installed")
	decl.set_defaults(func=package.decl)
	
	update_parser = subparsers.add_parser("update", description="Synchronize modules and buckets", help="Update modules and buckets")
	update_parser.add_argument("-bks", "--buckets", action="store_true", help="Download latest manifests from remote buckets")
	update_parser.add_argument("-f", "--force", action="store_true", help="Force the update")
	update_parser.add_argument("packages", nargs="*", help="Explicit selection labels, or '*' wildcard characters to upgrade all packages")
	update_parser.set_defaults(func=package.handle_update_command)
	
	subparsers.add_parser("create", help="Create package manifests", description="Create package manifests").set_defaults(func=package.create_package)
	subparsers.add_parser("cleanup", help="Clean cache files", description="Cleans up cached files").set_defaults(func=lambda args: package.handle_cleanup())
	subparsers.add_parser("status", help="Check status of module updates", description="Check module updates").set_defaults(func=package.status)
	
	args = parser.parse_args()
	if hasattr(args, "func"):
		args.func(args)
	else:
		parser.print_help()

if __name__ == "__main__":
	main()
