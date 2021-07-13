#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


# https://github.com/pypa/setuptools_scm
use_scm = {"write_to": "napari_oriented_points_picker/_version.py"}
setup(use_scm_version=use_scm)
