"""Blog content generation agent - Clean implementation"""

from typing import AsyncIterator, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory

from backend.config import settings


class BlogContentAgent:
    """Blog content generation agent using LangChain"""

    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
    ):
        """Initialize the agent with LLM configuration."""
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.llm = self._create_llm(llm_provider, llm_model, temperature)
        self.session_histories: Dict[str, ChatMessageHistory] = {}

    def _create_llm(self, provider: str, model: str, temperature: float):
        """Create LLM instance based on provider."""
        if provider == "openai":
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                streaming=True,
                api_key=self.api_key,
            )
        elif provider == "ollama":
            return ChatOllama(model=model, temperature=temperature, streaming=True)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def get_session_history(self, session_id: str) -> ChatMessageHistory:
        """Get or create session history."""
        if session_id not in self.session_histories:
            self.session_histories[session_id] = ChatMessageHistory()
        return self.session_histories[session_id]

    async def generate_content(
        self,
        prompt: str,
        session_id: str,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Generate content with streaming."""
        if system_prompt is None:
            system_prompt = """You are an expert blog content writer. Generate well-structured, 
engaging blog content based on the user's instructions. Use markdown formatting with proper 
headings, paragraphs, and bullet points where appropriate."""

        history = self.get_session_history(session_id)
        
        messages = [
            SystemMessage(content=system_prompt),
            *history.messages,
            HumanMessage(content=prompt),
        ]

        history.add_user_message(prompt)
        
        full_response = ""
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content

        history.add_ai_message(full_response)

    async def refine_content(
        self,
        current_content: str,
        feedback: str,
        session_id: str,
    ) -> AsyncIterator[str]:
        """Refine existing content based on feedback."""
        system_prompt = """You are an expert blog editor. Refine and improve the provided blog 
content based on the user's feedback. Maintain the overall structure while making the 
requested improvements. Output the complete refined content in markdown format."""

        prompt = f"""Current blog content:
{current_content}

User feedback/instructions:
{feedback}

Please provide the refined blog content based on the feedback above."""

        async for chunk in self.generate_content(prompt, session_id, system_prompt):
            yield chunk
