from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

from app.config import Settings


@dataclass
class GeneratedAnalysis:
    summary: str
    strengths: str
    style_notes: str
    improvement_tips: str


class AnalysisService(Protocol):
    async def analyze_avatar(self, *, title: str, description: str | None, image_url: str, width: int, height: int) -> GeneratedAnalysis:
        ...


class TemplateAnalysisService:
    async def analyze_avatar(self, *, title: str, description: str | None, image_url: str, width: int, height: int) -> GeneratedAnalysis:
        aspect = "세로형" if height > width else "가로형" if width > height else "정방형"
        mood = "컨셉이 또렷하고 인상이 빠르게 읽히는 아바타" if description else "비주얼만으로도 첫인상을 전달하는 아바타"
        return GeneratedAnalysis(
            summary=f"{title}는 {aspect} 구도의 {mood}입니다.",
            strengths="실루엣이 분명하고 썸네일에서도 인지가 쉬운 편입니다.",
            style_notes="대표 색상과 표정, 헤어/의상 포인트를 한두 개 더 강조하면 캐릭터성이 더 선명해집니다.",
            improvement_tips="프로필용 대표 컷과 월드컵용 전신 컷을 분리해 업로드하면 활용도가 높아집니다.",
        )


class OpenAIAnalysisService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def analyze_avatar(self, *, title: str, description: str | None, image_url: str, width: int, height: int) -> GeneratedAnalysis:
        prompt = (
            "You are an avatar stylist. Return Korean feedback with sections: summary, strengths, "
            "style_notes, improvement_tips. Focus on avatar style, concept consistency, readability, "
            "and practical improvement advice. Do not give numeric beauty scores."
        )
        payload = {
            "model": self.settings.openai_model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_text", "text": f"title={title}; description={description or ''}; size={width}x{height}"},
                        {"type": "input_image", "image_url": image_url},
                    ],
                }
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post("https://api.openai.com/v1/responses", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        text = ""
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    text += content.get("text", "")
        normalized = text.strip() or "summary: 분석 결과를 생성하지 못했습니다.\nstrengths: 입력 이미지 정보가 부족했습니다.\nstyle_notes: 다시 시도해 주세요.\nimprovement_tips: 다른 대표 컷을 업로드해 보세요."
        sections = _parse_analysis_sections(normalized)
        return GeneratedAnalysis(**sections)


def _parse_analysis_sections(payload: str) -> dict[str, str]:
    result = {
        "summary": "",
        "strengths": "",
        "style_notes": "",
        "improvement_tips": "",
    }
    current_key = "summary"
    for raw_line in payload.splitlines():
        line = raw_line.strip()
        lowered = line.lower()
        if lowered.startswith("summary:"):
            current_key = "summary"
            result[current_key] = line.partition(":")[2].strip()
            continue
        if lowered.startswith("strengths:"):
            current_key = "strengths"
            result[current_key] = line.partition(":")[2].strip()
            continue
        if lowered.startswith("style_notes:"):
            current_key = "style_notes"
            result[current_key] = line.partition(":")[2].strip()
            continue
        if lowered.startswith("improvement_tips:"):
            current_key = "improvement_tips"
            result[current_key] = line.partition(":")[2].strip()
            continue
        if line:
            existing = result[current_key]
            result[current_key] = f"{existing} {line}".strip()
    return {key: value or "준비된 분석 내용이 없습니다." for key, value in result.items()}

