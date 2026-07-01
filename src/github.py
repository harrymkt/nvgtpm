import io
import json
import os
import re
import shutil
import requests
import zipfile

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

def download_and_extract_manifest_zip(source_url, target_bucket_dir):
	"""Downloads the repository source tree as a single compressed zip file stream, then unzips only the contents of the 'json/' directory directly into the bucket."""
	user, repo = parse_github_url(source_url)
	if not user or not repo:
		return False
	
	# GitHub's clean zip snapshot endpoint for the default bucket
	archive_url = f"https://github.com/{user}/{repo}/archive/refs/heads/main.zip"
	try:
		response = requests.get(archive_url, timeout=15, stream=True, allow_redirects=True, headers={"User-Agent": "NVGTPM-Package-Manager-Client"})
		response.raise_for_status()
		# Download the entire repository as an in-memory byte stream to prevent disk thrashing
		zip_data = io.BytesIO(response.content)
		# Clean out old local bucket directory structure completely to clear ghost packages
		if os.path.exists(target_bucket_dir):
			shutil.rmtree(target_bucket_dir)
		os.makedirs(target_bucket_dir, exist_ok=True)
		download_count = 0
		with zipfile.ZipFile(zip_data) as archive:
			for file_path in archive.namelist():
				# GitHub zips root folders as '<repo_name>-main/json/<file_name>.json'
				# Check for files inside the 'json/' directory ending with '.json'
				if "/json/" in file_path and file_path.endswith(".json"):
					file_name = os.path.basename(file_path)
					if not file_name:
						continue # Skip directory stubs
					# Extract manifest content directly and format write to disk
					raw_content = archive.read(file_path)
					manifest_data = json.loads(raw_content.decode("utf-8"))
					dest_file_path = os.path.join(target_bucket_dir, file_name)
					with open(dest_file_path, "w", encoding="utf-8") as f:
						json.dump(manifest_data, f, indent=2)
					download_count += 1
		print(f"Update complete. Fetched a total of {download_count} manifests.")
		return True
	except Exception as e:
		print(f"Error: Failed to process zip repository download: {e}")
		return False
