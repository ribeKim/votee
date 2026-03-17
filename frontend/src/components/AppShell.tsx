import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";

import { logout } from "../api/client";
import { useSession } from "../hooks/useSession";

export function AppShell() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const sessionQuery = useSession();
  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["session"] });
      navigate("/login");
    }
  });

  const currentUser = sessionQuery.data?.user;

  return (
    <div className="shell">
      <aside className="shell__sidebar">
        <Link className="shell__brand" to="/feed">
          <span>Votee</span>
          <strong>Avatar Arena</strong>
        </Link>
        <nav className="shell__nav">
          <NavLink to="/feed">투표 피드</NavLink>
          <NavLink to="/me">내 스튜디오</NavLink>
          {currentUser ? <NavLink to={`/u/${currentUser.slug}`}>공개 프로필</NavLink> : null}
          {currentUser?.is_admin ? <NavLink to="/admin">관리자</NavLink> : null}
        </nav>
        <div className="shell__profile">
          <p>{currentUser?.display_name ?? "로딩 중..."}</p>
          <button type="button" className="ghost-button" onClick={() => logoutMutation.mutate()}>
            로그아웃
          </button>
        </div>
      </aside>
      <main className="shell__main">
        <Outlet />
      </main>
    </div>
  );
}

