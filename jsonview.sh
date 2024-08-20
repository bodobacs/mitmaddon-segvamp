#!/bin/sh
#views json in a pretty-printed
#json library tool module

sh -c "python -m json.tool $@ | less"

