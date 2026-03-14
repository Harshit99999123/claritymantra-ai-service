from models.common import ConversationMessage


def build_chat_prompt(message: str, context: list[ConversationMessage], verses: list[dict[str, str]]) -> str:
    context_lines = [f"{item.role}: {item.message}" for item in context]
    verse_lines = [f"BG {item['chapter']}.{item['verse']}: {item['translation']}" for item in verses]
    sections = [
        "You are a calm philosophical reflection mentor.",
        "Do not preach, impersonate Krishna, or claim therapeutic authority.",
        "Acknowledge emotion, introduce a relevant principle, ground it in Bhagavad Gita teaching, explain in modern language, and end with a reflection prompt.",
        "Context:",
        "\n".join(context_lines) if context_lines else "No previous context.",
        "Retrieved teachings:",
        "\n".join(verse_lines) if verse_lines else "No verses retrieved.",
        f"User concern: {message}",
    ]
    return "\n\n".join(sections)
