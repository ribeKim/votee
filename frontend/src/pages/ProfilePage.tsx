import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { fetchProfile } from "../api/client";
import { AvatarCard } from "../components/AvatarCard";
import { SectionCard } from "../components/SectionCard";

export function ProfilePage() {
  const params = useParams();
  const slug = params.slug ?? "";
  const profileQuery = useQuery({
    queryKey: ["profile", slug],
    queryFn: () => fetchProfile(slug),
    enabled: slug.length > 0
  });

  if (profileQuery.isLoading) {
    return <p>프로필을 불러오는 중입니다.</p>;
  }

  if (!profileQuery.data) {
    return <p>프로필을 찾을 수 없습니다.</p>;
  }

  return (
    <div className="page-stack">
      <SectionCard eyebrow="Public Profile" title={profileQuery.data.user.display_name}>
        <p>@{profileQuery.data.user.slug}</p>
        <div className="gallery-grid">
          {profileQuery.data.avatars.map((avatar) => (
            <AvatarCard key={avatar.id} avatar={avatar} />
          ))}
        </div>
      </SectionCard>
    </div>
  );
}

