import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="overcloud", # Replace with your own username
    version="0.0.1",
    author="Nikola Bebić",
    author_email="nikola.bebic99@gmail.com",
    description="a simple way to make clouds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/profMagija/overcloud",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            "overcloud = overcloud.cli:main"
        ]
    }
)