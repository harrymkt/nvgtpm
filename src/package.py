import json
import os
import shutil
import sys
import urllib.request
import zipfile
from src import paths, bucket, version

def get_installed_packages():
	include_dir = paths.get_nvgt_include_dir()
	if not os.path.exists(include_dir):
		return []
	return [d for d in os.listdir(include_dir) if os.path.isdir(os.path.join(include_dir, d))]

def locate_and_load_manifest(package_name, buckets=None):
	buckets = buckets or bucket.load_buckets()
	bucket_name = None
	pkg_name = package_name
	if "/" in package_name:
		parts = package_name.split("/", 1)
		bucket_name = parts[0].lower()
		pkg_name = parts[1]
		pkg_filename = f"{pkg_name.lower()}.json"
		b = bucket.find_bucket(buckets, bucket_name)
		if not b:
			return None, False, None, bucket_name
		if b.is_local:
			potential_path = os.path.join(b.source, "json", pkg_filename)
			if os.path.exists(potential_path):
				with open(potential_path, "r") as f:
					return json.load(f), True, b.source, b.name
		else:
			potential_path = os.path.join(b.dir, pkg_filename)
			if os.path.exists(potential_path):
				with open(potential_path, "r") as f:
					return json.load(f), False, b.source, b.name
		return None, False, None, bucket_name
	pkg_filename = f"{package_name.lower()}.json"
	for b in buckets:
		if b.name == bucket_name:
			continue
		if b.is_local:
			potential_path = os.path.join(b.source, "json", pkg_filename)
			if os.path.exists(potential_path):
				with open(potential_path, "r") as f:
					return json.load(f), True, b.source, b.name
		else:
			potential_path = os.path.join(b.dir, pkg_filename)
			if os.path.exists(potential_path):
				with open(potential_path, "r") as f:
					return json.load(f), False, b.source, b.name
	return None, False, None, None

def handle_install(package_names, requirement_file, force_update=False, force=False):
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
			stored_info = load_current_info(pkg)
			if stored_info:
				bucket_to_use = stored_info.get("bucket")
		if bucket_to_use:
			manifest, is_local, bucket_source, bucket_name = locate_and_load_manifest(f"{bucket_to_use}/{pkg_name}")
		else:
			manifest, is_local, bucket_source, bucket_name = locate_and_load_manifest(pkg_name)
		if not manifest:
			if bucket_name:
				print(f"Error: Package {pkg_name} could not be located in bucket {bucket_name}.")
			else:
				print(f"Error: Package {pkg_name} could not be located in any active bucket.")
			continue
		pkg_version = manifest.get("version", "1.0.0")
		url_or_path = manifest.get("url")
		target_path = os.path.join(include_dir, manifest.get("extract_dir", pkg_name))
		zip_payload_path = None
		installed = False
		if is_local and not url_or_path.startswith(("http://", "https://")):
			full_local_path = os.path.normpath(os.path.join(bucket_source, url_or_path))
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
			if not os.path.exists(zip_payload_path):
				print(f"Downloading release archive for {pkg_name} from {bucket_name} bucket...")
				try:
					urllib.request.urlretrieve(url_or_path, zip_payload_path)
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
				print(f"Successfully installed {pkg_name} {pkg_version}")
				installed = True
			except Exception as e:
				print(f"Extraction failure: {e}")
				continue
		if installed:
			info_path = os.path.join(target_path, "info.json")
			manifest["bucket"] = bucket_name
			manifest["name"] = pkg_name
			try:
				with open(info_path, "w", encoding="utf-8") as f:
					json.dump(manifest, f, indent=2)
			except Exception as e:
				print(f"Warning: install succeeded but failed to write manifest: {e}")

def handle_uninstall(package_name):
	include_dir = paths.get_nvgt_include_dir()
	pkg_name = package_name.lower()
	target_path = os.path.join(include_dir, pkg_name)
	if os.path.exists(target_path) and os.path.isdir(target_path):
		shutil.rmtree(target_path)
		print(f"Successfully removed {pkg_name} from NVGT include directory.")
	else:
		print(f"Error: Package {pkg_name} is not currently installed.")

def handle_cleanup():
	c = 0
	files = os.listdir(paths.cache_dir)
	if len(files) == 0:
		print("No cache to clean")
		return
	for x in files:
		fn = os.path.join(paths.cache_dir, x)
		if not os.path.exists(fn): continue
		os.remove(fn)
		c += 1
	print(f"{c} cache {"file" if c == 1 else "files"} removed")

