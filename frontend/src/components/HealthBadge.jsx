import { Tag, Tooltip } from "antd";
import styled from "styled-components";

const Wrap = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
`;

export default function HealthBadge({ health, loading }) {
  if (loading) {
    return <Tag>모델 상태 확인 중…</Tag>;
  }

  if (!health) {
    return <Tag color="error">API 연결 실패</Tag>;
  }

  const models = health.models || {};
  const tasks = ["qa", "generation", "summary"];

  return (
    <Wrap>
      <Tag color={health.status === "ok" ? "success" : "error"}>
        API {health.status === "ok" ? "정상" : "오류"}
      </Tag>
      {tasks.map((task) => {
        const m = models[task];
        const ready = Boolean(m?.ready);
        return (
          <Tooltip key={task} title={m?.path || task}>
            <Tag color={ready ? "processing" : "warning"}>
              {task} {ready ? "준비" : "없음"}
            </Tag>
          </Tooltip>
        );
      })}
    </Wrap>
  );
}
