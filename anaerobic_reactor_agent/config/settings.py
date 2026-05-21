"""Global configuration and environment variable loading."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"

PARAMETER_THRESHOLDS_FILE = KNOWLEDGE_DIR / "parameter_thresholds.yaml"
FAULT_RULES_FILE = KNOWLEDGE_DIR / "fault_rules.yaml"
RECOMMENDATIONS_FILE = KNOWLEDGE_DIR / "recommendations.yaml"

LOG_FILE = Path(os.getenv("ANAEROBIC_AGENT_LOG", str(PROJECT_ROOT / "anaerobic_agent.log")))
LOG_LEVEL = os.getenv("ANAEROBIC_AGENT_LOG_LEVEL", "INFO")

SUPPORTED_REACTOR_TYPES = ["UASB", "CSTR", "EGSB", "IC", "AnMBR"]

# ===== LLM API Keys =====
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# ===== LLM Settings =====
LLM_DEFAULT_MODEL = os.getenv("ANAEROBIC_AGENT_LLM_MODEL", "claude-sonnet-4-6")
LLM_DEFAULT_PROVIDER = os.getenv("ANAEROBIC_AGENT_LLM_PROVIDER", "")  # auto-detect if empty
LLM_TIMEOUT_SECONDS = int(os.getenv("ANAEROBIC_AGENT_LLM_TIMEOUT", "30"))
