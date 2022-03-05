import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyglowmarkt",
    version="0.5.3",
    author="Cybermaggedon",
    author_email="mark@cyberapocalypse.co.uk",
    description="Python API for accessing Hildebrand/Glowmarkt/Bright API to smart meter data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cybermaggedon/pyglowmarkt",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    download_url = "https://github.com/cybermaggedon/pyglowmarkt/archive/refs/tags/v0.5.2.tar.gz",
    install_requires=[
        "requests", "paho-mqtt"
    ],
    scripts=[
        "scripts/glowmarkt-dump",
        "scripts/glowmarkt-csv",
        "scripts/glowmarkt-today",
        "scripts/glowmarkt-mqtt",
    ]
)
