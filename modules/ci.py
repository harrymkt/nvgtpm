folders = [
	"nvgtpm"
]

import os
import sys
import zipfile
import json
import uuid

EOF_SEP = f"EOF_{uuid.uuid4()}"

def zip(start_dir, zip_path, include_root=False, custom_path=None, custom_paths=None):
	"""
	Zips files from start_dir into zip_path.
	
	:param start_dir: Root directory to walk.
	:param zip_path: Output ZIP file destination.
	:param include_root: Includes top directory name in arcnames if True.
	:param custom_path: Single path (string) or tuple/list `(source_path, target_arcname)`.
	:param custom_paths: List of paths/tuples or dict `{source_path: target_arcname}`.
	"""
	start_dir = os.path.abspath(start_dir)
	
	# Mapping of { absolute_source_path: archive_path_name }
	custom_map = {}
	
	def process_custom_entry(src, target=None):
		# If path is relative, evaluate it relative to current working directory (e.g. "license.md")
		abs_src = os.path.abspath(src)
		
		if target is not None:
			target_arcname = target
		else:
			# Default name inside the zip will be the filename itself
			target_arcname = os.path.basename(abs_src)
			
		custom_map[abs_src] = target_arcname

	if custom_path:
		if isinstance(custom_path, (tuple, list)):
			process_custom_entry(custom_path[0], custom_path[1])
		else:
			process_custom_entry(custom_path)

	if custom_paths:
		if isinstance(custom_paths, dict):
			for src, target in custom_paths.items():
				process_custom_entry(src, target)
		elif isinstance(custom_paths, (list, set, tuple)):
			for item in custom_paths:
				if isinstance(item, (tuple, list)):
					process_custom_entry(item[0], item[1])
				else:
					process_custom_entry(item)

	written_paths = set()

	with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
		# 1. Walk through the start_dir directory
		for root, dirs, files in os.walk(start_dir):
			for file in files:
				abs_path = os.path.join(root, file)

				if abs_path in custom_map:
					arcname = custom_map[abs_path]
				elif include_root:
					arcname = os.path.relpath(abs_path, os.path.dirname(start_dir))
				else:
					arcname = os.path.relpath(abs_path, start_dir)

				zf.write(abs_path, arcname)
				written_paths.add(abs_path)

		# 2. Write external custom paths that were not inside start_dir
		for abs_src, arcname in custom_map.items():
			if abs_src not in written_paths and os.path.exists(abs_src):
				zf.write(abs_src, arcname)
				written_paths.add(abs_src)

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
