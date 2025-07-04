import setuptools

with open("README.md") as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    requirements = [line.rstrip("\n") for line in fh.readlines() if line != ""]

setuptools.setup(
    name="sc-compression",
    version="0.6.6",
    author="Vorono4ka",
    author_email="crowo4ka@gmail.com",
    description="SC Compression",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xcoder-tool/sc-compression",
    license="GPLv3",
    entry_points={
        "console_scripts": ["sc-compression=sc_compression.__main__:main"],
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
    install_requires=requirements,
    package_data={
        "": ["support/lzham.exe"],
    },
)
