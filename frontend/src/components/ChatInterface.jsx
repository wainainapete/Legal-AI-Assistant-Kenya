import { useState, useRef, useEffect } from "react";
import { sendQuestion, flagResponse } from "../services/api";

const COUNTRIES = [
  { value: "benin", label: "🇧🇯 Bénin", placeholder: "Ex: Quels sont mes droits en cas de licenciement?" },
  { value: "madagascar", label: "🇲🇬 Madagascar", placeholder: "Ex: Comment enregistrer un mariage à Madagascar?" },
];

export default function ChatInterface() {
  const [country, setCountry] = useState("benin");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const currentCountry = COUNTRIES.find(c => c.value === country);

  const handleSubmit = async () => {
    if (!input.trim() || loading) return;
    const question = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const data = await sendQuestion({ question, country, session_id: sessionId });
      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        confidence: data.confidence,
        needs_review: data.needs_review,
        question,
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Une erreur est survenue. Veuillez réessayer.",
        error: true,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFlag = async (msg) => {
    await flagResponse({
      session_id: sessionId,
      question: msg.question,
      answer: msg.content,
      country,
      reason: "user_flagged",
    });
    alert("Merci! Cette réponse sera examinée par un expert juridique.");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", maxWidth: 720, margin: "0 auto", fontFamily: "Georgia, serif", background: "#fafaf7" }}>
      {/* Header */}
      <div style={{ background: "#1a3a2a", color: "#e8f5e9", padding: "1rem 1.5rem", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700 }}>⚖️ Assistant Juridique IA</h1>
          <p style={{ margin: 0, fontSize: "0.75rem", opacity: 0.7 }}>Accès gratuit à l'information juridique</p>
        </div>
        <select
          value={country}
          onChange={e => setCountry(e.target.value)}
          style={{ background: "#2d5a3d", color: "#e8f5e9", border: "1px solid #4a8a5a", borderRadius: 6, padding: "0.4rem 0.7rem", fontSize: "0.85rem" }}
        >
          {COUNTRIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
      </div>

      {/* Disclaimer */}
      <div style={{ background: "#fff8e1", borderBottom: "1px solid #ffe082", padding: "0.6rem 1.5rem", fontSize: "0.75rem", color: "#8a6a00" }}>
        ⚠️ Cet outil fournit des informations juridiques générales, pas des conseils juridiques personnalisés.
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
        {messages.length === 0 && (
          <div style={{ textAlign: "center", color: "#999", marginTop: "3rem" }}>
            <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>⚖️</div>
            <p style={{ fontSize: "1rem" }}>Posez votre question juridique</p>
            <p style={{ fontSize: "0.8rem", color: "#bbb" }}>{currentCountry.placeholder}</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start" }}>
            <div style={{
              maxWidth: "85%",
              background: msg.role === "user" ? "#1a3a2a" : "#fff",
              color: msg.role === "user" ? "#e8f5e9" : "#333",
              borderRadius: msg.role === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
              padding: "0.9rem 1.1rem",
              boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
              border: msg.role === "assistant" ? "1px solid #e5e5e0" : "none",
            }}>
              <p style={{ margin: 0, lineHeight: 1.65, fontSize: "0.9rem", whiteSpace: "pre-wrap" }}>{msg.content}</p>
              {msg.sources?.length > 0 && (
                <div style={{ marginTop: "0.6rem", paddingTop: "0.5rem", borderTop: "1px solid #e5e5e0", fontSize: "0.7rem", color: "#999" }}>
                  📚 Sources: {msg.sources.join(", ")}
                </div>
              )}
              {msg.role === "assistant" && !msg.error && (
                <div style={{ marginTop: "0.6rem", display: "flex", gap: "0.5rem", alignItems: "center" }}>
                  {msg.needs_review && (
                    <span style={{ fontSize: "0.65rem", background: "#fff3cd", color: "#856404", padding: "0.2rem 0.5rem", borderRadius: 4 }}>
                      🔍 En attente de vérification experte
                    </span>
                  )}
                  <button onClick={() => handleFlag(msg)} style={{ fontSize: "0.65rem", background: "none", border: "1px solid #ddd", borderRadius: 4, padding: "0.2rem 0.5rem", cursor: "pointer", color: "#999", marginLeft: "auto" }}>
                    🚩 Signaler
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: "flex" }}>
            <div style={{ background: "#fff", border: "1px solid #e5e5e0", borderRadius: "18px 18px 18px 4px", padding: "0.9rem 1.1rem", fontSize: "0.9rem", color: "#999" }}>
              ⏳ Recherche dans le corpus juridique...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ padding: "1rem 1.5rem", background: "#fff", borderTop: "1px solid #e5e5e0", display: "flex", gap: "0.7rem" }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleSubmit()}
          placeholder={currentCountry.placeholder}
          style={{ flex: 1, border: "1px solid #ddd", borderRadius: 24, padding: "0.7rem 1.1rem", fontSize: "0.9rem", outline: "none", fontFamily: "inherit" }}
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !input.trim()}
          style={{ background: loading ? "#ccc" : "#1a3a2a", color: "#fff", border: "none", borderRadius: 24, padding: "0.7rem 1.3rem", cursor: loading ? "not-allowed" : "pointer", fontSize: "0.9rem" }}
        >
          Envoyer
        </button>
      </div>
    </div>
  );
}
