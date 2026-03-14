from llm.prompt_builder import build_chat_prompt


class OllamaClient:
    def __init__(self, base_url: str, model_name: str) -> None:
        self.base_url = base_url
        self.model_name = model_name

    async def generate_chat_response(self, message: str, context, verses) -> str:
        prompt = build_chat_prompt(message=message, context=context, verses=verses)
        _ = prompt
        return (
            "It sounds like something important is weighing on you. "
            "A useful starting point may be to focus on the action that is yours today, "
            "rather than trying to control every outcome. "
            "What is one small action you can take with sincerity right now?"
        )

    async def generate_insight(self, conversation, verses) -> dict[str, str]:
        verse = verses[0] if verses else {
            "translation": "Act with steadiness and clarity.",
            "meaning": "Focus on what is within your control.",
        }
        return {
            "quote": verse["translation"],
            "meaning": verse["meaning"],
            "reflection": "Choose one action you can take today without becoming trapped by the outcome.",
        }
