import { Empty, Spin } from "antd";
import styled, { keyframes } from "styled-components";

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
`;

const Panel = styled.section`
  margin-top: 20px;
  padding: 20px 22px;
  border: 1px solid ${({ theme }) => theme.colors.line};
  border-radius: ${({ theme }) => theme.radius.md};
  background: rgba(255, 255, 255, 0.72);
  min-height: 160px;
  animation: ${fadeIn} 0.35s ease;
`;

const Label = styled.p`
  margin: 0 0 10px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: ${({ theme }) => theme.colors.inkSoft};
`;

const Body = styled.div`
  white-space: pre-wrap;
  line-height: 1.75;
  font-size: 15px;
  color: ${({ theme }) => theme.colors.ink};
`;

export default function ResultPanel({ loading, result, emptyText }) {
  return (
    <Panel>
      <Label>결과</Label>
      {loading ? (
        <Spin tip="모델이 생성하는 중…" />
      ) : result ? (
        <Body>{result}</Body>
      ) : (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={emptyText || "아직 결과가 없습니다"}
        />
      )}
    </Panel>
  );
}
