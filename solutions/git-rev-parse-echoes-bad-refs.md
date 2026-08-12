---
title: git rev-parse echoes bad refs to stdout
tags: [git, python]
projects: [clutch]
date: 2026-07-28
---

## Problem

`git rev-parse SOMEREF` prints SOMEREF to stdout even when the ref does not exist.

## Root cause

Without --verify, rev-parse passes unknown args through for use as pathspecs.

## Solution

Use `git rev-parse --verify --quiet REF` - empty stdout and exit 1 on failure.

## Notes

Bit us in .clutch history.py fallback logic.
