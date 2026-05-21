from setuptools import setup, find_packages

setup(
    name="anaerobic-reactor-agent",
    version="0.1.0",
    description="Intelligent agent for anaerobic reactor monitoring, diagnosis, and recommendations",
    author="",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0",
        "click>=8.1",
        "rich>=13.0",
        "streamlit>=1.28",
        "plotly>=5.17",
        "pyyaml>=6.0",
        "python-dotenv>=1.0",
    ],
    extras_require={
        "llm": ["anthropic>=0.40.0", "openai>=1.50.0"],
        "test": ["pytest>=7.4", "pytest-cov>=4.1"],
    },
    entry_points={
        "console_scripts": [
            "anaerobic-agent=anaerobic_reactor_agent.main:main",
        ],
    },
    python_requires=">=3.10",
)
