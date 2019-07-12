import os
import re
import ast
from setuptools import setup, find_packages


_root = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_root, "pymem/__init__.py")) as f:
    version = str(
        ast.literal_eval(
            re.search(r"__version__\s+=\s+(.*)", f.read()).group(1)
        )
    )

with open(os.path.join(_root, "requirements.txt")) as f:
    requirements = f.readlines()

with open(os.path.join(_root, "README.md")) as f:
    long_description = f.read()

setup(
    name="pymem-debugger",
    version=version,
    description="take a snapshot of Python process.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Hanaasagi",
    author_email="ambiguous404@gmail.com@gmail.com",
    py_modules=["pymem"],
    zip_safe=False,
    license="BSD",
    python_requires=">=3.6",
    url="https://github.com/Hanaasagi/pymem",
    keywords=["pymem", "memory", "gdb", "lldb", "debugger"],
    entry_points="""
    [console_scripts]
    pymem=pymem.cli:main
    """,
    install_requires=requirements,
    setup_requires=["setuptools>=38.6.0"],
    platforms=["linux", "darwin"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Utilities",
    ],
)
