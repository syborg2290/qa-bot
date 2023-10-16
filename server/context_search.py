import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity


def search_contexts(context, keywords):
    matching_sentences = []

    # Create a set of whole words from the keywords
    keyword_set = set(keywords)

    # First, find sentences that contain all whole keywords
    for sentence in context:
        if all(word in sentence.split() for word in keyword_set):
            matching_sentences.insert(0, sentence)
            if len(matching_sentences) == 5:
                return matching_sentences

    # Then, find additional sentences that contain any of the whole keywords
    for sentence in context:
        if (
            any(word in sentence.split() for word in keyword_set)
            and sentence not in matching_sentences
        ):
            matching_sentences.append(sentence)
            if len(matching_sentences) == 5:
                return matching_sentences

    return matching_sentences


def related_questions(context, keywords):
    related_sentences = []

    # Create a set of whole words from the keywords
    keyword_set = set(keywords)

    # First, find sentences that contain all whole keywords
    for sentence in context:
        if all(word in sentence.split() for word in keyword_set):
            related_sentences.insert(0, sentence)
            if len(related_sentences) == 5:
                return related_sentences

    # Then, find additional sentences that contain any of the whole keywords
    for sentence in context:
        if (
            any(word in sentence.split() for word in keyword_set)
            and sentence not in related_sentences
        ):
            related_sentences.append(sentence)
            if len(related_sentences) == 5:
                return related_sentences

    return related_sentences


def get_most_relevant_context(question, context_list):
    # Load pre-trained model and tokenizer
    model_name = "bert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Tokenize the question and contexts
    question_tokens = tokenizer(
        question, return_tensors="pt", padding=True, truncation=True
    )
    context_tokens = tokenizer(
        context_list,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512,  # You can adjust this value based on your specific use case
        return_attention_mask=True,
    )

    # Generate embeddings for the question and contexts
    with torch.no_grad():
        question_embedding = model(**question_tokens).last_hidden_state.mean(dim=1)
        context_embeddings = model(
            input_ids=context_tokens.input_ids
        ).last_hidden_state.mean(dim=1)

    # Calculate cosine similarities between the question and contexts
    similarities = cosine_similarity(question_embedding, context_embeddings)

    # Find the index of the most similar context
    most_similar_index = similarities.argmax()

    # Get the most relevant context
    most_relevant_context = context_list[most_similar_index]

    print("most_relevant_context : " + most_relevant_context)

    return most_relevant_context
