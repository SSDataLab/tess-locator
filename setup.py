#!/usr/bin/env python

# This is a shim setup.py file which only serves the purpose of allowing us
# to do an editable install during development.
# cf. https://snarky.ca/what-the-heck-is-pyproject-toml/

import setuptools

if __name__ == "__main__":
    setuptools.setup(name='tess_locator',
                     use_scm_version=True,
                     setup_requires=["setuptools_scm"],
                     packages=setuptools.find_packages(where="src"),
                     package_dir={"": "src"},
                     include_package_data=True)
