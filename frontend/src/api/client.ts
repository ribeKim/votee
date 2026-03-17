import type {
  AdminReportItem,
  AnalysisResultResponse,
  AnalysisTriggerResponse,
  AuthenticatedUserResponse,
  ReportResponse,
  UserProfileResponse,
  VoteMatchResponse,
  VoteSubmitResponse
} from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export class ApiError extends Error {
  public readonly status: number;

  public constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...init
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => ({ detail: "요청을 처리하지 못했습니다." }))) as { detail?: string };
    throw new ApiError(response.status, payload.detail ?? "요청을 처리하지 못했습니다.");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function loginWithDiscord(): void {
  window.location.href = `${API_BASE}/api/auth/discord/login`;
}

export function fetchCurrentUser(): Promise<AuthenticatedUserResponse> {
  return apiFetch<AuthenticatedUserResponse>("/api/auth/me");
}

export function logout(): Promise<void> {
  return apiFetch<void>("/api/auth/logout", { method: "POST" });
}

export function fetchProfile(slug: string): Promise<UserProfileResponse> {
  return apiFetch<UserProfileResponse>(`/api/profiles/${slug}`);
}

export function uploadAvatar(formData: FormData): Promise<{ avatar: AuthenticatedUserResponse["avatars"][number] }> {
  return apiFetch<{ avatar: AuthenticatedUserResponse["avatars"][number] }>("/api/avatars", {
    method: "POST",
    body: formData
  });
}

export function setPrimaryAvatar(avatarId: string): Promise<{ avatar: AuthenticatedUserResponse["avatars"][number] }> {
  return apiFetch<{ avatar: AuthenticatedUserResponse["avatars"][number] }>("/api/avatars/primary", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ avatar_id: avatarId })
  });
}

export function fetchVoteMatch(): Promise<VoteMatchResponse> {
  return apiFetch<VoteMatchResponse>("/api/votes/match");
}

export function submitVote(payload: {
  pair_view_id: string;
  winner_avatar_id: string;
  loser_avatar_id: string;
}): Promise<VoteSubmitResponse> {
  return apiFetch<VoteSubmitResponse>("/api/votes", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}

export function createReport(payload: { avatar_id: string; reason: string }): Promise<ReportResponse> {
  return apiFetch<ReportResponse>("/api/avatars/report", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}

export function fetchReports(): Promise<AdminReportItem[]> {
  return apiFetch<AdminReportItem[]>("/api/admin/reports");
}

export function hideAvatar(avatarId: string, note: string): Promise<void> {
  return apiFetch<void>(`/api/admin/avatars/${avatarId}/hide`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ note })
  });
}

export function deleteAvatar(avatarId: string, note: string): Promise<void> {
  return apiFetch<void>(`/api/admin/avatars/${avatarId}/delete`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ note })
  });
}

export function triggerAnalysis(avatarId: string): Promise<AnalysisTriggerResponse> {
  return apiFetch<AnalysisTriggerResponse>(`/api/avatars/${avatarId}/analysis`, {
    method: "POST"
  });
}

export function fetchAnalysis(requestId: string): Promise<AnalysisResultResponse> {
  return apiFetch<AnalysisResultResponse>(`/api/analysis/${requestId}`);
}
