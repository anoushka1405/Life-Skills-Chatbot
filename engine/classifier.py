from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

SIMILARITY_THRESHOLD = 0.25


def classify_intent(user_text, options):

    if not user_text:
        return None

    user_emb = model.encode(user_text, convert_to_tensor=True)

    best = None
    best_score = -1

    for opt in options:

        opt_emb = model.encode(opt["description"], convert_to_tensor=True)

        score = util.cos_sim(user_emb, opt_emb).item()

        if score > best_score:
            best_score = score
            best = opt

    if best_score >= SIMILARITY_THRESHOLD:
        return best

    return None