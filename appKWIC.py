import tkinter as tk
from tkinter import ttk, messagebox
import wikipedia
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
from collections import Counter, defaultdict

def kwic_nltk(text, search_value, operation, window, next_n=1, sort_mode=1):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    entities = ne_chunk(tagged)
    search_tokens = word_tokenize(search_value.lower())
    results = []

    next_word_counter = Counter()
    next_word_examples = defaultdict(list)
    next_word_pos_counter = Counter()
    next_word_pos_examples = defaultdict(list)

    entity_word_positions = set()
    if operation == 3:
        for subtree in entities:
            if isinstance(subtree, Tree) and subtree.label() == search_value:
                for leaf in subtree.leaves():
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
            ctx = tokens[start:end]
            hi_start = i - start
            hi_end = hi_start + len(search_tokens)

            results.append({
                'context': ctx,
                'highlight_start': hi_start,
                'highlight_end': hi_end
            })

            if i + len(search_tokens) < len(tokens):
                next_words = tuple(tokens[i + len(search_tokens):i + len(search_tokens) + next_n])
                next_pos = tuple(tagged[j][1] for j in range(i + len(search_tokens), min(i + len(search_tokens) + next_n, len(tokens))))
                if next_words:
                    next_word_counter[next_words] += 1
                    next_word_examples[next_words].append(ctx)
                if next_pos:
                    next_word_pos_counter[next_pos] += 1
                    next_word_pos_examples[next_pos].append(ctx)

    return {
        'results': results,
        'next_word_freq': next_word_counter,
        'next_word_examples': next_word_examples,
        'next_pos_freq': next_word_pos_counter,
        'next_pos_examples': next_word_pos_examples
    }

def run_kwic():
    interest = entry_interest.get().strip()
    if not interest:
        messagebox.showerror("入力エラー", "興味のあるテーマを入力してください。")
        return

    try:
        text = wikipedia.summary(interest)
    except wikipedia.exceptions.PageError:
        messagebox.showerror("エラー", "そのテーマのページは見つかりません。")
        return
    except wikipedia.exceptions.DisambiguationError as e:
        messagebox.showerror("エラー", f"曖昧なテーマです。候補: {', '.join(e.options[:5])} など")
        return

    try:
        operation = int(search_type.get().split(":")[0])
        sort_mode = int(display_order.get().split(":")[0])
        window = int(entry_window.get())
        search_word = entry_target.get().strip()
        if operation == 3:
            search_word = search_word.upper()
        elif operation == 1:
            search_word = search_word.lower()
    except Exception:
        messagebox.showerror("入力エラー", "検索タイプ、表示順、ウィンドウサイズは正しく入力してください。")
        return

    if not search_word:
        messagebox.showerror("入力エラー", "検索対象を入力してください。")
        return

    output_text.delete(1.0, tk.END)
    highlight_color = {'1':'red', '2':'blue', '3':'green'}.get(str(operation), 'red')
    output_text.tag_configure("highlight", foreground=highlight_color, font=("TkDefaultFont", 10, "bold"))

    output = kwic_nltk(text, search_word, operation, window, sort_mode=sort_mode)

    results = output['results']
    next_word_freq = output['next_word_freq']
    next_word_examples = output['next_word_examples']
    next_pos_freq = output['next_pos_freq']
    next_pos_examples = output['next_pos_examples']

    if sort_mode == 1:
        # 順次表示
        for res in results:
            ctx = res['context']
            hi_start = res['highlight_start']
            hi_end = res['highlight_end']
            pre = " ".join(ctx[:hi_start]) + " " if hi_start > 0 else ""
            word = " ".join(ctx[hi_start:hi_end])
            post = " " + " ".join(ctx[hi_end:]) if hi_end < len(ctx) else ""
            output_text.insert(tk.END, pre)
            output_text.insert(tk.END, word, "highlight")
            output_text.insert(tk.END, post + "\n\n")
    elif sort_mode == 2:
        # 次語頻度表示
        for word, count in next_word_freq.most_common():
            output_text.insert(tk.END, f"{search_word} {' '.join(word)}: {count}\n", "highlight")
            for example in next_word_examples[word]:
                output_text.insert(tk.END, "  " + " ".join(example) + "\n")
            output_text.insert(tk.END, "\n")
    elif sort_mode == 3:
        # 次品詞頻度表示
        for pos, count in next_pos_freq.most_common():
            pos_str = " ".join(pos)
            output_text.insert(tk.END, f"{search_word} <{pos_str}>: {count}\n", "highlight")
            for example in next_pos_examples[pos]:
                output_text.insert(tk.END, "  " + " ".join(example) + "\n")
            output_text.insert(tk.END, "\n")

# GUIセットアップ
root = tk.Tk()
root.title("KWIC検索アプリ")

frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky="ew")

ttk.Label(frame, text="興味のあるテーマ（Wikipedia）:").grid(row=0, column=0, sticky="w")
entry_interest = ttk.Entry(frame, width=50)
entry_interest.grid(row=0, column=1, sticky="ew")

ttk.Label(frame, text="検索タイプ:").grid(row=1, column=0, sticky="w")
search_type = ttk.Combobox(frame, values=[
    "1: 単語(token)",
    "2: 品詞(pos)",
    "3: 固有表現(entity)"
], state="readonly", width=20)
search_type.current(0)
search_type.grid(row=1, column=1, sticky="w")

ttk.Label(frame, text="検索対象:").grid(row=2, column=0, sticky="w")
entry_target = ttk.Entry(frame, width=50)
entry_target.grid(row=2, column=1, sticky="ew")

ttk.Label(frame, text="表示順:").grid(row=3, column=0, sticky="w")
display_order = ttk.Combobox(frame, values=[
    "1: 順次表示(sequential)",
    "2: 次の単語頻度(most freq token)",
    "3: 次の品詞頻度(most freq pos)"
], state="readonly", width=20)
display_order.current(0)
display_order.grid(row=3, column=1, sticky="w")

ttk.Label(frame, text="ウィンドウサイズ:").grid(row=4, column=0, sticky="w")
entry_window = ttk.Entry(frame, width=10)
entry_window.insert(0, "5")
entry_window.grid(row=4, column=1, sticky="w")

btn_run = ttk.Button(frame, text="実行", command=run_kwic)
btn_run.grid(row=5, column=0, columnspan=2, pady=10)

output_text = tk.Text(root, wrap="word", width=80, height=25)
output_text.grid(row=1, column=0, padx=10, pady=10)

root.mainloop()
