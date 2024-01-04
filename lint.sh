#!/bin/sh
pylint --rcfile=pylint.rc $@ geni > lint.out
