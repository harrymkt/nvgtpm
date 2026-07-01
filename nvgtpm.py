import argparse
import application as app
from src import bucket, module, cmd

def main():
	parser = argparse.ArgumentParser(allow_abbrev=False, description=f"NVGTPM version {app.version}: A Package Manager for NVGT Modules known as include scripts")
	subparsers = parser.add_subparsers(dest="command", title="Available commands:")
	bucket.cmd.register(subparsers)
	
	install_parser = subparsers.add_parser("install", description="Install targeted script modules, includes", help="Install script modules, includes")
	install_parser.add_argument("modules", nargs="*", help="Space-separated list of module names to install")
	install_parser.add_argument("-r", "--requirement", help="Install bulk module listings tracked from a plain text file")
	install_parser.set_defaults(func=lambda args: module.handle.install(args.modules, args.requirement))
	
	uninstall_parser = subparsers.add_parser("uninstall", description="Purge an installed module and its directory completely", help="Uninstall a module")
	uninstall_parser.add_argument("module", help="Name string of the module to uninstall")
	uninstall_parser.set_defaults(func=module.handle.uninstall)
	
	subparsers.add_parser("list", description="List all installed modules inside NVGT's include directory").set_defaults(func=module.handle.list)
	
	search = subparsers.add_parser("search", description="Search a specific module", help="Search modules")
	search.add_argument("pattern", help="Pattern to search")
	search.set_defaults(func=module.search)
	
	decl = subparsers.add_parser("decl", description="Retrieve the syntax to use a specific installed module", help="Retrieve the syntax to utilize a module")
	decl.add_argument("name", help="The name of the module that is installed")
	decl.add_argument("-c", "--copy", help="Copy the declaration syntax to clipboard", action="store_true")
	decl.set_defaults(func=module.decl)
	
	update_parser = subparsers.add_parser("update", description="Synchronize modules and buckets", help="Update modules and buckets")
	update_parser.add_argument("-bks", "--buckets", action="store_true", help="Download latest manifests from remote buckets")
	update_parser.add_argument("-f", "--force", action="store_true", help="Force the update")
	update_parser.add_argument("modules", nargs="*", help="Explicit selection labels, or '*' wildcard characters to upgrade all modules")
	update_parser.set_defaults(func=module.handle.update_command)
	
	subparsers.add_parser("create", help="Create module manifests", description="Create module manifests").set_defaults(func=module.create_module)
	cmd.cache.register(subparsers)
	subparsers.add_parser("status", help="Check status of module updates", description="Check module updates").set_defaults(func=module.status)
	
	args = parser.parse_args()
	if hasattr(args, "func"):
		args.func(args)
	else:
		parser.print_help()

if __name__ == "__main__":
	main()
