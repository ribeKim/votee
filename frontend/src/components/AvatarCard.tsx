import type { ReactNode } from "react";

import type { AvatarSummary } from "../api/types";

interface AvatarCardProps {
  avatar: AvatarSummary;
  footer?: ReactNode;
}

export function AvatarCard({ avatar, footer }: AvatarCardProps) {
  return (
    <article className="avatar-card">
      <img className="avatar-card__image" src={avatar.image_url} alt={avatar.title} />
      <div className="avatar-card__body">
        <div className="avatar-card__heading">
          <h3>{avatar.title}</h3>
          {avatar.is_primary ? <span className="status-chip">대표</span> : null}
        </div>
        <p>{avatar.description ?? "설명이 아직 없습니다."}</p>
        <dl className="avatar-card__stats">
          <div>
            <dt>Elo</dt>
            <dd>{avatar.elo_rating}</dd>
          </div>
          <div>
            <dt>전적</dt>
            <dd>
              {avatar.wins}승 {avatar.losses}패
            </dd>
          </div>
        </dl>
        {footer ? <div className="avatar-card__footer">{footer}</div> : null}
      </div>
    </article>
  );
}
