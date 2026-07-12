import sys
import os
import time
import platform
import tempfile
import shutil
import stat
import subprocess
import requests
import application as app
from . import cmd

def update_cmd(args):
	if "python.exe" in sys.executable:
		print("Error: this command cannot be used when running from source")
		return 1
	try:
		print("Checking latest release...")
		apiurl = f"https://api.github.com/repos/harrymkt/nvgtpm/releases/{"tags/dev" if args.dev else "latest"}"
		resp = requests.get(apiurl)
		resp.raise_for_status()
		data = resp.json()
		latest_version = data.get("tag_name")
		if not args.force and not latest_version == "dev" and latest_version == app.VERSION:
			print("Already up to date.")
			return 0
		system = platform.system().lower()
		if system == "windows":
			target = "nvgtpm.exe"
		elif system == "linux":
			target = "nvgtpm-linux"
		elif system == "darwin":
			target = "nvgtpm-macos"
		else:
			raise Exception(f"Unsupported OS: {system}")
		url = None
		for asset in data.get("assets", []):
			if asset["name"] == target:
				url = asset["browser_download_url"]
				break
		if not url:
			raise Exception("No matching binary found")
		print(f"Downloading: {url}")
		with tempfile.NamedTemporaryFile(delete=False) as tmp:
			tmp_path = tmp.name
		with requests.get(url, stream=True) as r:
			r.raise_for_status()
			with open(tmp_path, "wb") as f:
				for chunk in r.iter_content(8192):
					if chunk:
						f.write(chunk)
		current_exe = sys.executable
		print("Applying update...")
		if system == "windows":
			old_exe = f"{current_exe}.old"
			os.replace(current_exe, old_exe)
			os.replace(tmp_path, current_exe)
			subprocess.Popen([current_exe, "[applyupdatesilently]"])
		else:
			os.chmod(tmp_path, os.stat(tmp_path).st_mode | stat.S_IEXEC)
			shutil.move(tmp_path, current_exe)
			print("Update complete.")
		return 0
	except Exception as e:
		print(f"Update failed: {e}")
		return 1

def about(args=None):
	print(f"NVGTPM{" development" if app.DEV else ""} version {app.VERSION} ({app.BUILD})")
	return 0

