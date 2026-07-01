import json, os, shutil
import sys
import requests
import zipfile
from src import bucket, helper, package, paths

def install(package_names, requirement_file, force_update=False, force=False):
	if not package_names and not requirement_file:
		print("Error: The install command requires explicit arguments inputs fields.")
		sys.exit(1)
	include_dir = paths.get_nvgt_include_dir()
	targets = []
	if package_names:
		targets.extend(package_names)
	if requirement_file and os.path.exists(requirement_file):
		with open(requirement_file, "r") as f:
			targets.extend([
				line.strip()
				for line in f
				if line.strip() and not line.startswith("#")
			])
	for pkg in targets:
		pkg_name = pkg
		bucket_to_use = None
		if "/" in pkg:
			parts = pkg.split("/", 1)
			bucket_to_use = parts[0].lower()
			pkg_name = parts[1]
		elif force_update:
			cinfo = package.load_current_info(pkg)
			if cinfo:
				bucket_to_use = cinfo.bucket
		if bucket_to_use:
			manifest, b = package.locate_and_load_manifest(f"{bucket_to_use}/{pkg_name}")
		else:
			manifest, b = package.locate_and_load_manifest(pkg_name)
		if not manifest:
			if bucket_to_use:
				print(f"Error: Package {pkg_name} could not be located in bucket {bucket_to_use}.")
			else:
				print(f"Error: Package {pkg_name} could not be located in any active bucket.")
			continue
		pkg_version = manifest.version or "1.0.0"
		url_or_path = manifest.url
		bucket_name = b.name
		target_path = os.path.join(include_dir, pkg_name)
		zip_payload_path = None
		installed = False
		if url_or_path and manifest.is_local:
			full_local_path = os.path.normpath(url_or_path)
			if os.path.isdir(full_local_path):
				print(f"Syncing folder copy from local bucket: {full_local_path}")
				if os.path.exists(target_path):
					shutil.rmtree(target_path)
				shutil.copytree(full_local_path, target_path)
				installed = True
			elif os.path.isfile(full_local_path) and zipfile.is_zipfile(full_local_path):
				zip_payload_path = full_local_path
		else:
			zip_filename = f"{pkg_name}-{pkg_version}.zip"
			zip_payload_path = os.path.join(paths.cache_dir, zip_filename)
			if force_update and os.path.exists(zip_payload_path):
				os.remove(zip_payload_path)
			try:
				head = requests.head(url_or_path, timeout=15, headers={"User-Agent": "NVGTPM-Package-Manager-Client"})
				head.raise_for_status()
				content_length = int(head.headers.get("Content-Length", 0))
				size_str = helper.convert_size(content_length) if content_length > 0 else "unknown size"
				print(f"Downloading release archive for {pkg_name} ({size_str}) from {bucket_name} bucket...")
			except Exception:
				print(f"Downloading release archive for {pkg_name} from {bucket_name} bucket...")
			try:
				with requests.get(url_or_path, timeout=30, stream=True, headers={"User-Agent": "NVGTPM-Package-Manager-Client"}) as response:
					response.raise_for_status()
					with open(zip_payload_path, "wb") as f:
						for chunk in response.iter_content(chunk_size=8192):
							if chunk:
								f.write(chunk)
			except Exception as e:
				print(f"Failed to download asset archive: {e}")
				continue
		if zip_payload_path:
			if os.path.exists(target_path):
				shutil.rmtree(target_path)
			os.makedirs(target_path, exist_ok=True)
			try:
				with zipfile.ZipFile(zip_payload_path, "r") as zip_ref:
					zip_ref.extractall(target_path)
				installed = True
			except Exception as e:
				print(f"Extraction failure: {e}")
				continue
		if installed:
			print(f"Successfully installed {pkg_name} {pkg_version}")
			info_path = os.path.join(target_path, "info.json")
			manifest_path = b.make_path(pkg_name)
			try:
				with open(manifest_path, "r") as f:
					manifest_data = json.load(f)
				manifest_data["bucket"] = bucket_name
				with open(info_path, "w", encoding="utf-8") as f:
					json.dump(manifest_data, f, indent=2)
			except Exception as e:
				print(f"Warning: install succeeded but failed to write manifest: {e}")

def uninstall(args):
	package_name = args.package
	include_dir = paths.get_nvgt_include_dir()
	pkg_name = package_name.lower()
	target_path = os.path.join(include_dir, pkg_name)
	if os.path.exists(target_path) and os.path.isdir(target_path):
		shutil.rmtree(target_path)
		print(f"Successfully removed {pkg_name} from NVGT include directory.")
	else:
		print(f"Error: Package {pkg_name} is not currently installed.")

def list(args):
	packages = package.get_installed_packages()
	if not packages:
		print("No packages currently installed.")
		return
	print("Installed NVGT Packages:")
	print("| Name | Version | bucket name | description |")
	print("|---|---|---|---|")
	for pkg in sorted(packages):
		manifest = package.load_current_info(pkg)
		package.show_package_info(pkg, manifest, manifest.bucket if manifest else "unknown")

def update_command(args):
	buckets = bucket.load()
	if args.buckets:
		print("Synchronizing all remote buckets...")
		for b in buckets:
			if not b.is_local:
				bucket.sync_remote_bucket_manifests(b.name, b.source)
		if not args.packages:
			return
	
	targets = []
	if args.packages:
		if "*" in args.packages:
			targets = package.get_installed_packages()
		else:
			targets = [pkg.lower() for pkg in args.packages]
	
	updates_to_perform = []
	is_wildcard = "*" in args.packages
	for pkg in targets:
		update_info = package._check_package_update(pkg, buckets, force=args.force)
		if update_info:
			print(f"Updating {pkg}: current version {update_info['current']}, latest version {update_info['latest']} (from {update_info['bucket']} bucket)")
			updates_to_perform.append(pkg)
		elif is_wildcard:
			if not package.load_current_info(pkg):
				print(f"Package {pkg} not installed, skipping.")
			else:
				pass
		else:
			if not package.load_current_info(pkg):
				print(f"Package {pkg} is not installed.")
			else:
				print(f"Package {pkg} is already up to date.")
	
	if not args.packages:
		print("Error: Please specify a target package name, * or bucket update flags.")
		return
	
	if is_wildcard and not updates_to_perform:
		print("All packages are already up to date.")
		return
	
	if not updates_to_perform: return
	install(updates_to_perform, None, force_update=True, force=args.force)
