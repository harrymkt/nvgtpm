# NVGTPM
A command-line package manager for [NVGT](https://nvgt.dev) include scripts. NVGTPM lets you install, update, and manage reusable NVGT modules from remote GitHub buckets or local directories without manually copying files.

NVGTPM tracks installed packages, resolves dependencies from bucket manifests, and syncs updates directly into NVGT's `include/` directory.

[Bucket Creation Developer Guide](bucket-guide.md)

## Usage
Use `nvgtpm --help`, or `nvgtpm -h`, to view a list of commands which may contain commands that are not yet documented here.

Note: if you are running NVGTPM from source, use `python nvgtpm.py <command>`

### Managing Buckets
Buckets are sources of packages. A bucket can be a local directory or a remote GitHub repository that exposes a `json/` folder containing package manifests.

By default, [`main` bucket](https://github.com/harrymkt/nvgtpm_bucket_main) is added.

#### Adding a bucket
Register a new bucket so NVGTPM can discover its packages. The source can be a local folder path or a GitHub HTTPS URL.

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
Show all active buckets that NVGTPM currently uses to resolve packages.

```bash
nvgtpm bucket list
```

#### Listing known buckets
Show the officially known remote buckets available for registration.

```bash
nvgtpm bucket known
```

If a bucket is present in the known buckets, you can type `nvgtpm bucket add <name>`, omitting the source.

### Installing Packages
#### Installing a package
Download and install a single package from any active bucket into NVGT's `include/` directory.

```bash
nvgtpm install <package>
```

You can also specify a bucket explicitly to install a package from a specific source:

```bash
nvgtpm install <bucket>/<package>
```

This is useful when the same package name exists in multiple buckets. The installed package will be saved under `<package>` in the include directory, with its bucket recorded in `info.json`.

#### Installing packages via a requirements file
Install multiple packages at once by specifying a plain-text requirements file. Each line should contain one package name. Lines starting with `#` are treated as comments and ignored.

```bash
nvgtpm install -r nvgtpmr.txt
```

### Managing Installed Packages
#### Listing installed packages
Show all packages currently installed in NVGT's `include/` directory, along with their versions and source buckets.

```bash
nvgtpm list
```

#### Uninstalling a package
Remove an installed package and its directory from NVGT's `include/` folder.

```bash
nvgtpm uninstall <package>
```

#### Searching for a package
Look up a package by name across all active buckets.

```bash
nvgtpm search <package>
```

### Updating and Maintenance
#### Checking status
```bash
nvgtpm status
```

#### Updating buckets
Refresh manifests from all remote buckets so package listings and versions are up to date.

```bash
nvgtpm update --buckets
```

#### Updating a specific package
Re-download and install a package, overwriting the currently installed version with the latest available from its bucket.

```bash
nvgtpm update <package>
```

#### Updating all packages
Update every installed package to its latest version across all buckets.

```bash
nvgtpm update *
```

### Extra
### Getting declaration syntax of a package
Retrieve the declaration syntax of a package to put in your NVGT script to be included.

```bash
nvgtpm decl <name>
```

The format returned by this command will be `#include "<package_name>/<f>.nvgt"`, where `<f>` is the format, either `main` or `<package_name>`.

### Clearing cache
Remove all cached zip files downloaded during package installations.

```bash
nvgtpm cleanup
```

## Creating a Package
### Introduction
Creating a package is easy. Create a git repository, or anywhere you can host your package zip file, then contribute your `package_name.json` to one of the buckets, such as main.

### Zip and upload your package to your host
Each package zip must contain an entry point named `main.nvgt` or `<package_name>.nvgt` so it can be used with `#include "<name>/<f>.nvgt"`. If you use a different entry point name, document it in the package. However, using different name other than `main.nvgt` and `<package_name>.nvgt` is generally not recommended.

A package can contain multiple scripts and subdirectories.

### Create Manifest Schema (`package.json`)
Each package manifest is a JSON file named `<package_name>.json`. Note: you can also use `nvgtpm create` to create a package, which will bring up an interactive input fields.

| Key | Type | Description | Required |
| --- | --- | --- | --- |
| `version` | String | Release version, i.e. `"1.2.0"`. Used to detect updates. You can also use as build number if you wish, i.e. `"yyyy.mm.dd"`, `"1970.01.15"`. | Yes |
| `description` | String | Brief summary of the package. | No |
| `url` | String | Remote HTTPS zip URL, local zip path, or relative directory path. | Yes |
| `extract_dir` | String | Folder name inside `nvgt/include/`. Defaults to package name if omitted. | No |

### Final Step
- Add the created manifest JSON file to one of the buckets, usually on GitHub, into their json directory.
- Commit your changes to the bucket repository, and make a pull request.

That's it!
