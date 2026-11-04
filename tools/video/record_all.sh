#!/bin/sh
# Re-record every chapter's video, a few at a time. Run from the course folder.
# usage: sh tools/video/record_all.sh PYTHON
ls -d chapters/*/video/scenes.json | xargs -n1 dirname | xargs -n1 dirname |
  xargs -P 5 -I{} sh -c "$1 tools/video/record.py {} {}/media && echo done {}"
