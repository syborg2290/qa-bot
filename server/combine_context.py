from qa_inputs import qa_list

# Extract all the context and answers
context_and_answers = []

for item in qa_list:
    question = item["question"]
    context = item["context"]
    context = context.replace("\n", " ").replace("\r", " ")
    context_and_answers.append(question + "[QA]" + context)

# Combine context and answers into a single paragraph with answers separated by commas
combined_text = "[SEP]".join(context_and_answers)

output_file = "combined_context.txt"

# Write the combined context to the text file
with open(output_file, "w") as file:
    file.write(combined_text)

print(f"Combined context has been saved to {output_file}")