def handle_list():
	packages = get_installed_packages()
	if not packages:
		print("No packages currently installed.")
		return
	print("Installed NVGT Packages:")
	print("| Name | Version | bucket name |")
	print("|---|---|---|")
	for pkg in sorted(packages):
		manifest = load_current_info(pkg)
		show_package_info(pkg, manifest, manifest.get("bucket", "unknown"))

def _check_package_update(pkg, buckets, force=False):
	manifest = load_current_info(pkg)
	if not manifest or len(manifest) == 0:
		return None
	current_bucket = bucket.find_bucket(buckets, manifest.get("bucket", "main"))
	if not current_bucket:
		return None
	latest_manifest = current_bucket.load_manifest(pkg)
	if not latest_manifest or len(latest_manifest) == 0:
		return None
	vc = version.version(manifest.get("version", "0.0.0"))
	vl = version.version(latest_manifest.get("version", vc))
	if vl > vc or force:
		return {"current": vc.version, "latest": vl.version, "bucket": current_bucket.name}
	return None

def handle_update_command(args):
	buckets = bucket.load_buckets()
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
			targets = get_installed_packages()
		else:
			targets = [pkg.lower() for pkg in args.packages]
	
	updates_to_perform = []
	is_wildcard = "*" in args.packages
	for pkg in targets:
		update_info = _check_package_update(pkg, buckets, force=args.force)
		if update_info:
			print(f"Updating {pkg}: current version {update_info["current"]}, latest version {update_info["latest"]} (from {update_info["bucket"]} bucket)")
			updates_to_perform.append(pkg)
		elif is_wildcard:
			if not load_current_info(pkg):
				print(f"Package {pkg} not installed, skipping.")
			else:
				pass
		else:
			if not load_current_info(pkg):
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
	handle_install(updates_to_perform, None, force_update=True, force=args.force)

def load_current_info(name):
	incdir = paths.get_nvgt_include_dir()
	if not os.path.exists(incdir): return {}
	p = os.path.join(incdir, name, "info.json")
	if not os.path.exists(p): return {}
	try:
		with open(p, "r") as f:
			return json.load(f)
	except:
		pass
	return {}

def show_package_info(name, manifest, bucket_name):
	if name == "" or len(manifest) == 0: return
	print(f"| {name} | {manifest.get("version", "unknown")} | {bucket_name} |")

def search(args):
	term = args.package.lower()
	buckets = bucket.load_buckets()
	bc = None
	for b in buckets:
		l = b.list
		if term in l:
			bc = b
			break
	
	if not bc:
		print(f"There is no package matching {term}")
		sys.exit(1)
		return
	manifest = bc.load_manifest(term)
	if not manifest or len(manifest) == 0:
		print(f"Error. Manifest for {term} cannot be determined")
		sys.exit(1)
		return
	show_package_info(term, manifest, bc.name)

def status(args):
	pkgs = get_installed_packages()
	if len(pkgs) == 0:
		print("No modules installed")
		return
	buckets = bucket.load_buckets()
	c = 0
	prints = []
	for x in pkgs:
		manifest = load_current_info(x)
		if not manifest or len(manifest) == 0: continue
		b = bucket.find_bucket(buckets, manifest.get("bucket", "main"))
		if not b: continue
		linfo = b.load_manifest(x)
		if not linfo or len(linfo) == 0: continue
		vc = version.version(manifest.get("version", "0.0.0"))
		vl = version.version(linfo.get("version", vc))
		if vl == vc or vl < vc: continue
		c += 1
		prints.append(f"New version {vl.version} of {x} from {b.name} bucket")
	
	if len(prints) == 0 or c == 0:
		print("No updates available")
		return
	
	print(f"{c} {"modules are" if c != 1 else "module is"} out of date:")
	for x in prints:
		print(x)

def decl(args):
	if not args.name:
		print("Error. Name is required")
		sys.exit(1)
		return
	manifest = load_current_info(args.name)
	if not manifest or len(manifest) == 0:
		print(f"Error. Package {args.name} does not seem to have installed.")
		sys.exit(1)
		return
	f = f"#include \"{manifest.get("name", args.name)}/{manifest.get("entry", "main")}.nvgt\""
	print(f)

def create_package(args):
	name = input("Package name")
	if not name:
		print("Error. A package must have a name.")
		return
	elif " " in name:
		print("Error. The name must not contain spaces")
		return
	url = input("A link to download, or a path on the local file system")
	if not url:
		print("Error. A link to download or a path is required.")
		return
	version = input("Version")
	if not version:
		print("Error. A package requires its version.")
		return
	d = {
		"url": url,
		"version": version
	}
	with open(f"{name}.json", "w", encoding="utf-8") as f:
		json.dump(d, f, indent=2)
	print(f"Successfully created {name}.json")
