from src import program

def register(p):
	bp = p.add_parser("program", help="Manage NVGTPM program", description="Manage NVGTPM program related things")
	s = bp.add_subparsers(dest="subcommand", title="Available Commands", metavar="<cmd>")
	ab = s.add_parser("about", help="Show information about the program", description="Show about information of the program, such version information").set_defaults(func=program.about)
	upd = s.add_parser("update", help="Update the program", description="Update the NVGTPM program")
	upd.add_argument("-f", "--force", action="store_true", help="Force the update")
	upd.add_argument("-d", "--dev", action="store_true", help="Install the development version")
	upd.set_defaults(func=program.update_cmd)
