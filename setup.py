from setuptools import setup, find_packages

setup(
    name="place_cell_simulations",           
    version="0.1.0",              
    description="Repo to simulate place cells and noise neurons",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sara Molas Medina",
    url="https://github.com/SaraMolas/place-cell-simulations",
    packages=find_packages(),              # automatically find submodules
    install_requires=[
        # list dependencies here
        "matplotlib",
        "numpy",
        "scipy",
    ],
    python_requires=">=3.8",               # minimum Python version
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # or your license
        "Operating System :: OS Independent",
    ],
)
