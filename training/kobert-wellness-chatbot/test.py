import torch
import torch.nn as nn
import random
import pandas as pd
import numpy as np

from model.classifier import KoBERTforSequenceClassfication
from kobert_transformers import get_tokenizer
from tqdm import tqdm


def load_wellness_answer():
    root_path = "."
    category_path = f"{root_path}/data/dialog_category.txt"
    answer_path = f"{root_path}/data/dialog_answer.txt"

    c_f = open(category_path, 'r')
    a_f = open(answer_path, 'r')

    category_lines = c_f.readlines()
    answer_lines = a_f.readlines()

    category = {}
    answer = {}
    for line_num, line_data in enumerate(category_lines):
        data = line_data.split('\t')
        category[data[1][:-1]] = data[0]

    for line_num, line_data in enumerate(answer_lines):
        data = line_data.split('\t')
        keys = answer.keys()
        if (data[0] in keys):
            answer[data[0]] += [data[1][:-1]]
        else:
            answer[data[0]] = [data[1][:-1]]

    return category, answer


def kobert_input(tokenizer, str, device=None, max_seq_len=512):
    index_of_words = tokenizer.encode(str)
    token_type_ids = [0] * len(index_of_words)
    attention_mask = [1] * len(index_of_words)

    # Padding Length
    padding_length = max_seq_len - len(index_of_words)

    # Zero Padding
    index_of_words += [0] * padding_length
    token_type_ids += [0] * padding_length
    attention_mask += [0] * padding_length

    data = {
        'input_ids': torch.tensor([index_of_words]).to(device),
        'token_type_ids': torch.tensor([token_type_ids]).to(device),
        'attention_mask': torch.tensor([attention_mask]).to(device),
    }
    return data

if __name__ == "__main__":
    root_path = "."
    checkpoint_path = f"{root_path}/checkpoint"
    save_ckpt_path = f"{checkpoint_path}/kobert-wellness-text-classification.pth"

    # 답변과 카테고리 불러오기
    category, answer = load_wellness_answer()

    ctx = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(ctx)

    # 저장한 Checkpoint 불러오기
    checkpoint = torch.load(save_ckpt_path, map_location=device)

    model = KoBERTforSequenceClassfication()
    model.load_state_dict(checkpoint['model_state_dict'])

    model.to(ctx)
    model.eval()

    tokenizer = get_tokenizer()

    while 1:
        sent = input('\nQuestion: ')  # '요즘 기분이 우울한 느낌이에요'
        data = kobert_input(tokenizer, sent, device, 512)

        if '종료' in sent:
            break

        output = model(**data)

        logit = output[0]
        softmax_logit = torch.softmax(logit, dim=-1)
        softmax_logit = softmax_logit.squeeze()

        max_index = torch.argmax(softmax_logit).item()
        max_index_value = softmax_logit[torch.argmax(softmax_logit)].item()

        answer_list = answer[category[str(max_index)]]
        answer_len = len(answer_list) - 1
        answer_index = random.randint(0, answer_len)

        print(f'Answer: {answer_list[answer_index]}, index: {max_index}, softmax_value: {max_index_value}')
        
        print('-' * 50)



    # Load the labeled dataset for evaluation
    eval_data = pd.read_csv('/content/drive/MyDrive/자진프/data/data_for_train.csv')  # Replace 'path_to_eval_dataset.csv' with the actual path to your evaluation dataset
    eval_texts = eval_data['answer'].tolist()
    eval_labels = eval_data['encoding'].tolist()

    correct_predictions = 0
    total_predictions = 0

    for text, label in tqdm(zip(eval_texts, eval_labels), total=len(eval_texts), desc='Evaluating'):
        
        index_of_words = tokenizer.encode(text)
        if len(index_of_words) > 512:
            continue

        data = kobert_input(tokenizer, text, device, 512)
        output = model(**data)
        logit = output[0]
        softmax_logit = torch.softmax(logit, dim=-1)
        predicted_label = torch.argmax(softmax_logit).item()

        if predicted_label == label:
            correct_predictions += 1

        total_predictions += 1

    accuracy = correct_predictions / total_predictions
    print(f'Accuracy: {accuracy:.4f}')