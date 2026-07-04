import io
import json
import os
import re
import shutil
import requests
import zipfile
from tqdm import tqdm

def parse_github_url(url):
	"""Safely extracts username and repository name from a standard GitHub URL."""
	# Matches github.com/ followed by the first two segments cleanly
	match = re.search(r"github\.com/([^/]+)/([^/]+)", url)
	if match:
		user = match.group(1)
		repo = match.group(2)
		# Strip trailing slash if it was grabbed
		if repo.endswith("/"):
			repo = repo[:-1]
		# Strip potential .git suffixes
		if repo.endswith(".git"):
			repo = repo[:-4]
		return user, repo
	return None, None

def parse_repo(text, strict=False):
	"""Parses the owner/repo format.
	Returns owner, and repo."""
	
	lines = text.split("/")
	if not lines or len(lines) < 2: return None, None
	if strict and len(lines) != 2: return None, None
	owner, repo = lines[0], lines[1]
	return owner, repo

def is_valid_repo(text, strict=False):
	owner, repo = parse_repo(text, strict)
	return owner and repo

def download_and_extract_manifest_zip(source_url, target_bucket_dir):
	"""Downloads GitHub repo zip, extracts only json/ manifests with tqdm progress."""
	user, repo = parse_github_url(source_url)
	if not user or not repo:
		return False
	archive_url = f"https://github.com/{user}/{repo}/archive/refs/heads/main.zip"
	try:
		response = requests.get(
			archive_url,
			timeout=15,
			stream=True,
			allow_redirects=True,
			headers={"User-Agent": "NVGTPM-Package-Manager-Client"}
		)
		response.raise_for_status()
		total_size = int(response.headers.get("content-length", 0))
		chunk_size = 1024 * 8
		zip_buffer = io.BytesIO()
		with tqdm(
			total=total_size,
			unit="B",
			unit_scale=True,
			desc="Downloading bucket",
			mininterval=0.5,
			miniters=10
		) as bar:
			for chunk in response.iter_content(chunk_size=chunk_size):
				if chunk:
					zip_buffer.write(chunk)
					bar.update(len(chunk))
		zip_buffer.seek(0)
		if os.path.exists(target_bucket_dir):
			shutil.rmtree(target_bucket_dir)
		os.makedirs(target_bucket_dir, exist_ok=True)
		download_count = 0
		with zipfile.ZipFile(zip_buffer) as archive:
			for f in archive.namelist():
				if "/json/" not in f or not f.endswith(".json"): continue
				file_name = os.path.basename(f)
				if not file_name: continue
				raw_content = archive.read(f)
				manifest_data = json.loads(raw_content.decode("utf-8"))
				dest_file_path = os.path.join(target_bucket_dir, file_name)
				with open(dest_file_path, "w", encoding="utf-8") as out:
					json.dump(manifest_data, out, indent=2)
				download_count += 1
		print(f"Update complete. Fetched a total of {download_count} manifests.")
		return True
	except Exception as e:
		print(f"Error: Failed to process zip repository download: {e}")
		return False
