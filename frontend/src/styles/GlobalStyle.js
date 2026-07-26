import { createGlobalStyle } from "styled-components";

export const GlobalStyle = createGlobalStyle`
  *, *::before, *::after {
    box-sizing: border-box;
  }

  html, body, #root {
    min-height: 100%;
  }

  body {
    margin: 0;
    color: ${({ theme }) => theme.colors.ink};
    font-family: ${({ theme }) => theme.fonts.body};
    background:
      radial-gradient(1200px 600px at 10% -10%, rgba(31, 111, 120, 0.18), transparent 55%),
      radial-gradient(900px 500px at 100% 0%, rgba(15, 76, 92, 0.12), transparent 50%),
      linear-gradient(165deg, #eef5f4 0%, ${({ theme }) => theme.colors.paper} 45%, #e4eceb 100%);
    background-attachment: fixed;
  }

  button, input, textarea {
    font: inherit;
  }
`;
