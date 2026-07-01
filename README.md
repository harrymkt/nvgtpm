# NVGTPM
A command-line package manager for [NVGT](https://nvgt.dev) modules, known as include scripts. NVGTPM lets you install, update, and manage reusable NVGT modules from remote GitHub buckets or local directories without manually copying files.

NVGTPM tracks installed modules, resolves dependencies from bucket manifests, and syncs updates directly into NVGT's `include/` directory.

[Bucket Creation Developer Guide](bucket-guide.md)

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

#### Removing a bucket
Unregister a bucket and delete its locally cached manifest directory.
```bash
nvgtpm bucket rm <name>
```

#### Listing registered buckets
Show all active buckets that NVGTPM currently uses to resolve modules.
```bash
nvgtpm bucket list
```

#### Listing known buckets
Show the officially known remote buckets available for registration.
```bash
nvgtpm bucket known
```

If a bucket is present in the known buckets, you can type `nvgtpm bucket add <name>`, omitting the source.

### Installing Modules
#### Installing one or more modules
Download and install one or more modules from any active bucket into NVGT's `include/` directory.
```bash
nvgtpm install <modules>
```

Thus, if you want to install 3 modules, you would use the following command:
```bash
nvgtpm install p1 p2 p3
```

You can also specify a bucket in each module explicitly to install from specific sources:
```bash
nvgtpm install <bucket>/<module>
```

This is useful when the same module name exists in multiple buckets. The installed module will be saved under `<module>` in the include directory, with its bucket recorded in `info.json`.

#### Installing modules via a requirements file
Install multiple modules at once by specifying a plain-text requirements file. Each line should contain one module name. Lines starting with `#` are treated as comments and ignored.
```bash
nvgtpm install -r nvgtpmr.txt
```

### Managing Installed Modules
#### Listing installed Modules
Show all modules currently installed in NVGT's `include/` directory, along with their versions and source buckets.
```bash
nvgtpm list
```

#### Uninstalling a module
Remove an installed modules and its directory from NVGT's `include/` folder.
```bash
nvgtpm uninstall <module>
```

#### Searching for a module
Look up modules by a given pattern across all active buckets.
```bash
nvgtpm search <pattern>
```

This means that using `nvgtpm search *` will return all modules across all active buckets.

### Updating and Maintenance
#### Checking status
```bash
nvgtpm status
```

#### Updating buckets
Refresh manifests from all remote buckets so module listings and versions are up to date.
```bash
nvgtpm update --buckets
```

#### Updating a specific module
Re-download and install a module, overwriting the currently installed version with the latest available from its bucket.
```bash
nvgtpm update <module>
```

#### Updating all modules
Update every installed module to its latest version across all buckets.
```bash
nvgtpm update *
```

### Extra
### Getting declaration syntax of a module
Retrieve the declaration syntax of a module to put in your NVGT script to be included.
```bash
nvgtpm decl <name>
```

The format returned by this command will be `#include "<module>/<f>.nvgt"`, where `<f>` is the format, either `main` or `<module>`.

Add `-c` or `--copy` option to copy the declaration syntax to clipboard as well.

### Clearing cache
Remove all cached zip files downloaded during module installations, from a given pattern.
```bash
nvgtpm cache rm <pattern>
```

Use `*` to remove all files.

## Creating a Module
### Introduction
Creating a module is relatively easy. Create a git repository, or anywhere you can host your module zip file, then contribute your `module.json` to one of the buckets, such as main.

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

### Final Step
- Add the created manifest JSON file to one of the buckets, usually on GitHub, into their json directory.
- Commit your changes to the bucket repository, and make a pull request. Wait for the module to be approved.

To update the module, edit the JSON file again with the necessary info updated like version and URL.

That's it!
