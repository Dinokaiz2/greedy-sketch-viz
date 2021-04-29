import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="greedy_sketch",
    version="0.1.0",
    author=", ".join(["Kaiz Akhtar", "Eli W. Hunter", "Siddharth Sheth"]),
    author_email=", ".join(
        ["kaizakhtar@gmail.com", "elihunter173@gmail.com", "siddharths.iift@gmail.com"]
    ),
    description="Web-based visualizations for persim",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dinokaiz2/greedy-sketch-viz",
    install_requires=[
        "persim",
        "matplotlib",
        "numpy",
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
