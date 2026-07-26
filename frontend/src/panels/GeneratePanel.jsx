import { useState } from "react";
import { Alert, Button, Form, Input, InputNumber, Space } from "antd";
import ResultPanel from "../components/ResultPanel";
import { errorMessage, generateNovel } from "../api/client";

export default function GeneratePanel() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  const onFinish = async (values) => {
    setLoading(true);
    setError("");
    setResult("");
    try {
      const data = await generateNovel({
        title: values.title,
        seed_text: values.seed_text,
        max_new_tokens: values.max_new_tokens,
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
        initialValues={{ max_new_tokens: 200 }}
      >
        <Form.Item
          label="제목"
          name="title"
          rules={[{ required: true, message: "제목을 입력하세요" }]}
        >
          <Input placeholder="예: 가을 개울가의 만남" disabled={loading} />
        </Form.Item>
        <Form.Item label="씨앗 문장 (선택)" name="seed_text">
          <Input.TextArea
            rows={3}
            placeholder="예: 소년은 개울가에 앉아"
            disabled={loading}
          />
        </Form.Item>
        <Form.Item label="생성 길이" name="max_new_tokens">
          <InputNumber min={16} max={400} disabled={loading} />
        </Form.Item>
        <Space>
          <Button type="primary" htmlType="submit" loading={loading}>
            소설 생성
          </Button>
        </Space>
      </Form>
      {error ? (
        <Alert style={{ marginTop: 16 }} type="error" showIcon message={error} />
      ) : null}
      <ResultPanel
        loading={loading}
        result={result}
        emptyText="제목을 넣고 생성하면 본문이 여기에 표시됩니다"
      />
    </>
  );
}
