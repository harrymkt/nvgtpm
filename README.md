# NVGTPM
A command-line package manager for [NVGT](https://nvgt.dev) modules, known as include scripts. NVGTPM lets you install, update, and manage reusable NVGT modules from remote GitHub buckets or local directories without manually copying files.

NVGTPM tracks installed modules, resolves dependencies from bucket manifests, and syncs updates directly into NVGT's `include/` directory.

Note: this repository is the main source of the package manager, not a repository to contribute modules.

If you are looking forward to creating a bucket, see [bucket creation developer guide](bucket-guide.md).

## Usage
Use `nvgtpm --help`, or `nvgtpm -h`, to view a list of commands which may contain commands that are not yet documented here. For help on a specific command, use `nvgtpm <command> --help` or just `nvgtpm <command> -h`.

Note: if you are running NVGTPM from source, use `python nvgtpm.py <command>` up to the root of the repository of directory containing the script.

### Managing Buckets
Buckets are sources of modules. A bucket can be a local directory or a remote GitHub repository that exposes a `json/` folder containing module manifests.

By default, [`main` bucket](https://github.com/harrymkt/nvgtpm_bucket_main) is added.

#### Adding a bucket
Register a new bucket so NVGTPM can discover its modules. The source can be a local folder path or a GitHub HTTPS URL.
```bash
nvgtpm bucket add <name> <source>
```

If a bucket is present in the known buckets, you can type `nvgtpm bucket add <name>`, omitting the source.

## Creating a Module
### Introduction
Creating a module is relatively easy. Create a git repository, or anywhere you can host your module zip file, then contribute your `<module>.json` to one of the buckets, such as main.

### Zip and upload your module to your host
Each module zip must contain an entry point named `main.nvgt` or `<module>.nvgt` so it can be used with `#include "<name>/<f>.nvgt"`. If you use a different entry point name, document it in the module. However, using different name other than `main.nvgt` and `<module>.nvgt` is generally not recommended.

A module can contain multiple scripts and subdirectories.

### Create Manifest Schema (`<module>.json`)
Each module manifest is a JSON file named `<module>.json`.

Note: you can also use `nvgtpm create` to create a module, which will bring up an interactive input fields.

| Key | Type | Description | Required |
| --- | --- | --- | --- |
| `version` | String | Release version, i.e. `"1.2.0"`. Used to detect updates. You can also use as build number if you wish, i.e. `"yyyy.mm.dd"`, `"1970.01.15"`. | Yes |
| `description` | String | Brief summary of the module. | No |
| `url` | String | Remote HTTPS zip URL, local zip path, or relative directory path. | Yes |
| `homepage` | String | A link to the website, or the GitHub repository, of the module. | No |

### Final Step
- Add the created manifest JSON file to one of the buckets, usually on GitHub, such as [main](https://github.com/harrymkt/nvgtpm_bucket_main), into their json directory.
- Commit your changes to the bucket repository, and make a pull request. Wait for the module to be approved.

To update the module, edit the JSON file again with the necessary info updated like version and URL.

That's it!
