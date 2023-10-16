import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer
from sklearn.model_selection import train_test_split
from qa_inputs import qa_list

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")


def preprocess_test():
    # Split the data into training and testing sets
    train_data, test_data = train_test_split(qa_list, test_size=0.3, random_state=42)

    # Create a DataFrame from qa_list
    df = pd.DataFrame(test_data)

    # Extract "question" and "context" columns as separate lists
    questions = [q.strip() for q in df["question"]]
    context = [q.strip() for q in df["context"]]

    inputs = tokenizer(
        questions,
        context,
        max_length=384,
        truncation="only_second",
        return_offsets_mapping=True,
        padding="max_length",
    )

    offset_mapping = inputs.pop("offset_mapping")

    start_positions = []
    end_positions = []
    answers = df["context"]
    for i, offset in enumerate(offset_mapping):
        answer = answers[i]
        start_char = 0
        end_char = len(answer) - 1
        sequence_ids = inputs.sequence_ids(i)

        # Find the start and end of the context
        idx = 0
        while sequence_ids[idx] != 1:
            idx += 1
        context_start = idx
        while sequence_ids[idx] == 1:
            idx += 1
        context_end = idx - 1

        # If the answer is not fully inside the context, label it (0, 0)
        if offset[context_start][0] > end_char or offset[context_end][1] < start_char:
            start_positions.append(0)
            end_positions.append(0)
        else:
            # Otherwise it's the start and end token positions
            idx = context_start
            while idx <= context_end and offset[idx][0] <= start_char:
                idx += 1
            start_positions.append(idx - 1)

            idx = context_end
            while idx >= context_start and offset[idx][1] >= end_char:
                idx -= 1
            end_positions.append(idx + 1)

    df["start_positions"] = start_positions
    df["end_positions"] = end_positions

    data = {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"],
        "start_positions": start_positions,
        "end_positions": end_positions,
    }
    df = pd.DataFrame(data)
    df.to_csv("encoding_test.csv", index=False)
    test = Dataset.from_pandas(df)
    return test
