# Generated by ChatGPT
import sys
import nltk
import wikipedia
from nltk import word_tokenize, pos_tag, ne_chunk, sent_tokenize
from nltk.tree import Tree
from termcolor import colored
from collections import Counter, defaultdict

def kwic_nltk(text, search_value, operation, window, color, sort_mode, next_n=1):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    entities = ne_chunk(tagged)
    search_tokens = word_tokenize(search_value.lower())
    results = []

    next_word_counter = Counter()
    next_word_examples = defaultdict(list)
    next_word_pos_counter = Counter()
    next_word_pos_examples = defaultdict(list)

    # entity検索用にエンティティの単語位置を取得しておく
    entity_word_positions = set()
    if operation == 3:
        for subtree in entities:
            if isinstance(subtree, Tree) and subtree.label() == search_value:
                for leaf in subtree.leaves():
                    # tokens中のleaf[0]と一致する単語のインデックスを取得
                    # トークン化のズレに注意しつつ単純な検索を行う
                    for i, token in enumerate(tokens):
                        if token == leaf[0]:
                            entity_word_positions.add(i)

    for i in range(len(tokens) - len(search_tokens) + 1):
        match = False

        if operation == 1:
            if [t.lower() for t in tokens[i:i + len(search_tokens)]] == search_tokens:
                match = True
        elif operation == 2:
            if tagged[i][1] == search_value:
                match = True
        elif operation == 3:
            if i in entity_word_positions:
                match = True

        if match:
            start = max(i - window, 0)
            end = min(i + len(search_tokens) + window, len(tokens))
            context = tokens[start:i] + \
                      [colored(" ".join(tokens[i:i + len(search_tokens)]), color, attrs=["bold"])] + \
                      tokens[i + len(search_tokens):end]
            results.append({
                'index': i,
                'context': "... " + " ".join(context) + " ...",
                'token': " ".join(tokens[i:i + len(search_tokens)]),
                'pos': " ".join([tagged[j][1] for j in range(i, i + len(search_tokens))])
            })

            # 次の単語やPOSの収集
            if i + len(search_tokens) < len(tokens):
                next_words = tuple(tokens[i + len(search_tokens):i + len(search_tokens) + next_n])
                next_pos = tuple(tagged[j][1] for j in range(i + len(search_tokens), min(i + len(search_tokens) + next_n, len(tokens))))
                if next_words:
                    next_word_counter[next_words] += 1
                    next_word_examples[next_words].append("... " + " ".join(context) + " ...")
                if next_pos:
                    next_word_pos_counter[next_pos] += 1
                    next_word_pos_examples[next_pos].append("... " + " ".join(context) + " ...")

    # ソートモードの処理はあなたの既存コードのままでOKです。

    if operation == 1:
        if sort_mode == 2:
            print(f"\nOrder of appearance frequency（「{search_value} + next word」）:")
            for next_words, count in next_word_counter.most_common():
                pair = search_value + " " + " ".join(next_words)
                print(f"{pair}: {count}")
                for example in next_word_examples[next_words]:
                    print(example)
            return
        elif sort_mode == 3:
            print(f"\nOrder of appearance frequency（「{search_value} + <POS of next word>」）:")
            for pos, count in next_word_pos_counter.most_common():
                pos_str = " ".join(pos)
                print(f"{search_value} <{pos_str}>: {count}")
                for example in next_word_pos_examples[pos]:
                    print(example)
            return

    if sort_mode in [2, 3] and operation in [2, 3]:
        if operation == 2 and sort_mode == 2:
            print(f"\nOrder of appearance frequency（<{search_value}> + next word）:")
            for next_words, count in next_word_counter.most_common():
                pair = f"<{search_value}> " + " ".join(next_words)
                print(f"{pair}: {count}")
                for example in next_word_examples[next_words]:
                    print(example)
            return
        if operation == 2 and sort_mode == 3:
            print(f"\nOrder of appearance frequency（<{search_value}> + <POS of next word>）:")
            for pos, count in next_word_pos_counter.most_common():
                pos_str = " ".join(pos)
                print(f"<{search_value}> <{pos_str}>: {count}")
                for example in next_word_pos_examples[pos]:
                    print(example)
            return
        if operation == 3 and sort_mode == 2:
            print(f"\nOrder of appearance frequency（<{search_value}> + next word）:")
            for next_words, count in next_word_counter.most_common():
                pair = f"<{search_value}> " + " ".join(next_words)
                print(f"{pair}: {count}")
                for example in next_word_examples[next_words]:
                    print(example)
            return
        if operation == 3 and sort_mode == 3:
            print(f"\nOrder of appearance frequency（<{search_value}> + <POS of next word>）:")
            for pos, count in next_word_pos_counter.most_common():
                pos_str = " ".join(pos)
                print(f"<{search_value}> <{pos_str}>: {count}")
                for example in next_word_pos_examples[pos]:
                    print(example)
            return

    # 順次表示
    for r in results:
        print(r['context'])

interest = input("What is your interest: ")
try:
    text = wikipedia.summary(interest)
except wikipedia.exceptions.PageError:
    print("There is no interest.")
    sys.exit()
except wikipedia.exceptions.DisambiguationError as e:
    print("This interest is ambiguous. Please be more specific.")
    print("candidate: ", e.options)
    sys.exit()

# ユーザーからの入力を受け取る
operation = int(input("Search type? (token(1) / pos(2) / entity(3)): "))
target = input("Search target: ").strip()
sort_mode = int(input("Display order? (sequential(1) / most freq token(2) / most freq pos(3)): "))
window = int(input("Window size: "))

# 色の設定
color_map = {
    1: 'red',
    2: 'blue',
    3: 'green'
}

# 実行
if operation in color_map:
    if operation == 3:
        target = target.upper()
    elif operation == 1:
        target = target.lower()
    kwic_nltk(text, target, operation, window, color_map[operation], sort_mode)
else:
    print("Error: Unknown operation!")