from setuptools import setup,find_packages
setup(
    name="RBAC-RAG-Application",
    version="1.0.0",
    author="mithurshan",
    author_email="ldotmiturshan222@gmail.com",
    description="Role-Based Access Control RAG System with hybrid retrieval",
    packages=find_packages(include=["src", "src.*", "utils", "utils.*", "backend", "backend.*", "frontend", "frontend.*"])
)