from setuptools import setup, find_namespace_packages


setup(
    name='auto-flu',
    version='0.1.0-alpha',
    packages=find_namespace_packages(),
    entry_points={
        "console_scripts": [
            "auto-flu = auto_flu.__main__:main",
        ]
    },
    scripts=[],
    package_data={
    },
    install_requires=[
    ],
    description=' Automated analysis of flu sequence data',
    url='https://github.com/BCCDC-PHL/auto-flu',
    author='Dan Fornika',
    author_email='dan.fornika@bccdc.ca',
    include_package_data=True,
    keywords=[],
    zip_safe=False
)
