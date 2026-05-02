from setuptools import setup,find_packages
setup(
    name="RBAC-RAG-Appliaction",
    version="0.1.0",
    author="mithurshan",
    author_email="ldotmiturshan222@gamil.com",
    packages=find_packages(include=["src", "src.*", "utils", "utils.*"])
)