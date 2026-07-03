import json
import sys
from src import github, paths

def create(args):
	name = input("Module name that is used to construct <module>.json")
	if not name:
		print("Error. Name is required.")
		sys.exit(1)
		return
	elif " " in name:
		print("Error. Module name must not contain spaces.")
		sys.exit(1)
		return
	bkrepo = input("owner/repo format of the bucket repository. Leave it empty for the main bucket")
	if not bkrepo:
		mbko, mbkr = github.parse_github_url(paths.main_bucket_url)
		bkrepo = f"{mbko}/{mbkr}"
	if not bkrepo:
		print("Error. Bucket repository cannot be determined.")
		sys.exit(1)
		return
	bucket_owner, bucket_repo = github.parse_repo(bkrepo, True)
	if not bucket_owner or not bucket_repo:
		print(f"Error. Bucket owner and repository are invalid. Expected owner/repo, got \"{bkrepo}\".")
		sys.exit(1)
		return
	user = input("Your GitHub username")
	if not user:
		print("Error. You need a GitHub username.")
		sys.exit(1)
		return
	d = {
		"app_name": name,
		"bucket_repo": f"{bucket_owner}/{bucket_repo}",
		"fork_repo": f"{user}/{bucket_repo}"
	}
	content = value.format(**d)
	if not content:
		print(f"Failed to create content GitHub action for {name} module.")
		sys.exit(1)
		return
	with open("submit.yaml", "w") as f:
		f.write(content)
		print(f"Created submit.yaml for {name} module.")

value = """name: Auto-Submit to Community Bucket
env:
  bucket_repo: "{bucket_repo}"
  fork_repo: "{fork_repo}"
  app_name: "{app_name}"
on:
  push:
    branches: [main, master]
    # Triggers dynamically based on source path
    paths: ["${{ env.app_name }}"]
  workflow_dispatch:

jobs:
  submit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Current Repo
        uses: actions/checkout@v7
      - name: Checkout Bucket Upstream
        uses: actions/checkout@v7
        with:
          repository: ${{ env.bucket_repo }}
          token: ${{ secrets.PAT }}
          path: bucket
      - name: Add JSON into Bucket Directory
        run: |
          # Dynamically extract the directory path from the target file path
          TARGET_DIR=$(dirname "bucket/${{ env.app_name }}.json")
          mkdir -p "$TARGET_DIR"
          # Copy the file
          cp "${{ env.app_name }}.json" "bucket/${{ env.app_name }}.json"
      - name: Create Pull Request via Auto-Fork
        uses: peter-evans/create-pull-request@v8
        with:
          token: ${{ secrets.PAT }}
          path: bucket
          commit-message: "Update Package Manifest of ${{ env.app_name }}"
          title: "Update Package JSON Manifest of ${{ env.app_name }}"
          branch: "app/${{ env.app_name }}"
          push-to-fork: ${{ env.fork_repo }}"""
