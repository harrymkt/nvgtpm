folders = [
	"nvgtpm"
]

import os
import sys
import zipfile

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

def main():
	print("Processing files...")
	for x in folders:
		zip(x, f"{x}.zip")
		print(f"{x}.zip created")

if __name__ == "__main__":
	sys.exit(main())
