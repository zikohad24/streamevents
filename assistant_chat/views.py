import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .services.retriever import retrieve_events
from .services.prompts import build_prompt
from .services.llm_ollama import generate


def chat_page(request):
    return render(request, "assistant_chat/chat.html")


@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    message = (payload.get("message") or "").strip()
    only_future = bool(payload.get("only_future", True))

    if not message:
        return JsonResponse({"error": "Empty message"}, status=400)

    # RETRIEVAL
    ranked = retrieve_events(message, only_future=only_future, k=8)

    candidates = []
    for e, score in ranked:
        candidates.append({
            "id": int(e.pk),
            "title": e.title,
            "scheduled_date": e.scheduled_date.isoformat() if e.scheduled_date else None,
            "category": e.category,
            "tags": e.tags or "",
            "url": e.get_absolute_url(),
            "score": round(float(score), 3),
        })

    # GENERATION
    prompt = build_prompt(message, candidates)

    try:
        llm_text = generate(prompt)
    except Exception:
        llm_text = ""

    # Parse JSON resposta del model
    try:
        start = llm_text.find("{")
        end = llm_text.rfind("}") + 1
        llm_json = json.loads(llm_text[start:end])
    except Exception:
        # Fallback intel·ligent
        if candidates:
            llm_json = {
                "answer": f"He trobat {len(candidates)} esdeveniments relacionats amb la teva cerca:",
                "recommended_ids": [c["id"] for c in candidates[:3]],
                "follow_up": "Vols filtrar per alguna categoria o data concreta?"
            }
        else:
            llm_json = {
                "answer": "No he trobat esdeveniments que coincideixin amb la teva cerca. Prova amb altres paraules clau.",
                "recommended_ids": [],
                "follow_up": "Pots provar amb: música, gaming, tecnologia, yoga, art..."
            }

    # Seguretat: només IDs dels candidats reals
    allowed = {c["id"] for c in candidates}
    rec_ids = [i for i in llm_json.get("recommended_ids", []) if i in allowed]

    cards = [c for c in candidates if c["id"] in rec_ids]
    if not cards and candidates:
        cards = candidates[:3]

    return JsonResponse({
        "answer": llm_json.get("answer", ""),
        "follow_up": llm_json.get("follow_up", ""),
        "events": cards,
    })