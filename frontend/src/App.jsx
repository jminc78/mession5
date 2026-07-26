import { useEffect, useState } from "react";
import { ConfigProvider, Tabs, Typography, message } from "antd";
import styled, { keyframes } from "styled-components";
import { BookOutlined, EditOutlined, ReadOutlined } from "@ant-design/icons";
import { errorMessage, getHealth, getNovels } from "./api/client";
import HealthBadge from "./components/HealthBadge";
import QaPanel from "./panels/QaPanel";
import GeneratePanel from "./panels/GeneratePanel";
import SummaryPanel from "./panels/SummaryPanel";
import { theme as appTheme } from "./styles/theme";

const rise = keyframes`
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
`;

const Page = styled.div`
  width: min(920px, calc(100% - 32px));
  margin: 0 auto;
  padding: 40px 0 64px;
  animation: ${rise} 0.55s ease;
`;

const Brand = styled.header`
  margin-bottom: 28px;
`;

const BrandName = styled.h1`
  margin: 0;
  font-family: ${({ theme }) => theme.fonts.brand};
  font-size: clamp(2.4rem, 6vw, 3.4rem);
  font-weight: 400;
  letter-spacing: -0.02em;
  color: ${({ theme }) => theme.colors.ink};
  line-height: 1.15;
`;

const Lead = styled.p`
  margin: 12px 0 0;
  max-width: 34rem;
  font-size: 1.05rem;
  line-height: 1.6;
  color: ${({ theme }) => theme.colors.inkSoft};
`;

const StatusRow = styled.div`
  margin-top: 18px;
`;

const Work = styled.main`
  margin-top: 28px;
  padding: 22px 24px 28px;
  border-radius: ${({ theme }) => theme.radius.md};
  border: 1px solid ${({ theme }) => theme.colors.line};
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(8px);
  box-shadow: ${({ theme }) => theme.shadow};
  animation: ${rise} 0.7s ease;
`;

const Foot = styled.footer`
  margin-top: 22px;
  font-size: 12px;
  color: ${({ theme }) => theme.colors.inkSoft};
`;

export default function App() {
  const [health, setHealth] = useState(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [novels, setNovels] = useState([]);

  useEffect(() => {
    let alive = true;

    (async () => {
      try {
        const [h, list] = await Promise.all([getHealth(), getNovels()]);
        if (!alive) return;
        setHealth(h);
        setNovels(list || []);
      } catch (err) {
        if (!alive) return;
        setHealth(null);
        message.error(errorMessage(err));
      } finally {
        if (alive) setHealthLoading(false);
      }
    })();

    return () => {
      alive = false;
    };
  }, []);

  const items = [
    {
      key: "qa",
      label: (
        <span>
          <ReadOutlined /> 문답
        </span>
      ),
      children: <QaPanel novels={novels} />,
    },
    {
      key: "generate",
      label: (
        <span>
          <EditOutlined /> 생성
        </span>
      ),
      children: <GeneratePanel />,
    },
    {
      key: "summary",
      label: (
        <span>
          <BookOutlined /> 요약
        </span>
      ),
      children: <SummaryPanel novels={novels} />,
    },
  ];

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: appTheme.colors.teal,
          colorInfo: appTheme.colors.tealDeep,
          borderRadius: 10,
          fontFamily: appTheme.fonts.body,
        },
      }}
    >
      <Page>
        <Brand>
          <BrandName>서재 AI</BrandName>
          <Lead>
            한국 소설을 묻고, 쓰고, 줄거리를 정리하는 Mission 5 프론트엔드입니다.
          </Lead>
          <StatusRow>
            <HealthBadge health={health} loading={healthLoading} />
          </StatusRow>
        </Brand>

        <Work>
          <Typography.Paragraph type="secondary" style={{ marginTop: 0 }}>
            소설 {novels.length}편 로드됨 · API → /api (nginx → backend)
          </Typography.Paragraph>
          <Tabs items={items} />
        </Work>

        <Foot>Mission 5 · React · styled-components · Ant Design · Docker</Foot>
      </Page>
    </ConfigProvider>
  );
}
