# Config for ast-grep

Contains rule definition files for [ast-grep](https://ast-grep.github.io/) to
check for various code conventions and fix them, if possible.

To run, install the `ast-grep` package and run from the repository root:

    sg scan -c tools/fixups/config

Add `-U` to apply auto-fixes or `-i` to fix interactively.

## Writing new rules

There is some good documentation at
https://ast-grep.github.io/guide/rule-config.html and an interactive playground
at https://ast-grep.github.io/playground.html
