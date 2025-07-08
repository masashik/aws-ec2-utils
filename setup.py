from setuptools import setup, find_packages

setup(
    name="aws-ec2-utils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.26,<2.0",
        "click>=8.0",
        ],
    entry_points={
        "console_scripts": [
            "ec2-start=ec2_utils.ec2_start:start_ec2_instances",
            ]
        },
    python_requires=">=3.8",
    include_package_data=True,
)
