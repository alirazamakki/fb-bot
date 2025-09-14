from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class WeightedLink:
    id: int
    url: str
    weight: int = 1


def choose_weighted_link(links: List[WeightedLink]) -> Optional[WeightedLink]:
    if not links:
        return None
    total = sum(max(1, l.weight) for l in links)
    r = random.uniform(0, total)
    upto = 0.0
    for link in links:
        upto += max(1, link.weight)
        if upto >= r:
            return link
    return links[-1]


def build_caption(template: str, link_url: Optional[str], group_name: Optional[str] = None) -> str:
    caption = template
    if link_url:
        caption = caption.replace("{LINK}", link_url)
    if group_name:
        caption = caption.replace("{GROUP}", group_name)
    return caption

