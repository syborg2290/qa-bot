from transformers import AutoModelForQuestionAnswering, TrainingArguments, Trainer
from transformers import AutoTokenizer
from preprocess_train import preprocess_train
from preprocess_test import preprocess_test

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

model = AutoModelForQuestionAnswering.from_pretrained("distilbert-base-uncased")


training_args = TrainingArguments(
    output_dir="bert_qa",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    push_to_hub=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=preprocess_train(),
    eval_dataset=preprocess_test(),
    tokenizer=tokenizer,
)

trainer.train()

# Save the model after training
trainer.save_model()
