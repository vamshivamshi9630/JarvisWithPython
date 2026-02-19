"""
LocalLLM: Offline AI Brain for JARVIS

Runs a local LLM model (TinyLlama) using ctransformers.
Automatically downloads the model on first run.
No API keys, no cloud services, fully offline.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LocalLLM:
    """
    Local language model runner for JARVIS.
    
    Uses TinyLlama-1.1B instruct model in GGUF format.
    ~1.1B parameters, ~600MB, runs on CPU.
    
    First run: Auto-downloads model (~30-60 seconds)
    Subsequent runs: Instant (offline)
    """
    
    # Model configuration
    MODEL_DIR = Path(__file__).parent.parent / "models"
    MODEL_PATH = MODEL_DIR / "tinyllama.gguf"
    MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    
    def __init__(self):
        """Initialize the local LLM, downloading model if needed."""
        self.llm = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Load or download the model."""
        self.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        
        if self.MODEL_PATH.exists():
            logger.info(f"✓ Model found: {self.MODEL_PATH.name}")
            self._load_model()
        else:
            logger.info(f"🔍 Model not found. Downloading to {self.MODEL_PATH}...")
            self._download_model()
            self._load_model()
    
    def _download_model(self):
        """Download the TinyLlama model."""
        try:
            import urllib.request
            
            logger.info("⏳ Downloading TinyLlama model (30-60 seconds)...")
            
            def download_with_progress(url, filepath):
                class ProgressBar:
                    def __init__(self):
                        self.last_percent = 0
                    
                    def __call__(self, block_num, block_size, total_size):
                        if total_size == -1:
                            return
                        downloaded = block_num * block_size
                        percent = min(100, int((downloaded / total_size) * 100)) if total_size > 0 else 0
                        if percent >= self.last_percent + 10:
                            logger.info(f"   {percent}%")
                            self.last_percent = percent
                
                urllib.request.urlretrieve(url, filepath, ProgressBar())
            
            download_with_progress(self.MODEL_URL, self.MODEL_PATH)
            logger.info("✓ Model downloaded")
            
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            raise
    
    def _load_model(self):
        """Load the model using ctransformers."""
        try:
            try:
                from ctransformers import AutoModelForCausalLM
            except ImportError:
                logger.info("📦 Installing ctransformers...")
                import subprocess
                subprocess.check_call(["pip", "install", "ctransformers", "-q"])
                from ctransformers import AutoModelForCausalLM
            
            logger.info(f"🧠 Loading {self.MODEL_PATH.name}...")
            
            self.llm = AutoModelForCausalLM.from_pretrained(
                str(self.MODEL_PATH),
                model_type="llama",
                gpu_layers=0,
                threads=6,
                context_length=1024
            )
            
            logger.info("✓ LLM ready (offline)")
            
        except Exception as e:
            logger.error(f"❌ Load failed: {e}")
            raise
    
    def generate(
        self,
        system_prompt: str,
        user_input: str,
        max_tokens: int = 120,
    ) -> str:
        """
        Generate response from local model using ctransformers native API.
        
        Args:
            system_prompt: System instruction
            user_input: User query
            max_tokens: Max response length
            
        Returns:
            Model response as string
        """
        if not self.llm:
            logger.error("Model not loaded")
            return ""
        
        try:
            # Build plain text prompt (ctransformers expects simple text, not chat format)
            prompt = f"""{system_prompt}

User Request:
{user_input}

Response:"""
            
            # Call model using ONLY ctransformers native API
            # ctransformers GGUF models expect: model(prompt, max_new_tokens=N)
            # Do NOT use: max_tokens, temperature, top_p, or generate()
            response = self.llm(
                prompt,
                max_new_tokens=max_tokens,
                temperature=0.2,
                stop=["</s>"]
            )
            
            # Convert response to string
            response_text = str(response).strip()
            
            if not response_text:
                logger.warning("LLM returned empty response")
                return ""
            
            return response_text
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return ""
    
    def plan(
        self,
        user_input: str,
        available_tools: str,
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Generate structured action plan.
        
        Returns:
            Plan dict with goal and steps
        """
        system_prompt = f"""You are a computer automation planning engine.
Do NOT chat. Produce ONLY valid JSON.
Break down requests into steps using available tools.

Available tools:
{available_tools}

Return ONLY this JSON format (no markdown, no explanation):
{{"goal": "...", "steps": [{{"tool": "...", "parameters": {{}}, "reason": "..."}}]}}"""
        
        if context:
            system_prompt += f"\n\nContext: {context}"
        
        user_prompt = f"Create action plan for: {user_input}"
        response = self.generate(system_prompt, user_prompt, max_tokens=1000)
        
        try:
            if "{" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
            else:
                json_str = response
            
            plan = json.loads(json_str)
            
            if "goal" not in plan:
                plan["goal"] = "Execute"
            if "steps" not in plan or not isinstance(plan["steps"], list):
                plan["steps"] = []
            
            return plan
            
        except json.JSONDecodeError:
            logger.warning(f"⚠️ Plan parse failed")
            return {"goal": "Request", "steps": []}


# Global instance
_local_llm = None


def get_local_llm() -> LocalLLM:
    """Get or create global LocalLLM instance."""
    global _local_llm
    if _local_llm is None:
        _local_llm = LocalLLM()
    return _local_llm

