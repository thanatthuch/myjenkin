from setuptools import find_packages, setup

requirements = [
    "pytest<7,>=5",
    "pytest-timeout",
]

setup(
    name="dimensional-modelling",
    version="1.0.0",
    author="thanatthuch",
    author_email="thanatthuch.cu@gmail.com.com",
    packages=find_packages(),
    package_data={"app": ["tables/*.csv"], "verify_pack": ["tables/*.csv"]},
    install_requires=["numpy", "pandas"],
    tests_require=requirements,
    setup_requires=["pytest-runner"],
    extras_require={"dev": ["black"]},
)
