class InMemoryVectorStore:
    def __init__(self) -> None:
        self._documents = [
            {
                "chapter": "2",
                "verse": "47",
                "translation": "You have a right to perform your prescribed duty, but not to the fruits of action.",
                "meaning": "Focus on action without attachment to outcomes.",
            }
        ]

    async def search(self, embedding: list[float], top_k: int = 5) -> list[dict[str, str]]:
        return self._documents[:top_k]
