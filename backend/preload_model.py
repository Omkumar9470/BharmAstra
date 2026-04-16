from transformers import pipeline
print("Pre-downloading FinBERT...")
pipeline("text-classification", model="ProsusAI/finbert", tokenizer="ProsusAI/finbert", top_k=None)
print("Done.")
