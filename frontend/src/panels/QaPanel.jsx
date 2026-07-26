import { useState } from "react";
import { Alert, Button, Form, Input, Space } from "antd";
import NovelSelect from "../components/NovelSelect";
import ResultPanel from "../components/ResultPanel";
import { askQuestion, errorMessage } from "../api/client";

export default function QaPanel({ novels }) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  const onFinish = async (values) => {
    setLoading(true);
    setError("");
    setResult("");
    try {
      const data = await askQuestion({
        title: values.title,
        question: values.question,
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
          rules={[{ required: true, message: "소설을 선택하세요" }]}
        >
          <NovelSelect novels={novels} disabled={loading} />
        </Form.Item>
        <Form.Item
          label="질문"
          name="question"
          rules={[{ required: true, message: "질문을 입력하세요" }]}
        >
          <Input.TextArea
            rows={3}
            placeholder="예: 주요 인물은 누구인가요?"
            disabled={loading}
          />
        </Form.Item>
        <Space>
          <Button type="primary" htmlType="submit" loading={loading}>
            답변 받기
          </Button>
        </Space>
      </Form>
      {error ? (
        <Alert style={{ marginTop: 16 }} type="error" showIcon message={error} />
      ) : null}
      <ResultPanel
        loading={loading}
        result={result}
        emptyText="질문을 보내면 답변이 여기에 표시됩니다"
      />
    </>
  );
}
