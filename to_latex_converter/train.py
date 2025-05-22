from transformers import AutoTokenizer, VisionEncoderDecoderModel, AutoImageProcessor
from PIL import Image
import requests
import os

from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments
from datasets import load_dataset
from PIL import Image
import torch

feature_extractor = AutoImageProcessor.from_pretrained("MixTex/ZhEn-Latex-OCR")
tokenizer = AutoTokenizer.from_pretrained("MixTex/ZhEn-Latex-OCR")
model = VisionEncoderDecoderModel.from_pretrained("MixTex/ZhEn-Latex-OCR")

# --- Добавляем русские символы в токенизатор ---
russian_chars = [chr(code) for code in range(ord('а'), ord('я')+1)] + \
                [chr(code) for code in range(ord('А'), ord('Я')+1)] + ['ё', 'Ё']

added_tokens = []
for char in russian_chars:
    if tokenizer.convert_tokens_to_ids(char) == tokenizer.unk_token_id:
        added_tokens.append(char)

if added_tokens:
    tokenizer.add_tokens(added_tokens)
    print(f"Добавлено токенов: {len(added_tokens)}")
    model.decoder.resize_token_embeddings(len(tokenizer))
else:
    print("Все русские символы уже есть в токенизаторе.")

# --- Новый класс датасета для локальных файлов ---
from torch.utils.data import Dataset
class MyDataset(Dataset):
    def __init__(self, img_dir, text_dir, tokenizer, feature_extractor, max_length=296):
        self.img_dir = img_dir
        self.text_dir = text_dir
        self.tokenizer = tokenizer
        self.feature_extractor = feature_extractor
        self.max_length = max_length
        self.img_files = sorted([f for f in os.listdir(img_dir) if f.endswith('.png')])

    def __len__(self):
        return len(self.img_files)

    def __getitem__(self, idx):
        img_name = self.img_files[idx]
        img_path = os.path.join(self.img_dir, img_name)
        text_path = os.path.join(self.text_dir, img_name.replace('.png', '.txt'))

        image = Image.open(img_path).convert("RGB")
        with open(text_path, 'r', encoding='utf-8') as f:
            target_text = f.read().strip()

        pixel_values = self.feature_extractor(image, return_tensors="pt").pixel_values
        target = self.tokenizer(target_text, padding="max_length", max_length=self.max_length, truncation=True).input_ids
        labels = [label if label != self.tokenizer.pad_token_id else -100 for label in target]
        return {"pixel_values": pixel_values.squeeze(), "labels": torch.tensor(labels)}

traindataset = MyDataset(
    img_dir="data/img",
    text_dir="data/txt",
    tokenizer=tokenizer,
    feature_extractor=feature_extractor
)

training_args = Seq2SeqTrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=32,
    predict_with_generate=True,
    logging_dir='./logs',
    learning_rate=2e-5,
    weight_decay=0.01,
    save_total_limit=2,
    logging_steps=50,
    save_steps=1000,
    num_train_epochs=5,
    warmup_steps=500,
    # evaluation_strategy="steps",
    # eval_steps=1000,
    # load_best_model_at_end=True,
    # metric_for_best_model="loss",
    # greater_is_better=False,
    # fp16=True,
    gradient_accumulation_steps=4,
    gradient_checkpointing=True,
    optim="adamw_torch",
    # lr_scheduler_type="cosine",
)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=traindataset,
)
trainer.train()
tokenizer.save_pretrained("./results/tokenizer")