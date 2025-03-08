#!/bin/bash
cd ~/drop_file;
cat $(ls -v | grep -E '^[0-9]+$' | sort -n) > out
dd if=out of=final bs=1 count=$(($1));
md5sum final;
rm *