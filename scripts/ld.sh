#! /bin/bash
#
# ld.sh
# Copyright (C) 2016 Kovid Goyal <kovid at kovidgoyal.net>
#
# Distributed under terms of the MIT license.
#
# For some reason in the docker container python is unable to set the LD_LIBRARY_PATH environment variable

export LD_LIBRARY_PATH="$LLP"
exec "$@"

