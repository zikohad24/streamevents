from django.shortcuts import render
from django.utils import timezone

from events.models import Event
from .services.embeddings import embed_text, model_name
from .services.ranker import cosine_top_k


def semantic_search(request):
    q = (request.GET.get("q") or "").strip()
    only_future = request.GET.get("future", "") == "1"  # Cambiado aquí

    results = []
    debug_info = {
        'total_events': Event.objects.count(),
        'events_con_embedding': Event.objects.filter(embedding__isnull=False).count(),
        'only_future': only_future,
    }

    if q:
        q_vec = embed_text(q)
        debug_info['query_vec_length'] = len(q_vec)

        qs = Event.objects.all()
        debug_info['before_filter'] = qs.count()

        if only_future:
            qs = qs.filter(scheduled_date__gte=timezone.now())
            debug_info['after_filter'] = qs.count()

        # Cargamos candidatos y hacemos ranking en Python
        items = []
        for e in qs:
            emb = getattr(e, "embedding", None)
            if emb:
                items.append((e, emb))

        debug_info['items_with_embedding'] = len(items)

        ranked = cosine_top_k(q_vec, items, k=20)
        results = ranked

        debug_info['results_count'] = len(results)

    context = {
        "query": q,
        "results": results,
        "only_future": only_future,
        "embedding_model": model_name(),
        "debug": debug_info,
    }
    return render(request, "semantic_search/search.html", context)