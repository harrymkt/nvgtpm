import os
import sys
import argparse
from src import bucket, module, cmd, github_action, program

def main():
	parser = argparse.ArgumentParser(allow_abbrev=False, description="A Package Manager for NVGT Modules")
	subparsers = parser.add_subparsers(dest="command", title="Available Commands", metavar="<cmd>")
	program.cmd.register(subparsers)
	bucket.cmd.register(subparsers)
	
	install = subparsers.add_parser("install", help="Install script modules", description="Install script modules, include scripts")
	install.add_argument("modules", nargs="*", help="Space-separated list of module names to install")
	install.add_argument("-r", "--requirement", help="Install modules from a file")
	install.set_defaults(func=lambda args: module.handle.install(args.modules, args.requirement))
	
	uninstall = subparsers.add_parser("uninstall", help="Uninstall a module", description="Purge an installed module and its directory completely")
	uninstall.add_argument("module", help="Name of the module to uninstall")
	uninstall.set_defaults(func=module.handle.uninstall)
	
	subparsers.add_parser("list", help="List installed modules", description="List all installed modules inside NVGT's include directory").set_defaults(func=module.handle.list)
	
	search = subparsers.add_parser("search", help="Search modules", description="Search a specific module")
	search.add_argument("pattern", help="Pattern to search")
	search.set_defaults(func=module.search)
	
	decl = subparsers.add_parser("decl", help="Retrieve the syntax to utilize a module", description="Retrieve the syntax to use a specific installed module")
	decl.add_argument("name", help="Name of the module that is installed")
	decl.add_argument("-c", "--copy", help="Copy the declaration syntax to clipboard", action="store_true")
	decl.set_defaults(func=module.decl)
	
	update = subparsers.add_parser("update", help="Update modules and buckets", description="Synchronize modules and buckets")
	update.add_argument("-bks", "--buckets", action="store_true", help="Download latest manifests from remote buckets")
	update.add_argument("-f", "--force", action="store_true", help="Force the update")
	update.add_argument("modules", nargs="*", help="Explicit selection labels, or '*' wildcard characters to upgrade all modules")
	update.set_defaults(func=module.handle.update_command)
	
	subparsers.add_parser("create", help="Create module manifests", description="Create module manifests").set_defaults(func=module.create_module)
	
	ga = subparsers.add_parser("create-ga", help="Create GitHub action for automated submition", description="Create a GitHub action to automate pull-request and update your module manifest")
	ga.add_argument("-o", "--output", help="Path to output, defaults to submit.yaml")
	ga.set_defaults(func=github_action.create)
	
	cmd.cache.register(subparsers)
	
	subparsers.add_parser("status", help="Check module updates", description="Check status of module updates").set_defaults(func=module.status)
	
	home = subparsers.add_parser("home", help="Open the home page of a module", description="Open the home page of a module (if available)")
	home.add_argument("name", help="Name of the module")
	home.set_defaults(func=module.handle.homepage)
	
	e = 0
	args = parser.parse_args()
	if hasattr(args, "func"):
		e = args.func(args)
	else:
		parser.print_help()
	return e

if __name__ == "__main__":
	sys.exit(main())
