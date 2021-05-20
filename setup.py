from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='r2py',
    version='0.2.0',
    author="Ricardo E. Gonzalez",
    author_email="ricardog@itinerisinc.com",
    description="Compile mixed-effects R models to python modules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.8.3',
    url="https://github.com/ricardog/r2py",
    project_urls={
        "Bug Tracker": "https://github.com/ricardog/r2py/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where='src'),
    include_package_data=True,
    install_requires=[
        'Click',
        'inflection',
        'numba',
        'pandas',
        'pyparsing',
        'rpy2',
        'setuptools',
    ],
    entry_points='''
        [console_scripts]
        r2py=r2py.scripts.r2py:main
    ''',
)
