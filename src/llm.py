import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()


def get_llm():
    """
    Initialize and return the Groq LLM.
    """

    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY"),
    )


def get_prompt():
    """
    Return the prompt template used by the LLM.
    """

    return ChatPromptTemplate.from_template(
        """
You are an intelligent AI assistant.

Answer ONLY using the provided document context.

If the answer is not available in the context, reply:

"I couldn't find that information in the uploaded documents."

Context:
{context}

Question:
{question}

Answer:
"""
    )


def generate_answer(question, retrieved_docs):
    """
    Generate an answer from the retrieved documents.
    """

    context = "\n\n".join(
        doc.page_content for doc in retrieved_docs
    )

    prompt = get_prompt()

    llm = get_llm()

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    return response.content