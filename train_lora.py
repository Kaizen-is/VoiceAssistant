"""LoRA fine-tune Qwen 2.5 1.5B Instruct on the Jarvis dataset.

Run:
    python data/build_dataset.py   # first, to produce train.jsonl + val.jsonl
    python train_lora.py

Trains ~1% of parameters via LoRA in 4-bit — fits on an RTX 3060 12 GB in
about 5-6 GB VRAM. Expect 10-20 minutes for 3 epochs on ~500 rows.

Output: models/jarvis-lora/ (LoRA adapter, ~30 MB — much smaller than the
base model, so training is fast and the adapter is portable).
"""
# Обучение LoRA-адаптера на датасете Джарвиса
from pathlib import Path

# Route SSL through the OS trust store — fixes HF/PyPI cert issues on some Windows setups
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (AutoModelForCausalLM, AutoTokenizer,
                          BitsAndBytesConfig)
from trl import SFTConfig, SFTTrainer

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "models" / "jarvis-lora"
BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
MAX_SEQ_LEN = 512


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading base model in 4-bit: {BASE_MODEL}")
    # Квантизация в 4 бита — экономия VRAM
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb,
        device_map="auto",
    )
    model = prepare_model_for_kbit_training(model)

    print("Attaching LoRA adapter...")
    # LoRA обучает ~1% параметров
    lora = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    print("Loading dataset...")
    # Загружаем train и val
    train_ds = load_dataset("json", data_files=str(DATA_DIR / "train.jsonl"), split="train")
    val_ds = load_dataset("json", data_files=str(DATA_DIR / "val.jsonl"), split="train")

    # Форматируем каждую строку через шаблон чата Qwen
    def format_row(row):
        return {"text": tokenizer.apply_chat_template(
            row["messages"], tokenize=False, add_generation_prompt=False)}

    train_ds = train_ds.map(format_row, remove_columns=train_ds.column_names)
    val_ds = val_ds.map(format_row, remove_columns=val_ds.column_names)
    print(f"  train: {len(train_ds)} rows | val: {len(val_ds)} rows")

    # Настройки обучения
    cfg = SFTConfig(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,          # эффективный батч = 8
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_steps=20,                        # ~10% of ~190 total steps
        weight_decay=0.01,
        optim="paged_adamw_8bit",
        bf16=True,
        fp16=False,
        max_length=MAX_SEQ_LEN,
        dataset_text_field="text",
        packing=False,                          # тексты короткие, пакование не нужно
        logging_steps=5,
        save_strategy="epoch",
        eval_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",
        seed=42,
    )

    print("Starting training...")
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        args=cfg,
    )
    trainer.train()

    # Сохраняем адаптер и токенизатор
    trainer.save_model(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    print(f"\nLoRA adapter saved to: {OUTPUT_DIR}")
    print("Now edit config.py to set STYLIZER_ENABLED = True (already the default)")


if __name__ == "__main__":
    main()
