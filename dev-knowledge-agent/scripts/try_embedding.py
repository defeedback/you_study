from app.services.embedding_service import EmbeddingService


def main():
    s = EmbeddingService()
    vecs = s.embed_texts(["天很蓝", "海很深"])
    print("数量:", len(vecs))
    print("维度:", len(vecs[0]))
    print("前5个值:", vecs[0][:5])


if __name__ == "__main__":
    main()
