# NVGTPM Bucket Creation Guide
This guide covers creating buckets for NVGTPM. These are the structural standards for building modules that NVGTPM can discover, install, and update.

## Repository Layout
To make a GitHub repository work as a bucket, add a `json/` folder at its root with individual module manifests:
```text
your-bucket-repo/
	README.md
	json/
		test.json
```

For local testing, create a parent folder with a `json/` directory inside:
```text
D:/Development/MyLocalbucket/
	json/
		test.json
```

## Testing a Custom Bucket
Register and run your bucket locally before publishing:
```bash
nvgtpm bucket add workspace-test D:/Development/MyLocalbucket
nvgtpm install test
nvgtpm list
```
