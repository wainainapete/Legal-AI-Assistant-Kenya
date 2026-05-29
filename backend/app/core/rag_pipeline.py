from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from app.core.config import settings
from app.utils.safety import SafetyFilter

COLLECTION_MAP = {
    "benin": "legal_docs_benin",
    "madagascar": "legal_docs_madagascar",
}

SYSTEM_PROMPT = """Tu es un assistant juridique qui aide les citoyens a comprendre
leurs droits legaux en {country}. Tu fournis des informations juridiques claires
et comprehensibles basees UNIQUEMENT sur les documents legaux fournis ci-dessous.

REGLES IMPORTANTES:
1. Reponds uniquement en te basant sur les documents fournis.
2. Si tu n'es pas sur, dis-le clairement et recommande de consulter un avocat.
3. Ne donne JAMAIS de conseils juridiques specifiques — seulement des informations generales.
4. Termine toujours par: "Pour votre situation specifique, consultez un professionnel juridique."
5. Reponds dans la langue de la question (francais ou malgache).

Documents juridiques pertinents:
{context}

Question du citoyen: {question}

Reponse (claire et accessible pour un non-juriste):"""


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"batch_size": 8},
    )


class LegalRAGPipeline:
    _embeddings = None

    def __init__(self, country: str):
        if country not in COLLECTION_MAP:
            raise ValueError(f"Country must be one of: {list(COLLECTION_MAP.keys())}")

        self.country = country
        self.safety = SafetyFilter()

        if LegalRAGPipeline._embeddings is None:
            LegalRAGPipeline._embeddings = get_embeddings()

        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            max_tokens=settings.MAX_TOKENS_RESPONSE,
            temperature=0.1,
        )

        self.vector_store = PGVector(
            embeddings=LegalRAGPipeline._embeddings,
            collection_name=COLLECTION_MAP[country],
            connection=settings.DATABASE_URL,
            use_jsonb=True,
        )

        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5},
        )

        self.prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)

    async def query(self, question: str) -> dict:
        safety_result = self.safety.pre_check(question)
        if not safety_result["safe"]:
            return {
                "answer": safety_result["message"],
                "sources": [],
                "confidence": 0.0,
                "needs_review": False,
                "flagged": True,
            }

        docs = self.retriever.invoke(question)
        context = "\n\n---\n\n".join([d.page_content for d in docs])
        sources = [d.metadata.get("source", "Unknown") for d in docs]

        chain = (
            {"context": lambda _: context, "question": RunnablePassthrough(), "country": lambda _: self.country}
            | self.prompt
            | self.llm
        )
        response = await chain.ainvoke(question)
        answer = response.content

        post_check = self.safety.post_check(answer, docs)
        confidence = post_check["confidence"]
        needs_review = confidence < settings.CONFIDENCE_THRESHOLD

        return {
            "answer": answer,
            "sources": list(set(sources)),
            "confidence": confidence,
            "needs_review": needs_review,
            "flagged": False,
        }