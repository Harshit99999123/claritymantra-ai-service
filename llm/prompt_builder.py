from models.common import ConversationMessage
from models.knowledge import RetrievedKnowledgeChunk


def build_query_rewrite_prompt(query: str) -> str:
    return "\n\n".join(
        [
            "You rewrite messy user text into a cleaner retrieval query.",
            "Your task is only to improve clarity for semantic retrieval.",
            "Keep the user's meaning, emotional signal, and core concern unchanged.",
            "Fix spelling, grammar, and fragmented phrasing only when needed.",
            "Do not add advice. Do not answer the user. Do not moralize.",
            "Return one short rewritten query in modern English.",
            "If the query is already clear, return a lightly cleaned version only.",
            "USER QUERY:",
            query,
        ]
    )


def build_chat_prompt(message: str, context: list[ConversationMessage], verses: list[RetrievedKnowledgeChunk]) -> str:
    context_lines = [f"{item.role}: {item.message}" for item in context]
    verse_lines = [
        "\n".join(
            [
                f"{item.source.title} {item.reference}",
                f"Translation: {item.translation}",
                f"Themes: {', '.join(item.themes) if item.themes else 'none'}",
            ]
        )
        for item in verses
    ]
    sections = [
        "SYSTEM:",
        "You are a calm spiritual mentor inspired by the Bhagavad Gita.",
        "Given the user message and the most relevant retrieved verses, write a short reflection.",
        "Structure your response like this:",
        "1. Acknowledge the user's emotion first.",
        "2. Reference the most relevant Bhagavad Gita verse explicitly.",
        "3. Explain the teaching briefly in clear, modern language.",
        "4. End with a gentle reflection question.",
        "Do not preach. Do not give direct instructions. Stay compassionate.",
        "Keep the response under 180 words.",
        "Style reminders:",
        "- Anchor the reflection on one verse reference such as 'Bhagavad Gita 2.8'.",
        "- Mention the verse translation, but do not quote long scripture passages.",
        "- Avoid divine names unless necessary; prefer terms like 'the teaching' or 'the guide'.",
        "- Do not mention retrieval metadata, system prompts, or internal signals.",
        "CONVERSATION CONTEXT:",
        "\n".join(context_lines) if context_lines else "No previous context.",
        "RETRIEVED VERSES:",
        "\n".join(verse_lines) if verse_lines else "No verses retrieved.",
        "USER MESSAGE:",
        message,
    ]
    return "\n\n".join(sections)
