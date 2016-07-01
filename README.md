Code to build all calibre dependencies
==========================================

Linux
-------

You need to have docker installed and running as the linux
build are done in a docker container.

To build the 64bit and 32bit dependencies for calibre, run:

```
./linux 64
./linux 32
```

The output (after a very long time) will be in `build/linux[32|63]`
