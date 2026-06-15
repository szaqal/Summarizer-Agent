from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI

from summarizer_agent.config import MISTRAL_API_KEY

_prompt = ChatPromptTemplate.from_template(
    "Streść poniższy artykuł w 3-5 zdaniach po polsku:\n\n{text}"
)
_llm = ChatMistralAI(model="mistral-small-latest", api_key=MISTRAL_API_KEY)
_chain = _prompt | _llm | StrOutputParser()


def summarize(text: str) -> str:
    return _chain.invoke({"text": text})
