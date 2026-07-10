import sys
import argparse
import application as app
from src import bucket, module, cmd, github_action, program

def main():
	parser = argparse.ArgumentParser(allow_abbrev=False, description=f"NVGTPM version {app.version}: A Package Manager for NVGT Modules")
	subparsers = parser.add_subparsers(dest="command", title="Available commands:", metavar="<cmd>")
	aabout = subparsers.add_parser("about", description="Show information of the program", help="Show program information").set_defaults(func=program.about)
	program.cmd.register(subparsers)
	bucket.cmd.register(subparsers)
	
	install = subparsers.add_parser("install", description="Install script modules, includes", help="Install script modules, includes")
	install.add_argument("modules", nargs="*", help="Space-separated list of module names to install")
	install.add_argument("-r", "--requirement", help="Install modules from a file")
	install.set_defaults(func=lambda args: module.handle.install(args.modules, args.requirement))
	
	uninstall = subparsers.add_parser("uninstall", description="Purge an installed module and its directory completely", help="Uninstall a module")
	uninstall.add_argument("module", help="Name of the module to uninstall")
	uninstall.set_defaults(func=module.handle.uninstall)
	
	subparsers.add_parser("list", description="List all installed modules inside NVGT's include directory").set_defaults(func=module.handle.list)
	
	search = subparsers.add_parser("search", description="Search a specific module", help="Search modules")
	search.add_argument("pattern", help="Pattern to search")
	search.set_defaults(func=module.search)
	
	decl = subparsers.add_parser("decl", description="Retrieve the syntax to use a specific installed module", help="Retrieve the syntax to utilize a module")
	decl.add_argument("name", help="Name of the module that is installed")
	decl.add_argument("-c", "--copy", help="Copy the declaration syntax to clipboard", action="store_true")
	decl.set_defaults(func=module.decl)
	
	update = subparsers.add_parser("update", description="Synchronize modules and buckets", help="Update modules and buckets")
	update.add_argument("-bks", "--buckets", action="store_true", help="Download latest manifests from remote buckets")
	update.add_argument("-f", "--force", action="store_true", help="Force the update")
	update.add_argument("modules", nargs="*", help="Explicit selection labels, or '*' wildcard characters to upgrade all modules")
	update.set_defaults(func=module.handle.update_command)
	
	subparsers.add_parser("create", help="Create module manifests", description="Create module manifests").set_defaults(func=module.create_module)
	ga = subparsers.add_parser("create-ga", help="Create GitHub action for automated submition", description="Create a GitHub action to automate pull-request and update your module manifest")
	ga.add_argument("-o", "--output", help="Path to output, defaults to submit.yaml")
	ga.set_defaults(func=github_action.create)
	
	cmd.cache.register(subparsers)
	subparsers.add_parser("status", help="Check status of module updates", description="Check module updates").set_defaults(func=module.status)
	
	home = subparsers.add_parser("home", description="Open the home page of a module (if available)", help="Open the home page of a module")
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
	if "[applyupdatesilently]" in sys.argv:
		if program.applyupdate() == 0: sys.exit()
	sys.exit(main())
