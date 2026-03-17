import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { createReport, fetchVoteMatch, submitVote } from "../api/client";
import { SectionCard } from "../components/SectionCard";

export function FeedPage() {
  const queryClient = useQueryClient();
  const [reportReason, setReportReason] = useState("");
  const [reportAvatarId, setReportAvatarId] = useState<string | null>(null);

  const matchQuery = useQuery({
    queryKey: ["vote-match"],
    queryFn: fetchVoteMatch,
    retry: false
  });

  const voteMutation = useMutation({
    mutationFn: submitVote,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["vote-match"] });
    }
  });

  const reportMutation = useMutation({
    mutationFn: createReport,
    onSuccess: async () => {
      setReportReason("");
      setReportAvatarId(null);
      await queryClient.invalidateQueries({ queryKey: ["reports"] });
    }
  });

  const match = matchQuery.data;

  return (
    <div className="page-stack">
      <SectionCard eyebrow="Vote Feed" title="오늘의 취향 대결">
        {matchQuery.isLoading ? <p>매치를 불러오는 중입니다.</p> : null}
        {matchQuery.isError ? <p>투표 가능한 아바타가 아직 부족합니다.</p> : null}
        {match ? (
          <div className="battle-grid">
            {[match.left, match.right].map((candidate, index) => {
              const other = index === 0 ? match.right : match.left;
              const isReporting = reportAvatarId === candidate.id;
              return (
                <article key={candidate.id} className="battle-card">
                  <img src={candidate.image_url} alt={candidate.title} />
                  <div className="battle-card__body">
                    <h3>{candidate.title}</h3>
                    <p>@{candidate.owner_slug}</p>
                    <div className="battle-card__actions">
                      <button
                        type="button"
                        className="primary-button"
                        onClick={() =>
                          voteMutation.mutate({
                            pair_view_id: match.pair_view_id,
                            winner_avatar_id: candidate.id,
                            loser_avatar_id: other.id
                          })
                        }
                      >
                        이 아바타 선택
                      </button>
                      <button
                        type="button"
                        className="ghost-button"
                        onClick={() => setReportAvatarId(isReporting ? null : candidate.id)}
                      >
                        신고
                      </button>
                    </div>
                    {isReporting ? (
                      <form
                        className="inline-form"
                        onSubmit={(event) => {
                          event.preventDefault();
                          reportMutation.mutate({ avatar_id: candidate.id, reason: reportReason });
                        }}
                      >
                        <textarea
                          value={reportReason}
                          onChange={(event) => setReportReason(event.target.value)}
                          placeholder="신고 사유를 입력하세요."
                        />
                        <button type="submit" className="primary-button">
                          신고 제출
                        </button>
                      </form>
                    ) : null}
                  </div>
                </article>
              );
            })}
          </div>
        ) : null}
      </SectionCard>
    </div>
  );
}

