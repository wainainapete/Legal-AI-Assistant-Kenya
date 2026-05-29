import re

OUT_OF_SCOPE_PATTERNS = [
    r"\b(bombe|arme|tuer|violence|drogue|trafic)\b",
    r"\b(bomb|weapon|kill|drug|traffic)\b",
]

LEGAL_DISCLAIMER = (
    "\n\n* Cette information est a titre general uniquement. "
    "Pour votre situation specifique, consultez un avocat ou un centre d'aide juridique.*"
)

UNCERTAINTY_SIGNALS = [
    "je ne sais pas", "je ne suis pas sur", "il est difficile de dire",
    "cela depend", "je vous recommande de consulter", "il n est pas clair",
]


class SafetyFilter:
    def pre_check(self, query: str) -> dict:
        query_lower = query.lower()
        for pattern in OUT_OF_SCOPE_PATTERNS:
            if re.search(pattern, query_lower):
                return {"safe": False, "message": "Je suis concu uniquement pour repondre a des questions juridiques."}
        if len(query.strip()) < 10:
            return {"safe": False, "message": "Veuillez poser une question juridique complete."}
        return {"safe": True}

    def post_check(self, answer: str, source_docs: list) -> dict:
        score = 1.0
        answer_lower = answer.lower()
        uncertainty_count = sum(1 for s in UNCERTAINTY_SIGNALS if s in answer_lower)
        score -= uncertainty_count * 0.15
        if not source_docs:
            score -= 0.4
        if len(answer.split()) < 30:
            score -= 0.2
        return {"confidence": max(0.0, min(1.0, round(score, 2))), "answer": answer}
