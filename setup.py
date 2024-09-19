from setuptools import setup, find_packages

setup(
    name="systemics",
    version="0.0.7",
    packages=find_packages(),
    install_requires=[        
    ],
    extras_require={
        "lm" : ["openai", "pydantic"],
    },
    author="HaShaWB",
    author_email="whitebluej@kaist.ac.kr",
    description="AI system for general agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/HaShaWB/systemics",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
