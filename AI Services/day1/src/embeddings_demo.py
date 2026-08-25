
import math


# words are keys, vector embeddings are values
WORD_VECTORS = {

    # vectors are generally on a scale of -1 to 1
    #   real models have WAY more embeddings dimensions that are more ambiguous
    # 
    #           royalty    gender   fruit    technology
    "king":      [0.95,     0.30,    0.00,     0.00],
    "queen":     [0.95,    -0.30,    0.00,     0.00],
    "man":       [0.10,     0.95,    0.00,     0.00],
    "woman":     [0.10,    -0.95,    0.00,     0.00],
    "apple":     [0.00,     0.00,    0.95,     0.20],
    "orange":    [0.00,     0.00,    0.80,     0.05],
    "computer":  [0.00,     0.00,    0.05,     0.90],
    "laptop":    [0.00,     0.00,    0.05,     0.85],
}



def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:

    # calculating how similar two values are together
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    return dot_product / (magnitude_a * magnitude_b)


def most_similar(target_vector: list[float], exclude: set[str]) -> tuple[str | None, float]:
    """ nearest neighbor by cosine similarity """

    best_word, best_score = None, -1.0

    for word, vector in WORD_VECTORS.items():

        # if we don't want to check any words, continue on to next word
        if word in exclude:
            continue

        # similarity of the given vector to each vector in the "embeddings database" (aka.. dict for WORD_VECTORS)
        score = cosine_similarity(target_vector, vector)

        if score > best_score:
            best_word, best_score = word, score

    return best_word, best_score



if __name__ == "__main__":

    print("=== COSINE SIMILARITY ===")
    for word_a, word_b in [("king", "queen"), ("man", "woman"), ("apple", "orange"), ("computer", "laptop")]:
        score = cosine_similarity(WORD_VECTORS[word_a], WORD_VECTORS[word_b])
        print(f"  similarity({word_a}, {word_b}) = {score:.3f}")



    print("=== SIMILAR WORDS ===")

    # grab vectors for these three words
    king, man, woman = WORD_VECTORS["king"], WORD_VECTORS["man"], WORD_VECTORS["woman"]

    # generate a vector of these three values
    result_vector = [k - m + w for k, m, w in zip(king, man, woman)]

    # find the word in the knowledge base that is most similar to this new "prompt"
    nearest_word, score = most_similar(result_vector, exclude={"king", "man", "woman"})

    print(f"  most_similar('king', 'man', 'woman') = {nearest_word} with score {score:.3f}")