import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const api = axios.create({ baseURL: API_BASE, timeout: 30000 });

export const sendQuestion = async ({ question, country, language = "fr", session_id }) => {
  const res = await api.post("/api/chat/", { question, country, language, session_id });
  return res.data;
};

export const flagResponse = async ({ session_id, question, answer, country, reason }) => {
  const res = await api.post("/api/review/flag", { session_id, question, answer, country, reason, flagged_by: "user" });
  return res.data;
};
