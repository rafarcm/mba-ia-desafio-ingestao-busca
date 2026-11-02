from search import search_prompt


def main():
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Faça sua pergunta (digite 'sair' para encerrar):")

    while True:
        try:
            pergunta = input("\nPERGUNTA: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if pergunta.lower() == "sair":
            break
        if not pergunta:
            continue

        try:
            resposta = chain.invoke(pergunta)
        except Exception as e:
            print(f"Erro ao gerar a resposta: {e}")
            continue

        print(f"RESPOSTA: {resposta.strip()}")

    print("Até logo!")


if __name__ == "__main__":
    main()
