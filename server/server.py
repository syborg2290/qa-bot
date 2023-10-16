from transformers import (
    AutoModelForQuestionAnswering,
    AutoTokenizer,
)
import torch
import nltk
from nltk.corpus import stopwords
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from context_search import search_contexts, related_questions

# from custom_stop_words import custom_stop_words


app = Flask(__name__)

# Allow requests from all origins in development
cors = CORS(app)

# Initialize the fine-tuned tokenizer and model


bert_qa_model = AutoModelForQuestionAnswering.from_pretrained("bert_qa")
bert_qa_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")


with open("combined_context.txt", "r") as file:
    context = file.read()

# Download NLTK stop words
nltk.download("stopwords")


def convert_answer(question, context_text):
    # Tokenize the input
    inputs = bert_qa_tokenizer(question, context_text, return_tensors="pt")

    # Get the answer from the model
    answer = bert_qa_model(**inputs)

    # Find the token positions with the highest values in start_logits and end_logits
    start_idx = torch.argmax(answer.start_logits)
    end_idx = torch.argmax(answer.end_logits) + 1  # Add 1 to include the end token

    # Convert the token positions to text spans
    answer_start = bert_qa_tokenizer.convert_tokens_to_string(
        bert_qa_tokenizer.convert_ids_to_tokens(inputs.input_ids[0][start_idx:end_idx])
    )

    # Calculate the confidence score
    start_score = torch.max(answer.start_logits).item()
    end_score = torch.max(answer.end_logits).item()
    confidence_score = (start_score + end_score) / 2.0

    # Return the answer and its confidence score as a dictionary
    return {"answer": answer_start, "score": confidence_score}


def most_related_pair(context_related, filtered_keywords):
    pair = []
    context_arr_related = [
        sentence.strip() for sentence in context_related if sentence.strip()
    ]
    related_pair = related_questions(context_arr_related, filtered_keywords)
    for single_pair in related_pair:
        pair.append(
            {
                "question": single_pair.split("[QA]")[0],
                "answer": single_pair.split("[QA]")[1],
            }
        )
    return pair


@app.route("/answer", methods=["POST"])
@cross_origin()
def get_answer():
    try:
        data = request.json
        question = data["question"]
        context_text = data["context"]

        answers = []

        stop_words = set(stopwords.words("english"))

        filtered_keywords = [
            word for word in question.split() if word.lower() not in stop_words
        ]

        answers = []

        if context_text == "":
            context_arr = context.split("[SEP]")  # Fixed the variable name
            context_arr = [
                sentence.strip() for sentence in context_arr if sentence.strip()
            ]
            matching_contexts = search_contexts(context_arr, filtered_keywords)

            for each_context in matching_contexts:
                # Get human-readable answer from the get_answer function

                answer = convert_answer(question, each_context.split("[QA]")[1])
                answers.append(
                    {
                        "answer": answer["answer"],
                        "score": answer["score"],
                    }
                )

        else:
            # Get human-readable answer from the get_answer function
            answer = convert_answer(question, context_text)
            answers.append(answer)

        related = most_related_pair(context.split("[SEP]"), filtered_keywords)

        response = {"question": question, "answers": answers, "related": related}

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
