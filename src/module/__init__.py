import json
import os
import sys
from src import paths, bucket, version
from . import handle
from .search import *

class Module:
	def __init__(self, data=None):
		self.name = None
		self.version = None
		self.url = None
		self.entry = None
		self.bucket = None
		self.description = None
		self.homepage = None
		self.depends = None
		if data:
			self.load(data)
	
	@property
	def json(self):
		d = {}
		if self.version:
			d["version"] = self.version
		if self.url:
			d["url"] = self.url
		if self.entry:
			d["entry"] = self.entry
		if self.bucket:
			d["bucket"] = self.bucket
		if self.description:
			d["description"] = self.description
		if self.homepage:
			d["homepage"] = self.homepage
		if self.depends and len(self.depends) != 0:
			d["depends"] = self.depends
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
			if "homepage" in data:
				self.homepage = data["homepage"]
			if "depends" in data:
				self.depends = data["depends"]
	
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

def get_installed_modules():
	include_dir = paths.get_nvgt_include_dir()
	if not os.path.exists(include_dir):
		return []
	return [d for d in os.listdir(include_dir) if os.path.isdir(os.path.join(include_dir, d))]

def list_installed_modules(bucket_name=None):
	result = []
	for mod in get_installed_modules():
		m = load_current_info(mod)
		if not m: continue
		if bucket_name and not bucket_name == m.bucket: continue
		result.append(m)
	return result

def load_manifest_from(path, module_name):
	if not os.path.exists(path): return None
	try:
		with open(path, "r") as f:
			data = json.load(f)
			mod = Module()
			temp_manifest = data
			temp_manifest["name"] = module_name
			mod.load(temp_manifest)
			return mod
	except:
		pass
	return None

def locate_and_load_manifest(module_name, buckets=None):
	buckets = buckets or bucket.load()
	bucket_name = None
	mod_name = module_name
	if "/" in module_name:
		parts = module_name.split("/", 1)
		bucket_name = parts[0].lower()
		mod_name = parts[1]
		b = bucket.find(buckets, bucket_name)
		if not b:
			return None, None
		p = b.make_path(mod_name)
		if not os.path.exists(p):
			return None, None
		mod = load_manifest_from(p, mod_name)
		if mod:
			mod.bucket = b.name
			return mod, b
		return None, None
	for b in buckets:
		if b.name == bucket_name:
			continue
		p = b.make_path(module_name)
		if not os.path.exists(p):
			continue
		mod = load_manifest_from(p, module_name)
		if mod:
			mod.bucket = b.name
			return mod, b
	return None, None

def load_current_info(name):
	incdir = paths.get_nvgt_include_dir()
	if not os.path.exists(incdir): return None
	p = os.path.join(incdir, name, "info.json")
	if not os.path.exists(p): return None
	return load_manifest_from(p, name)

def show_info(name, mod, bucket_name=None):
	if name == "" or not mod: return
	print(f"| {name} | {mod.version or "unknown"} | {bucket_name or mod.bucket or ""} | {mod.description or ""} |")

def _check_module_update(mod, buckets, force=False):
	manifest = load_current_info(mod)
	if not manifest:
		return None
	current_bucket = bucket.find(buckets, manifest.bucket or "main")
	if not current_bucket:
		return None
	latest_manifest = current_bucket.load_manifest(mod)
	if not latest_manifest:
		return None
	vc = version.Version(manifest.version or "0.0.0")
	vl = version.Version(latest_manifest.version or "0.0.0")
	if vl > vc or force:
		return {"current": vc.version, "latest": vl.version, "bucket": current_bucket.name}
	return None

def status(args):
	mods = get_installed_modules()
	if len(mods) == 0:
		print("No modules are installed.")
		return 0
	buckets = bucket.load()
	c = 0
	prints = []
	for x in mods:
		manifest = load_current_info(x)
		if not manifest: continue
		b = bucket.find(buckets, manifest.bucket or "main")
		if not b: continue
		linfo = b.load_manifest(x)
		if not linfo: continue
		vc = version.Version(manifest.version or "0.0.0")
		vl = version.Version(linfo.version or "0.0.0")
		if vl == vc or vl < vc: continue
		c += 1
		prints.append(f"New version {vl.version} of {x} from {b.name} bucket")
	
	if len(prints) == 0 or c == 0:
		print("No updates available.")
		return 0
	
	print(f"{c} {"modules are" if c != 1 else "module is"} out of date:")
	for x in prints:
		print(x)
	return 0

def decl(args):
	manifest = load_current_info(args.name)
	if not manifest:
		print(f"Error. Module {args.name} does not seem to have installed.")
		return 1
	m = "main"
	if not os.path.exists(os.path.join(manifest.dir, f"{m}.nvgt")): m = manifest.name or args.name
	msg = f"#include \"{manifest.name or args.name}/{manifest.entry or m}.nvgt\""
	print(msg)
	if args.copy:
		import pyperclip as clip
		clip.copy(msg)
	return 0

def create_module(args):
	mod = Module()
	mod.name = input("Module name")
	if not mod.name:
		print("Error: a module must have a name.")
		return 1
	elif " " in mod.name:
		print("Error: the name must not contain spaces.")
		return 1
	mod.url = input("A link to download, or a path on the local file system")
	if not mod.url:
		print("Error: a link to download or a path is required.")
		return 1
	mod.version = input("Version")
	if not mod.version:
		print("Error: a module requires its version.")
		return 1
	mod.description = input("Module description, a short summary, optional")
	mod.homepage = input("Home page to the website or repository of the module, optional")
	depends = []
	for x in input("Semicolon separated list of required dependencies, optional").split(";"):
		if not x: continue
		if " " in x:
			print(f"Module {x} contains spaces, skipping...")
			continue
		depends.append(x)
	if len(depends) != 0: mod.depends = depends
	with open(f"{mod.name}.json", "w", encoding="utf-8") as f:
		json.dump(mod.json, f, indent=2)
	print(f"Successfully created {mod.name}.json")
	return 0
