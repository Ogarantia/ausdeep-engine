import setuptools
import codecs

setuptools.setup(
    name="upstride",
    version="1.1.1",
    author="UpStride S.A.S",
    author_email="hello@upstride.io",
    description="",
    long_description='',
    long_description_content_type="text/markdown",
    url="https://upstride.io",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={'': ['_upstride_ops.so']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    # test_suite="",
    # tests_require=[''],
    install_requires=['pydot', 'graphviz']
)
