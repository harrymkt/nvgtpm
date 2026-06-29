# NVGTPM Guide
This guide covers creating buckets and packages for NVGTPM. These are the structural standards for building packages that NVGTPM can discover, install, and update.

---

## Repository Layout
To make a GitHub repo work as a bucket, add a `json/` folder at its root with individual package manifests:

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

---

## Manifest Schema (`package.json`)
Each package manifest is a JSON file named `<package_name>.json` inside the `json/` directory. Note: you can also use `nvgtpm create` to create a package, which will bring up an interactive input fields.

| Key | Type | Description | Required |
| --- | --- | --- | --- |
| `version` | String | Release version, i.e. `"1.2.0"`. Used to detect updates. You can also use as build number if you wish, i.e. `"yyyy.mm.dd"`, `"1970-01-15"`. | Yes |
| `description` | String | Brief summary of the package. | No |
| `url` | String | Remote HTTPS zip URL, local zip path, or relative directory path. | Yes |
| `extract_dir` | String | Folder name inside `nvgt/include/`. Defaults to package name if omitted. | No |

---

## Packaging Scenarios
Choose the right URL format based on how you are distributing the package.

### Remote Public Releases (GitHub)
Point `url` directly to a compressed archive or GitHub release asset:

```json
{
  "version": "2.1.0",
  "description": "Test framework",
  "url": "https://github.com/your-username/test/releases/download/v2.1.0/test-v2.1.0.zip"
}
```

### Local Zip Asset
Track a local zip file without hosting it online. The path is relative to the bucket root:

```json
{
  "version": "1.0.4",
  "description": "Test framework",
  "url": "archives/test_v104.zip"
}
```

### Uncompressed Directory Sync
If `url` points to an uncompressed local directory, NVGTPM bypasses zip extraction and syncs the folder directly into the NVGT `include/` directory. Best for active development:

```json
{
  "version": "0.9.0",
  "description": "Direct workspace mirroring.",
  "url": "../src/test"
}
```

---

## Testing a Custom Bucket
Register and run your bucket locally before publishing:

```bash
nvgtpm bucket add workspace-test D:/Development/MyLocalbucket
nvgtpm install test
nvgtpm list
```

---

## Package Zip Contents
Each package zip must contain an entry point named **main.nvgt** so it can be used with `#include "<name>/main.nvgt"`. If you use a different entry point name, document it in the package. However, using different name other than **main.nvgt** is generally not recommended.

A package can contain multiple scripts and subdirectories.
