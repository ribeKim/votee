import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { fetchAnalysis, setPrimaryAvatar, triggerAnalysis, uploadAvatar } from "../api/client";
import { AvatarCard } from "../components/AvatarCard";
import { SectionCard } from "../components/SectionCard";
import { useSession } from "../hooks/useSession";

export function MePage() {
  const sessionQuery = useSession();
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysisRequestId, setAnalysisRequestId] = useState<string | null>(null);

  const uploadMutation = useMutation({
    mutationFn: uploadAvatar,
    onSuccess: async () => {
      setTitle("");
      setDescription("");
      setSelectedFile(null);
      await queryClient.invalidateQueries({ queryKey: ["session"] });
    }
  });

  const primaryMutation = useMutation({
    mutationFn: setPrimaryAvatar,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["session"] });
    }
  });

  const analysisMutation = useMutation({
    mutationFn: triggerAnalysis,
    onSuccess: async (payload) => {
      setAnalysisRequestId(payload.request_id);
      await queryClient.invalidateQueries({ queryKey: ["analysis", payload.request_id] });
    }
  });

  const analysisQuery = useQuery({
    queryKey: ["analysis", analysisRequestId],
    queryFn: () => fetchAnalysis(analysisRequestId ?? ""),
    enabled: analysisRequestId !== null
  });

  const currentUser = sessionQuery.data;

  return (
    <div className="page-stack">
      <SectionCard eyebrow="Studio" title="내 아바타 스튜디오">
        <form
          className="upload-form"
          onSubmit={(event) => {
            event.preventDefault();
            if (!selectedFile) {
              return;
            }
            const formData = new FormData();
            formData.append("title", title);
            formData.append("description", description);
            formData.append("file", selectedFile);
            uploadMutation.mutate(formData);
          }}
        >
          <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="아바타 제목" required />
          <textarea
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="이 컷의 콘셉트나 포인트를 적어주세요."
          />
          <input type="file" accept="image/png,image/jpeg,image/webp" onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)} required />
          <button type="submit" className="primary-button">
            업로드
          </button>
        </form>
      </SectionCard>

      <SectionCard eyebrow="Gallery" title="내 공개 아바타">
        <div className="gallery-grid">
          {currentUser?.avatars.map((avatar) => (
            <AvatarCard
              key={avatar.id}
              avatar={avatar}
              footer={
                <div className="avatar-actions">
                  <button type="button" className="ghost-button" onClick={() => primaryMutation.mutate(avatar.id)}>
                    대표로 지정
                  </button>
                  <button type="button" className="ghost-button" onClick={() => analysisMutation.mutate(avatar.id)}>
                    AI 스타일 분석
                  </button>
                </div>
              }
            />
          ))}
        </div>
      </SectionCard>

      <SectionCard eyebrow="AI Analysis" title="최근 분석 결과">
        {analysisQuery.data ? (
          <div className="analysis-result">
            <p>
              <strong>요약:</strong> {analysisQuery.data.summary}
            </p>
            <p>
              <strong>강점:</strong> {analysisQuery.data.strengths}
            </p>
            <p>
              <strong>스타일 메모:</strong> {analysisQuery.data.style_notes}
            </p>
            <p>
              <strong>개선 아이디어:</strong> {analysisQuery.data.improvement_tips}
            </p>
          </div>
        ) : (
          <p>분석을 실행하면 여기에서 결과를 확인할 수 있습니다.</p>
        )}
      </SectionCard>
    </div>
  );
}

