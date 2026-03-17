import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { deleteAvatar, fetchReports, hideAvatar } from "../api/client";
import { SectionCard } from "../components/SectionCard";
import { useSession } from "../hooks/useSession";

export function AdminPage() {
  const sessionQuery = useSession();
  const queryClient = useQueryClient();
  const reportsQuery = useQuery({
    queryKey: ["reports"],
    queryFn: fetchReports,
    enabled: sessionQuery.data?.user.is_admin === true
  });

  const hideMutation = useMutation({
    mutationFn: ({ avatarId, note }: { avatarId: string; note: string }) => hideAvatar(avatarId, note),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["reports"] });
    }
  });

  const deleteMutation = useMutation({
    mutationFn: ({ avatarId, note }: { avatarId: string; note: string }) => deleteAvatar(avatarId, note),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["reports"] });
    }
  });

  if (sessionQuery.isLoading) {
    return (
      <div className="page-stack">
        <SectionCard eyebrow="Moderation" title="권한 확인 중">
          <p>관리자 권한을 확인하고 있습니다.</p>
        </SectionCard>
      </div>
    );
  }

  if (sessionQuery.data?.user.is_admin !== true) {
    return (
      <div className="page-stack">
        <SectionCard eyebrow="Moderation" title="관리자 권한 필요">
          <p>이 화면은 관리자 계정으로만 접근할 수 있습니다.</p>
        </SectionCard>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <SectionCard eyebrow="Moderation" title="신고 큐">
        <div className="report-list">
          {reportsQuery.data?.map((report) => (
            <article key={report.id} className="report-card">
              <div>
                <h3>{report.avatar_title}</h3>
                <p>@{report.reporter_slug}</p>
                <p>{report.reason}</p>
              </div>
              <div className="report-card__actions">
                <button type="button" className="ghost-button" onClick={() => hideMutation.mutate({ avatarId: report.avatar_id, note: "관리자 숨김" })}>
                  숨김
                </button>
                <button type="button" className="ghost-button ghost-button--danger" onClick={() => deleteMutation.mutate({ avatarId: report.avatar_id, note: "관리자 삭제" })}>
                  삭제
                </button>
              </div>
            </article>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
