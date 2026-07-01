import json
import os
import sys
from src import paths, bucket, version
from . import handle
from .search import *

class package:
	def __init__(self, data=None):
		self.name = None
		self.version = None
		self.url = None
		self.entry = None
		self.bucket = None
		self.description = None
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
		if self.bucket is not None:
			d["bucket"] = self.bucket
		if self.description is not None:
			d["description"] = self.description
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
			if "bucket" in data:
				self.bucket = data["bucket"]
			if "description" in data:
				self.description = data["description"]
	
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

def list_installed_packages(bucket_name=None):
	buckets = bucket.load()
	b = None
	if bucket_name: b = bucket.find(buckets, bucket_name)
	result = []
	for pkg in get_installed_packages():
		m = load_current_info(pkg)
		if not m: continue
		if b and not b.name == m.bucket: continue
		result.append(m)
	return result

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
	buckets = buckets or bucket.load()
	bucket_name = None
	pkg_name = package_name
	if "/" in package_name:
		parts = package_name.split("/", 1)
		bucket_name = parts[0].lower()
		pkg_name = parts[1]
		b = bucket.find(buckets, bucket_name)
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
	print(f"| {name} | {pkg.version or 'unknown'} | {bucket_name} | {pkg.description or ""} |")

def _check_package_update(pkg, buckets, force=False):
	manifest = load_current_info(pkg)
	if not manifest:
		return None
	current_bucket = bucket.find(buckets, manifest.bucket or "main")
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

def status(args):
	pkgs = get_installed_packages()
	if len(pkgs) == 0:
		print("No modules installed")
		return
	buckets = bucket.load()
	c = 0
	prints = []
	for x in pkgs:
		manifest = load_current_info(x)
		if not manifest: continue
		b = bucket.find(buckets, manifest.bucket or "main")
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

def decl(args):
	manifest = load_current_info(args.name)
	if not manifest:
		print(f"Error. Package {args.name} does not seem to have installed.")
		sys.exit(1)
		return
	m = "main"
	if not os.path.exists(os.path.join(manifest.dir, f"{m}.nvgt")): m = manifest.name or args.name
	msg = f"#include \"{manifest.name or args.name}/{manifest.entry or m}.nvgt\""
	print(msg)
	if args.copy:
		import pyperclip as clip
		clip.copy(msg)
	return

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
	pkg.description = input("Package description, a short summary, optional")
	with open(f"{pkg.name}.json", "w", encoding="utf-8") as f:
		json.dump(pkg.json, f, indent=2)
	print(f"Successfully created {pkg.name}.json")
