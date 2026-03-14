class EmbeddingService:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    async def embed(self, text: str) -> list[float]:
        # Placeholder embedding to keep the interface stable before real model integration.
        size = min(len(text), 8)
        return [float((ord(char) % 32) / 31.0) for char in text[:size]]
