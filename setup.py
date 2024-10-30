from setuptools import setup, find_packages

setup(
    name="systemics",
    version="0.1.11",
    packages=find_packages(),
    install_requires=["numpy"],
    extras_require={
        "face_recognition" : ["Pillow", "deepface", "tf-keras"],
        "lm" : ["openai", "pydantic"],
        "sr" : ["webrtcvad", "groq", "pydub"],
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
