import { useState } from "react";
import { Alert, Button, Form, Input, Space } from "antd";
import NovelSelect from "../components/NovelSelect";
import ResultPanel from "../components/ResultPanel";
import { errorMessage, summarizeNovel } from "../api/client";

export default function SummaryPanel({ novels }) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  const onFinish = async (values) => {
    setLoading(true);
    setError("");
    setResult("");
    try {
      const data = await summarizeNovel({
        title: values.title,
        passage: values.passage,
      });
      setResult(data.result);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        requiredMark={false}
      >
        <Form.Item
          label="소설"
          name="title"
          rules={[{ required: true, message: "소설을 선택하거나 제목을 입력하세요" }]}
        >
          <NovelSelect novels={novels} disabled={loading} />
        </Form.Item>
        <Form.Item
          label="본문 (선택 — 비우면 서버가 원문을 찾습니다)"
          name="passage"
        >
          <Input.TextArea
            rows={5}
            placeholder="직접 요약을 원할 때 본문을 붙여 넣으세요"
            disabled={loading}
          />
        </Form.Item>
        <Space>
          <Button type="primary" htmlType="submit" loading={loading}>
            줄거리 요약
          </Button>
        </Space>
      </Form>
      {error ? (
        <Alert style={{ marginTop: 16 }} type="error" showIcon message={error} />
      ) : null}
      <ResultPanel
        loading={loading}
        result={result}
        emptyText="요약을 실행하면 줄거리가 여기에 표시됩니다"
      />
    </>
  );
}
