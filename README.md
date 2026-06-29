# NVGTPM
A command-line package manager for [NVGT](https://nvgt.dev) include scripts. NVGTPM lets you install, update, and manage reusable NVGT modules from remote GitHub buckets or local directories without manually copying files.

NVGTPM tracks installed packages, resolves dependencies from bucket manifests, and syncs updates directly into NVGT's `include/` directory.

[Package and Bucket Creation Developer Guide](guide.md)

## Help
```bash
nvgtpm --help
```

Note: if you are running NVGTPM from source, use `python nvgtpm.py <command>`

## Usage
Use `nvgtpm --help`, or `nvgtpm -h`, to view a list of commands which may contain commands that are not yet documented here.

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
### Clearing cache
Remove all cached zip files downloaded during package installations.

```bash
nvgtpm cleanup
```
