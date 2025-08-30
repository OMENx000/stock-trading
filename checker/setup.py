from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "cpplcsu",  # module name (must match PYBIND11_MODULE)
        ["checker.cpp"],  # your C++ file
        include_dirs=[pybind11.get_include()],
        language="c++"
    ),
]

setup(
    name="cpplcsu",
    version="0.1",
    ext_modules=ext_modules,
)
