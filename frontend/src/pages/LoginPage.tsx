import { Navigate } from "react-router-dom";

import { loginWithDiscord } from "../api/client";
import { useSession } from "../hooks/useSession";

export function LoginPage() {
  const sessionQuery = useSession();

  if (sessionQuery.data) {
    return <Navigate to="/feed" replace />;
  }

  return (
    <div className="login-page">
      <div className="login-page__hero">
        <p className="eyebrow">Discord OAuth2 / Avatar Community</p>
        <h1>당신의 아바타를 올리고, 취향 전장을 열어보세요.</h1>
        <p className="login-page__description">
          Votee는 아바타 업로드, 공개 프로필, 무한 1대1 투표, 신고 및 관리자 운영을 한 흐름으로 묶은 커뮤니티 서비스입니다.
        </p>
        <button type="button" className="primary-button" onClick={loginWithDiscord}>
          Discord로 시작하기
        </button>
      </div>
    </div>
  );
}

