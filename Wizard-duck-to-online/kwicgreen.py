import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
from termcolor import colored
from collections import Counter

# 検索とコンテキスト表示を行う関数
def kwic_nltk(text, search_value, operation, window=3, color='red', sort_mode='sequential'):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    entities = ne_chunk(tagged)

    search_tokens = word_tokenize(search_value.lower())

    # 結果を保存するリスト
    results = []

    for i in range(len(tokens) - len(search_tokens) + 1):
        match = False

        if operation == "token":
            if [t.lower() for t in tokens[i:i + len(search_tokens)]] == search_tokens:
                match = True
        elif operation == "pos" and tagged[i][1] == search_value:
            match = True
        elif operation == "entity":
            for subtree in entities:
                if isinstance(subtree, Tree) and subtree.label() == search_value:
                    for leaf in subtree.leaves():
                        if leaf[0] == tokens[i]:
                            match = True
                            break

        if match:
            start = max(i - window, 0)
            end = min(i + len(search_tokens) + window, len(tokens))
            context = tokens[start:i] + \
                      [colored(" ".join(tokens[i:i + len(search_tokens)]), color, attrs=["bold"])] + \
                      tokens[i + len(search_tokens):end]
            result_text = "... " + " ".join(context) + " ..."
            results.append({
                'index': i,
                'context': result_text,
                'token': tokens[i],
                'pos': tagged[i][1]
            })

    # 表示順を選ぶ
    if sort_mode == 'most_freq_token':
        freq = Counter([r['token'].lower() for r in results])
        results.sort(key=lambda r: freq[r['token'].lower()], reverse=True)
    elif sort_mode == 'most_freq_pos':
        freq = Counter([r['pos'] for r in results])
        results.sort(key=lambda r: freq[r['pos']], reverse=True)
    # sequential の場合は順番通り（変更なし）

    # 結果表示
    for r in results:
        print(r['context'])

# テキストデータ（例文）
text = "Touching on education, allow me to briefly delve into UoA's unique undergraduate program. Our enrollment number is 240 per graduating class. That number may at first seem unimpressive. However, nurturing that many ICT conversant students each year is indeed unique in the field of information science in Japan and places us among the largest of all like-minded, informatics-leaned universities in Japan. We retain approximately 110 full-time faculty members. That means each faculty advisor's fair share is two to three students per graduating class. Such a low student-to-faculty ratio affords us the opportunity to provide our students with a complete package of individual lessons imparting knowledge and skills, followed up by caring and trusted mentoring to ensure students graduate with confidence in their abilities."

# ユーザーからの入力を受け取る
operation = input("Search type? (token / pos / entity): ").strip().lower()
target = input("Search target: ").strip()
sort_mode = input("Display order? (sequential / most_freq_token / most_freq_pos): ").strip().lower()

# 色の設定
color_map = {
    'token': 'red',
    'pos': 'blue',
    'entity': 'green'
}

# 実行
if operation in color_map:
    if operation == 'entity':
        target = target.upper()
    elif operation == 'token':
        target = target.lower()
    kwic_nltk(text, target, operation, window=5, color=color_map[operation], sort_mode=sort_mode)
else:
    print("Error: Unknown operation!")
