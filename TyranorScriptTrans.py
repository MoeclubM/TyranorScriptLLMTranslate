import re
import os
import time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

# 设置OpenAI API密钥
client = OpenAI(
    base_url="https://api.siliconflow.cn/v1",
    api_key='sk-xxxxxxxxxxxxxxx'
    )

def extract_text_blocks(content):
    # 使用正则表达式匹配[tb_start_text mode=1 ]和[_tb_end_text]之间的文本
    pattern = r'\[tb_start_text mode=1 \](.*?)\[_tb_end_text\]'
    matches = re.finditer(pattern, content, re.DOTALL)
    return [(m.group(0), m.group(1).strip()) for m in matches]

def translate_text(text):
    try:
        completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=[
                {"role": "system", "content": "You are a professional Japanese to Simplified Chinese translator."},
                {"role": "user", "content": f"Translate the following Japanese text to Simplified Chinese ,do not send me any words except the result: {text}"}
            ],
        )
        translated_text = completion.choices[0].message.content.strip()
        print(f"Translated text: {translated_text}")
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        return None

def process_file(input_file, output_file):
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取需要翻译的文本块
        text_blocks = extract_text_blocks(content)
        
        # 使用多线程进行翻译
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_block = {executor.submit(translate_text, text): (full_block, text) for full_block, text in text_blocks if text.strip()}
            for future in as_completed(future_to_block):
                full_block, text = future_to_block[future]
                translated = future.result()
                if translated:
                    # 保持原始格式，只替换文本部分
                    new_block = f'[tb_start_text mode=1 ]\n{translated}[p]\n[_tb_end_text]'
                    content = content.replace(full_block, new_block)
                    
                    # 添加延迟以避免API限制
                    time.sleep(0.1)

        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Translation completed successfully!")

    except Exception as e:
        print(f"Error processing file: {e}")

# 使用示例
input_file = ""
output_file = ''
process_file(input_file, output_file)