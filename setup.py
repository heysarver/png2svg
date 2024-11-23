# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="png2svg",
    version="0.1.0",
    author="heysarver",
    author_email="your.email@example.com",
    description="Convert PNG images to SVG with advanced options",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/heysarver/png2svg",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pillow",
        "numpy",
        "opencv-python",
        "scikit-learn",
        "svgwrite",
    ],
    entry_points={
        "console_scripts": [
            "png2svg=png2svg.cli:main",
        ],
    },
)
