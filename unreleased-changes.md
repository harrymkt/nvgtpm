## New in Version 0.0.4
- Renamed package as module.
- `search` command has been rewritten to support searching for multiple module results from a given pattern.
- `description` field in `<module>.json` is now activated.
- Added `homepage` key in module manifest.
- Added `home` command to open the home page (if available) of a given module, just like `bucket home`.
- Added `-s` or `--silent` option to `cache rm` command that allows you to suppress messages of what files are being removed.
- Added `-fp` or `--fullpath` option to `cache rm` command that allows you to show full path of the files being removed.
- Added `create-ga` command to create an automated GitHub action file to push your module manifest into a specific bucket, which is main by default.
