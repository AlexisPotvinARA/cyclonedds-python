#!/usr/bin/env python

"""
 * Copyright(c) 2022 ZettaScale Technology and others
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v. 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0, or the Eclipse Distribution License
 * v. 1.0 which is available at
 * http://www.eclipse.org/org/documents/edl-v10.php.
 *
 * SPDX-License-Identifier: EPL-2.0 OR BSD-3-Clause
"""

import os
import sys
from pathlib import Path
from setuptools import setup, Extension, find_packages

this_directory = Path(__file__).resolve().parent
sys.path.insert(0, str(this_directory / 'buildhelp'))

from cyclone_search import find_cyclonedds
from build_ext import build_ext, Library
from bdist_wheel import bdist_wheel


__version__ = "0.11.0"
package = "cyclonedds"


with open(this_directory / 'README.md', encoding='utf-8') as f:
    long_description = f.read()


if "BUILDING_SDIST" not in os.environ:
    cyclone = find_cyclonedds()

    if not cyclone:
        print("Could not locate cyclonedds. Try to set CYCLONEDDS_HOME or CMAKE_PREFIX_PATH")
        import sys
        sys.exit(1)


    if "PYOXIDIZER" in os.environ:
        (this_directory / 'cyclonedds' / '__library__.py').write_text((this_directory / 'buildhelp' / 'oxidize_library.py').read_text())
    else:
        with open(this_directory / 'cyclonedds' / '__library__.py', "w", encoding='utf-8') as f:
            f.write("in_wheel = False\n")
            f.write(f"library_path = r'{cyclone.ddsc_library}'\n")

    ext_modules = [
        Extension('cyclonedds._clayer', [
                'clayer/pysertype.c'
            ],
            include_dirs=[
                str(cyclone.include_path),
                str(this_directory / "clayer")
            ],
            libraries=['ddsc'],
            library_dirs=[
                str(cyclone.library_path),
                str(cyclone.binary_path),
            ]
        )
    ]

    if cyclone.idlc_library:
        ext_modules += [
            Library('cyclonedds._idlpy', [
                    'idlpy/src/context.c',
                    'idlpy/src/generator.c',
                    'idlpy/src/naming.c',
                    'idlpy/src/ssos.c',
                    'idlpy/src/types.c',
                    'idlpy/src/util.c'
                ],
                include_dirs=[
                    str(cyclone.include_path),
                    str(this_directory / "idlpy" / "include")
                ],
                libraries=['ddsc', 'cycloneddsidl'],
                library_dirs=[
                    str(cyclone.library_path),
                    str(cyclone.binary_path)
                ]
            )
        ]
else:
    ext_modules=[]


setup(
    name=package,
    version=__version__,
    description='Eclipse Cyclone DDS Python binding',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Eclipse Cyclone DDS Committers',
    maintainer='Thijs Miedema',
    maintainer_email='thijs.miedema@zettascale.tech',
    url="https://cyclonedds.io",
    project_urls={
        "Documentation": "https://cyclonedds.io/docs",
        "Source Code": "https://github.com/eclipse-cyclonedds/cyclonedds-python",
        "Bug Tracker": "https://github.com/eclipse-cyclonedds/cyclonedds-python/issues"
    },
    license="EPL-2.0, BSD-3-Clause",
    platforms=["Windows", "Linux", "Mac OS-X", "Unix"],
    keywords=[
        "eclipse", "cyclone", "dds", "pub", "sub",
        "pubsub", "iot", "cyclonedds", "cdr", "omg",
        "idl", "middleware", "ros"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(".", include=("cyclonedds", "cyclonedds.*")),
    package_data={
        "cyclonedds": ["*.so", "*.dylib", "*.dll", "idlc*", "*py.typed"],
        "cyclonedds.idl": ["py.typed"]
    },
    ext_modules=ext_modules,
    cmdclass={
        'bdist_wheel': bdist_wheel,
        'build_ext': build_ext,
    },
    entry_points={
        "console_scripts": [
            "ddsls=cyclonedds.tools.ddsls:command",
            "pubsub=cyclonedds.tools.pubsub:command",
            "cyclonedds=cyclonedds.tools.cli.main:cli"
        ],
    },
    python_requires='>=3.9',
    install_requires=[
        "typing-inspect>=0.6;python_version<'3.7'",
        "typing-extensions>=3.7;python_version<'3.9'",
        "rich-click"
    ],
    extras_require={
        "dev": [
            "pytest>=6.2",
            "pytest-asyncio",
            "pytest-cov",
            "pytest-mock",
            "flake8",
            "flake8-bugbear",
            "twine"
        ],
        "docs": [
            "Sphinx>=4.0.0",
            "piccolo_theme>=0.12.0"
        ]
    },
    zip_safe=False
)
