# PLEASE NO MORE

**PLEASE NO MORE** (or pnm for short) is a tool born out of necessity. It allows you to place an upper bound on the number of files allowed to exist in a given directory tree. If the directory is "full", pnm will silently either delete some file to make room. There are three deletion strategies which can be passed as options to pnm with `--strategy`:

- **old** will delete the oldest file in the watched directory
- **random** will delete a file from the directory at random
- **new** will simply delete the file that has just been added. This is the default behavior.