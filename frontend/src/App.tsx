import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { useSession } from "./hooks/useSession";
import { AdminPage } from "./pages/AdminPage";
import { FeedPage } from "./pages/FeedPage";
import { LoginPage } from "./pages/LoginPage";
import { MePage } from "./pages/MePage";
import { ProfilePage } from "./pages/ProfilePage";

const queryClient = new QueryClient();

function ProtectedApp() {
  const sessionQuery = useSession();

  if (sessionQuery.isLoading) {
    return <div className="page-splash">세션을 확인하는 중입니다.</div>;
  }

  if (sessionQuery.isError || !sessionQuery.data) {
    return <Navigate to="/login" replace />;
  }

  return <AppShell />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedApp />}>
            <Route path="/" element={<Navigate to="/feed" replace />} />
            <Route path="/feed" element={<FeedPage />} />
            <Route path="/me" element={<MePage />} />
            <Route path="/u/:slug" element={<ProfilePage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

