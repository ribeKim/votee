export interface UserSummary {
  id: string;
  display_name: string;
  username: string;
  slug: string;
  avatar_url: string | null;
  bio: string | null;
  is_admin: boolean;
}

export interface AvatarSummary {
  id: string;
  title: string;
  description: string | null;
  image_url: string;
  status: string;
  is_primary: boolean;
  elo_rating: number;
  wins: number;
  losses: number;
  width: number;
  height: number;
  created_at: string;
}

export interface AuthenticatedUserResponse {
  user: UserSummary;
  avatars: AvatarSummary[];
}

export interface UserProfileResponse {
  user: UserSummary;
  avatars: AvatarSummary[];
}

export interface VoteMatchResponse {
  pair_view_id: string;
  left: {
    id: string;
    title: string;
    image_url: string;
    owner_slug: string;
  };
  right: {
    id: string;
    title: string;
    image_url: string;
    owner_slug: string;
  };
}

export interface VoteSubmitResponse {
  winner_rating: number;
  loser_rating: number;
}

export interface ReportResponse {
  id: string;
  avatar_id: string;
  reason: string;
  status: string;
  created_at: string;
}

export interface AdminReportItem {
  id: string;
  avatar_id: string;
  avatar_title: string;
  reporter_slug: string;
  reason: string;
  status: string;
  created_at: string;
}

export interface AnalysisTriggerResponse {
  request_id: string;
  status: string;
}

export interface AnalysisResultResponse {
  request_id: string;
  avatar_id: string;
  status: string;
  summary: string | null;
  strengths: string | null;
  style_notes: string | null;
  improvement_tips: string | null;
  error_message: string | null;
}

