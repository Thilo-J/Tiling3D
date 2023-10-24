from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.4'
DESCRIPTION = 'Tiling solver'


# Setting up
setup(
    name="tiling3d",
    version=VERSION,
    author="Thilo Langensteiner",
    author_email="<thilo.j.la@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=open("README.md", encoding="utf-8").read(),
    project_urls = {"GitHub":"https://github.com/Thilo-J/Tiling3D"},
    url="https://github.com/Thilo-J/Tiling3D",
    
    packages=find_packages(),
    install_requires=['dxz', 'numpy', 'exact_cover', 'matplotlib'],
    keywords=['python', 'ubongo', 'tiling', '3d', 'polyomino'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)