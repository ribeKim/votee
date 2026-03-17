from __future__ import annotations


def update_elo(winner_rating: int, loser_rating: int, k_factor: int = 24) -> tuple[int, int]:
    winner_expected = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    loser_expected = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
    updated_winner = round(winner_rating + k_factor * (1 - winner_expected))
    updated_loser = round(loser_rating + k_factor * (0 - loser_expected))
    return updated_winner, updated_loser

