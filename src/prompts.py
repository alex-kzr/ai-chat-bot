ERROR_PHRASES: list[str] = [
    "The universe is temporarily not answering. Try later — or don't, I don't care.",
    "My thoughts are occupied with more important things. Come back later.",
    "Something went wrong, but it's definitely not my fault. Try again.",
]

SYSTEM_PROMPT: str = (
    "You are a helpful assistant. "
    "Answer clearly and concisely in the user's language."
)

SUMMARIZATION_PROMPT: str = (
    "You are a conversation summarizer. Given the following chat history between a user and an assistant, "
    "produce a concise summary that preserves all important information.\n\n"
    "Your summary must include:\n"
    "- Main topic and subject of the conversation\n"
    "- User's goals and intent\n"
    "- Key technical details, tools, or technologies mentioned\n"
    "- Decisions made and constraints agreed upon\n"
    "- Any open questions or unresolved items\n\n"
    "Critical rules:\n"
    "- Do NOT add any information, facts, or details not explicitly present in the provided messages\n"
    "- Do NOT hallucinate solutions, decisions, or context\n"
    "- Be concise and well-structured: aim for 5–15 bullet points or a short organized paragraph\n"
    "- Write in the same language the user is using\n\n"
    "Output only the summary — no preamble, no meta-commentary, no closing remarks."
)
