import axios from "axios";

const client = axios.create({
  baseURL: "/api",
  timeout: 180_000,
});

export async function getHealth() {
  const { data } = await client.get("/health");
  return data;
}

export async function getNovels() {
  const { data } = await client.get("/novels");
  return data;
}

export async function askQuestion({ title, question }) {
  const { data } = await client.post("/qa", { title, question });
  return data;
}

export async function generateNovel({ title, seed_text, max_new_tokens }) {
  const body = { title, seed_text: seed_text || "" };
  if (max_new_tokens) body.max_new_tokens = max_new_tokens;
  const { data } = await client.post("/generate", body);
  return data;
}

export async function summarizeNovel({ title, passage }) {
  const body = { title };
  if (passage) body.passage = passage;
  const { data } = await client.post("/summary", body);
  return data;
}

export function errorMessage(err) {
  return (
    err?.response?.data?.detail ||
    err?.message ||
    "요청에 실패했습니다."
  );
}
