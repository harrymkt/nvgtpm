folders = [
	"nvgtpm"
]

import os
import sys
import zipfile
import json
import uuid

EOF_SEP = f"EOF_{uuid.uuid4()}"

def zip(start_dir, zip_path, include_root=False):
	start_dir = os.path.abspath(start_dir)
	with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
		for root, dirs, files in os.walk(start_dir):
			for file in files:
				abs_path = os.path.join(root, file)
				if include_root:
					arcname = os.path.relpath(abs_path, os.path.dirname(start_dir))
				else:
					arcname = os.path.relpath(abs_path, start_dir)
				zf.write(abs_path, arcname)

def set_output(key, value):
	o = os.getenv("GITHUB_OUTPUT")
	if not o:
		return
	with open(o, "a") as f:
		if "\n" in value:
			f.write(f"{key}<<{EOF_SEP}\n{value}\n{EOF_SEP}\n")
		else:
			f.write(f"{key}={value}")

def main():
	print("Processing CI...")
	pr = "### Module Manifests\nThe following modules are available\n\n"
	for x in folders:
		zip(x, f"{x}.zip")
		print(f"{x}.zip created")
		d = None
		with open(f"{x}.json", "r", encoding="utf-8") as f:
			d = json.load(f)
		if not d:
			print(f"Warning: JSON file for {x} module could not be loaded.")
			continue
		cm = f"#### {d.get("name", x) or x}\n"
		if "description" in d: cm += f"{d["description"]}\n"
		cm += f"- Version: {d.get("version", "unknown")}\n- Download URL: {d["url"]}\n"
		if "homepage" in d: cm += f"- Home page URL: {d["homepage"]}"
		pr += f"{cm.strip()}\n\n"
	pr = pr.strip()
	set_output("pr_body", pr)
	return 0

if __name__ == "__main__":
	sys.exit(main())
