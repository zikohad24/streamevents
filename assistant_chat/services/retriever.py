from django.utils import timezone
from events.models import Event
from semantic_search.services.embeddings import embed_text
from semantic_search.services.ranker import cosine_top_k

def build_event_text(e: Event) -> str:
    return " | ".join([
        (e.title or "").strip(),
        (e.description or "").strip(),
        (e.category or "").strip(),
        (e.tags or "").strip(),
    ]).strip()

def retrieve_events(query: str, only_future: bool = True, k: int = 8):
    q_vec = embed_text(query)

    qs = Event.objects.all()
    if only_future:
        qs = qs.filter(scheduled_date__gte=timezone.now())

    items = []
    for e in qs.only("id", "title", "scheduled_date", "category", "tags", "embedding"):
        emb = getattr(e, "embedding", None)
        if isinstance(emb, list) and len(emb) > 0:
            items.append((e, emb))

    ranked = cosine_top_k(q_vec, items, k=max(k, 20))

    # Llindar mínim per evitar recomanar qualsevol cosa
    ranked = [(e, s) for (e, s) in ranked if s >= 0.25]

    return ranked[:k]