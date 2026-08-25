import tiktoken


# cl100k_base is a real byte-pair encoding used by production GPT models
ENCODING = tiktoken.get_encoding("cl100k_base")


def show_tokens(text: str) -> None:
    """ Print each token's ID next to its decoded text """

    # calling the encoder to do the tokenization process
    token_ids = ENCODING.encode(text)

    print(f"\n {text}")
    print(f"\t{len(text.split())} words -> {len(token_ids)} tokens")

    for token_id in token_ids:
        chunk = ENCODING.decode([token_id])
        print(f"\t{token_id:>6} -> '{chunk}'")


if __name__ == "__main__":
    print("=== SHOW TOKENS ===")
    show_tokens("the quick brown fox")
    show_tokens("unbelievable")
    show_tokens("Pneumono­ultra­micro­scopic­silico­volcano­coniosis")      # includes invisible characters that are token id 5879

    # comparing tokens across languages
    show_tokens("The customer wants a refund today.")           # English
    show_tokens("El cliente quiere un reembolso hoy.")          # Spanish
    show_tokens("お客様は本日返金を希望しています。")               # Japanese