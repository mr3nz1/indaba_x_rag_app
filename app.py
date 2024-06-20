from flask import Flask, request, jsonify
from indaba_x_rag_app.rag.rag import (
    llm,
    getDocs,
    translateEngToKiny,
    createAndStoreEmbeddings,
    searchLocalStore,
    translateKinyToEng,
)

app = Flask(__name__)


@app.route("/")
def main():
    return "<p>Hello World</p>"


@app.route("/query", methods=["POST"])
def post():
    prompt = request.json["prompt"]
    docs = getDocs()
    store = createAndStoreEmbeddings(docs)
    kinyToEngTranslation = translateKinyToEng(
        "You are a helpful assistant that translates kinyarwanda to english. You are supposed to answer the following question based on the following info. Just give me the translated text",
        prompt=prompt,
    )
    similarEmbedding = searchLocalStore(store, kinyToEngTranslation)
    engToKinyTranslation = translateEngToKiny(
        similarEmbedding,
        "You are a helpful assistant that translates kinyarwanda to english. You are supposed to answer the following question based on the following info. Just give me the translated text",
    )

    return jsonify({"message": engToKinyTranslation.content})


# run
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
