# feature-lists

Lists of the hidden features in each Windows build: one `Name: ID` line per feature. The lists are produced with [flagscope](https://github.com/flagscope/flagscope), which reads feature names from Microsoft's public symbol files and feature IDs from the Windows binaries.

These lists let someone find a feature by name without downloading gigabytes of symbol files: a list is a few hundred kilobytes, while scanning a build downloads several gigabytes. Support in flagscope for downloading lists from this repository is planned and not released yet.

## Layout

```
<architecture>/<major build>/<major build>.<revision>.txt
```

For example, `x64/26300/26300.10075.txt` is the list for Windows build 26300.10075 on x64. There is one file per build. Only x64 is collected for now.

## File format

UTF-8 text. A few header lines start with `#`; every other line is one feature, sorted by name:

```
# flagscope feature list
# Build: 26300.10075
# Architecture: x64
# Generator: flagscope 0.1.0, full scan
# Scanned: 2026-11-26
AccountAndRegionalPolicyEnforcement: 47557358
AppDefaultHashRotation: 43229420
```

Apart from the `#` header lines, this is the line format of mach2's feature lists.

## Using a list

Find the file for your build. `winver` shows the build, for example "OS Build 26300.10075". Feature IDs can be enabled or disabled with ViVeTool or, later, with flagscope. Changing feature states can make Windows unstable: know how to revert a change before making it.

## Contributing a list

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: scan your build with flagscope, add the file it writes, and open a pull request.

## License

The lists are dedicated to the public domain under [CC0-1.0](LICENSE). Feature names and IDs come from Microsoft's public symbol files and Windows binaries; this repository is not affiliated with Microsoft.
