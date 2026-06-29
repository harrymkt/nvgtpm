import json
import os
import shutil
import sys
import urllib.request
import zipfile
from src import paths, bucket, version

class package:
	def __init__(self, data=None):
		self.name = None
		self.version = None
		self.url = None
		self.entry = None
		self.extract_dir = None
		self.bucket = None
		if data:
			self.load(data)
	
	@property
	def json(self):
		d = {}
		if self.version is not None:
			d["version"] = self.version
		if self.url is not None:
			d["url"] = self.url
		if self.entry is not None:
			d["entry"] = self.entry
		if self.extract_dir is not None:
			d["extract_dir"] = self.extract_dir
		if self.bucket is not None:
			d["bucket"] = self.bucket
		return d
	
	def load(self, data):
		if data:
			if "name" in data:
				self.name = data["name"]
			if "version" in data:
				self.version = data["version"]
			if "url" in data:
				self.url = data["url"]
			if "entry" in data:
				self.entry = data["entry"]
			if "extract_dir" in data:
				self.extract_dir = data["extract_dir"]
			if "bucket" in data:
				self.bucket = data["bucket"]
	
	@property
	def dir(self):
		if self.name:
			return os.path.join(paths.get_nvgt_include_dir(), self.name)
		return None
	
	@property
	def is_local(self):
		if self.url:
			return not self.url.startswith(("http://", "https://"))
		return None
	
	def save(self, path):
		with open(path, "w", encoding="utf-8") as f:
			json.dump(self.json, f, indent=2)

def get_installed_packages():
	include_dir = paths.get_nvgt_include_dir()
	if not os.path.exists(include_dir):
		return []
	return [d for d in os.listdir(include_dir) if os.path.isdir(os.path.join(include_dir, d))]

def load_manifest_from(path, package_name):
	if not os.path.exists(path): return None
	try:
		with open(path, "r") as f:
			data = json.load(f)
			pkg = package()
			temp_manifest = data
			temp_manifest["name"] = package_name
			pkg.load(temp_manifest)
			return pkg
	except:
		pass
	return None

def locate_and_load_manifest(package_name, buckets=None):
	buckets = buckets or bucket.load_buckets()
	bucket_name = None
	pkg_name = package_name
	if "/" in package_name:
		parts = package_name.split("/", 1)
		bucket_name = parts[0].lower()
		pkg_name = parts[1]
		b = bucket.find_bucket(buckets, bucket_name)
		if not b:
			return None, None
		p = b.make_path(pkg_name)
		if not os.path.exists(p):
			return None, None
		pkg = load_manifest_from(p, pkg_name)
		if pkg:
			pkg.bucket = b.name
			return pkg, b
		return None, None
	for b in buckets:
		if b.name == bucket_name:
			continue
		p = b.make_path(package_name)
		if not os.path.exists(p):
			continue
		pkg = load_manifest_from(p, package_name)
		if pkg:
			pkg.bucket = b.name
			return pkg, b
	return None, None

def load_current_info(name):
	incdir = paths.get_nvgt_include_dir()
	if not os.path.exists(incdir): return None
	p = os.path.join(incdir, name, "info.json")
	if not os.path.exists(p): return None
	return load_manifest_from(p, name)

def show_package_info(name, pkg, bucket_name):
	if name == "" or not pkg: return
	print(f"| {name} | {pkg.version or 'unknown'} | {bucket_name} |")

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

def handle_install_package(package_names, requirement_file, force_update=False, force=False):
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
			cinfo = load_current_info(pkg)
			if cinfo:
				bucket_to_use = cinfo.bucket
		if bucket_to_use:
			manifest, b = locate_and_load_manifest(f"{bucket_to_use}/{pkg_name}")
		else:
			manifest, b = locate_and_load_manifest(pkg_name)
		if not manifest:
			if bucket_to_use:
				print(f"Error: Package {pkg_name} could not be located in bucket {bucket_to_use}.")
			else:
				print(f"Error: Package {pkg_name} could not be located in any active bucket.")
			continue
		pkg_version = manifest.version or "1.0.0"
		url_or_path = manifest.url
		bucket_name = b.name
		target_path = os.path.join(include_dir, manifest.extract_dir or pkg_name)
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

def handle_uninstall(package_name):
	include_dir = paths.get_nvgt_include_dir()
	pkg_name = package_name.lower()
	target_path = os.path.join(include_dir, pkg_name)
	if os.path.exists(target_path) and os.path.isdir(target_path):
		shutil.rmtree(target_path)
		print(f"Successfully removed {pkg_name} from NVGT include directory.")
	else:
		print(f"Error: Package {pkg_name} is not currently installed.")

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
		show_package_info(pkg, manifest, manifest.bucket if manifest else "unknown")

def _check_package_update(pkg, buckets, force=False):
	manifest = load_current_info(pkg)
	if not manifest:
		return None
	current_bucket = bucket.find_bucket(buckets, manifest.bucket or "main")
	if not current_bucket:
		return None
	latest_manifest = current_bucket.load_manifest(pkg)
	if not latest_manifest:
		return None
	vc = version.version(manifest.version or "0.0.0")
	vl = version.version(latest_manifest.version or "0.0.0")
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
			print(f"Updating {pkg}: current version {update_info['current']}, latest version {update_info['latest']} (from {update_info['bucket']} bucket)")
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
	handle_install_package(updates_to_perform, None, force_update=True, force=args.force)

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
		if not manifest: continue
		b = bucket.find_bucket(buckets, manifest.bucket or "main")
		if not b: continue
		linfo = b.load_manifest(x)
		if not linfo: continue
		vc = version.version(manifest.version or "0.0.0")
		vl = version.version(linfo.version or "0.0.0")
		if vl == vc or vl < vc: continue
		c += 1
		prints.append(f"New version {vl.version} of {x} from {b.name} bucket")
	
	if len(prints) == 0 or c == 0:
		print("No updates available")
		return
	
	print(f"{c} {"modules are" if c != 1 else "module is"} out of date:")
	for x in prints:
		print(x)

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
	if not manifest:
		print(f"Error. Manifest for {term} cannot be determined")
		sys.exit(1)
		return
	show_package_info(term, manifest, bc.name)

def decl(args):
	manifest = load_current_info(args.name)
	if not manifest:
		print(f"Error. Package {args.name} does not seem to have installed.")
		sys.exit(1)
		return
	print(f'#include "{manifest.name or args.name}/{manifest.entry or "main"}.nvgt"')

def create_package(args):
	pkg = package()
	pkg.name = input("Package name")
	if not pkg.name:
		print("Error. A package must have a name.")
		return
	elif " " in pkg.name:
		print("Error. The name must not contain spaces")
		return
	pkg.url = input("A link to download, or a path on the local file system")
	if not pkg.url:
		print("Error. A link to download or a path is required.")
		return
	pkg.version = input("Version")
	if not pkg.version:
		print("Error. A package requires its version.")
		return
	with open(f"{pkg.name}.json", "w", encoding="utf-8") as f:
		json.dump(pkg.json, f, indent=2)
	print(f"Successfully created {pkg.name}.json")
