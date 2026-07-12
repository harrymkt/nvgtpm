import json
import os
from string import Template
from src import github, paths

def create(args):
	name = input("Module name that is used to construct <module>.json")
	if not name:
		print("Error. Name is required.")
		return 1
	elif " " in name:
		print("Error. Module name must not contain spaces.")
		return 1
	bkrepo = input("owner/repo format of the bucket repository. Leave it empty for the main bucket")
	if not bkrepo:
		mbko, mbkr = github.parse_github_url(paths.MAIN_BUCKET_URL)
		if mbko and mbkr: bkrepo = f"{mbko}/{mbkr}"
	if not bkrepo:
		print("Error. Could not determine the bucket repository.")
		return 1
	bucket_owner, bucket_repo = github.parse_repo(bkrepo, True)
	if not bucket_owner or not bucket_repo:
		print(f"Error. Bucket owner and repository are invalid. Expected owner/repo, got \"{bkrepo}\".")
		return 1
	user = input("Your GitHub username")
	if not user:
		print("Error. You need a GitHub username.")
		return 1
	d = {
		"app_name": name,
		"bucket_repo": f"{bucket_owner}/{bucket_repo}",
		"fork_repo": f"{user}/{bucket_repo}"
	}
	content = Template(value).safe_substitute(d)
	if not content:
		print(f"Failed to create content GitHub action for {name} module.")
		return 1
	outpath = os.path.realpath(os.path.join(os.getcwd(), args.output or "submit.yaml"))
	with open(outpath, "w") as f:
		f.write(content)
		print(f"Created {os.path.basename(outpath) or outpath} in \"{outpath}\" for {name} module.")
	return 0

value = """name: Auto-Submit to Community Bucket
env:
  bucket_repo: "$bucket_repo"
  fork_repo: "$fork_repo"
  app_name: "$app_name"
on:
  push:
    branches: [main, master]
    # Triggers dynamically based on source paths
    paths: ["$app_name.json"]
  workflow_dispatch:

jobs:
  submit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Current Repository
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
          TARGET_DIR=$(dirname "bucket/json/${{ env.app_name }}.json")
          mkdir -p "$TARGET_DIR"
          # Copy the file
          cp "${{ env.app_name }}.json" "$TARGET_DIR/${{ env.app_name }}.json"
      - name: Create Pull Request to bucket
        uses: peter-evans/create-pull-request@v8
        with:
          token: ${{ secrets.PAT }}
          path: bucket
          commit-message: "Update Package Manifest of ${{ env.app_name }}"
          title: "Update Package JSON Manifest of ${{ env.app_name }}"
          branch: "app/${{ env.app_name }}"
          push-to-fork: ${{ env.fork_repo }}"""
