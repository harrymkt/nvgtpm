import json
import os, shutil
import requests
import zipfile
from src import bucket, helper, module, paths

def install(module_names, requirement_file, force_update=False, force=False):
	if not module_names and not requirement_file:
		print("Error: The install command requires explicit arguments inputs fields.")
		return 1
	include_dir = paths.get_nvgt_include_dir()
	targets = []
	if module_names:
		targets.extend(module_names)
	if requirement_file and os.path.exists(requirement_file):
		with open(requirement_file, "r", encoding="utf-8") as f:
			targets.extend([
				line.strip()
				for line in f
				if line.strip() and not line.startswith("#")
			])
	if not targets:
		print("Error: a list of modules to install is required.")
		return 1
	for mod in targets:
		mod_name = mod
		bucket_to_use = None
		if "/" in mod:
			parts = mod.split("/", 1)
			bucket_to_use = parts[0].lower()
			mod_name = parts[1]
		elif force_update:
			cinfo = module.load_current_info(mod)
			if cinfo:
				bucket_to_use = cinfo.bucket
		if bucket_to_use:
			manifest, b = module.locate_and_load_manifest(f"{bucket_to_use}/{mod_name}")
		else:
			manifest, b = module.locate_and_load_manifest(mod_name)
		if not manifest:
			if bucket_to_use:
				print(f"Error: Module {mod_name} could not be located in bucket {bucket_to_use}.")
			else:
				print(f"Error: Module {mod_name} could not be located in any active bucket.")
			continue
		mod_version = manifest.version or "0.0.0"
		url_or_path = manifest.url
		bucket_name = b.name
		target_path = os.path.join(include_dir, mod_name)
		zip_payload_path = None
		installed = False
		if manifest.depends and len(manifest.depends) != 0:
			print("Downloading required dependencies...")
			for x in manifest.depends:
				if x.lower() == mod_name.lower(): continue
				if x in module.get_installed_modules(): update([x])
				else: install([x], None)
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
			zip_filename = f"{mod_name}-{mod_version}.zip"
			zip_payload_path = os.path.join(paths.CACHE_DIR, zip_filename)
			if force_update and os.path.exists(zip_payload_path):
				os.remove(zip_payload_path)
			try:
				head = requests.head(url_or_path, timeout=15, headers={"User-Agent": "NVGTPM-Package-Manager-Client"}, allow_redirects=True)
				head.raise_for_status()
				content_length = int(head.headers.get("Content-Length", 0))
				size_str = helper.convert_size(content_length) if content_length > 0 else "size unknown"
				print(f"Downloading release archive for {mod_name} ({size_str}) from {bucket_name} bucket...")
			except Exception:
				print(f"Downloading release archive for {mod_name} from {bucket_name} bucket...")
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
			print(f"Successfully installed {mod_name} {mod_version}")
			info_path = os.path.join(target_path, "info.json")
			manifest_path = b.make_path(mod_name)
			try:
				with open(manifest_path, "r", encoding="utf-8") as f:
					manifest_data = json.load(f)
				manifest_data["bucket"] = bucket_name
				with open(info_path, "w", encoding="utf-8") as f:
					json.dump(manifest_data, f, indent=2)
			except Exception as e:
				print(f"Warning: install succeeded but failed to write manifest: {e}")
			finally:
				pass
	return 0

def uninstall(args):
	module_name = args.module
	include_dir = paths.get_nvgt_include_dir()
	mod_name = module_name.lower()
	target_path = os.path.join(include_dir, mod_name)
	if os.path.exists(target_path) and os.path.isdir(target_path):
		shutil.rmtree(target_path)
		print(f"Successfully uninstalled {mod_name}")
		return 0
	else:
		print(f"Error: module {mod_name} is not currently installed.")
		return 1

def list(args):
	modules = module.get_installed_modules()
	if not modules:
		print("No modules are currently installed.")
		return 0
	print("Installed NVGT modules:")
	print("| Name | Version | bucket name | description |")
	print("|---|---|---|---|")
	for mod in sorted(modules):
		manifest = module.load_current_info(mod)
		module.show_info(mod, manifest, manifest.bucket if manifest else "unknown")
	return 0

def homepage(args):
	manifest, b = module.locate_and_load_manifest(args.name)
	if not manifest: manifest = module.load_current_info(args.name)
	if not manifest:
		print(f"module {args.name} not found.")
		return 1
	elif not manifest.homepage:
		print(f"Error: module {manifest.name or args.name} does not have ahome page URL to open.")
		return 1
	import webbrowser as w
	if not w.open(manifest.homepage):
		print(f"Error: failed to open the home page URL of module {manifest.name or args.name}")
		print("---")
		print(manifest.homepage)
		return 1
	print(f"Home page URL of {manifest.name or args.name} module opened successfully in your browser.")
	return 0

def update_command(args):
	buckets = bucket.load()
	if args.buckets:
		print("Synchronizing all remote buckets...")
		for b in buckets:
			if not b.is_local:
				bucket.sync_remote_bucket_manifests(b.name, b.source)
		if not args.modules:
			return 0
	if not args.modules:
		print("Error: Please specify a target module name, * or bucket update flags.")
		return 1
	return update(args.modules, args.force, buckets)

def update(modules, force=False, buckets=None):
	buckets = buckets or bucket.load()
	targets = []
	if modules:
		if "*" in modules:
			targets = module.get_installed_modules()
		else:
			targets = [mod.lower() for mod in modules]
	
	updates_to_perform = []
	is_wildcard = "*" in modules
	if not targets:
		print("No modules are installed.")
		return 0
	for mod in targets:
		update_info = module._check_module_update(mod, buckets, force=force)
		if update_info:
			print(f"Updating {mod}: current version {update_info['current']}, latest version {update_info['latest']} (from {update_info['bucket']} bucket)")
			updates_to_perform.append(mod)
		elif is_wildcard:
			if not module.load_current_info(mod):
				print(f"Module {mod} not installed, skipping.")
			else:
				pass
		else:
			if not module.load_current_info(mod):
				print(f"Module {mod} is not installed.")
			else:
				print(f"Module {mod} is already up to date.")
	
	if is_wildcard and not updates_to_perform:
		print("All modules are already up to date.")
		return 0
	
	if not updates_to_perform: return 0
	return install(updates_to_perform, None, force_update=True, force=force)
