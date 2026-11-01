#!/usr/bin/env python3
"""lab-03: LDA 话题建模"""
import json
import os
import re
from collections import Counter, defaultdict

out_dir = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(out_dir, exist_ok=True)

# 模拟文档集：6 个文档，2 个话题（音乐、科技）
documents = [
    "piano music song melody instrument keyboard",
    "guitar music chord song rhythm instrument",
    "computer software algorithm data program",
    "python code software computer program algorithm",
    "music computer digital audio software",
    "song melody code program data"
]

# 简单分词
def tokenize(text):
    return text.lower().split()

# 构建词表
vocab = set()
for doc in documents:
    vocab.update(tokenize(doc))
vocab = sorted(vocab)
vocab_index = {w: i for i, w in enumerate(vocab)}

# LDA 参数
K = 2  # 话题数
alpha = 0.1
beta = 0.1
iterations = 50

# 初始化：随机分配话题
doc_topics = []  # doc_topics[d][w] = topic
for doc in documents:
    words = tokenize(doc)
    doc_topics.append([hash(w) % K for w in words])

# Gibbs 采样（简化版）
for it in range(iterations):
    for d, doc in enumerate(documents):
        words = tokenize(doc)
        for i, word in enumerate(words):
            # 当前话题
            old_topic = doc_topics[d][i]
            
            # 计算话题概率
            topic_probs = []
            for k in range(K):
                # p(topic | doc)
                doc_count = sum(1 for t in doc_topics[d] if t == k)
                p_topic_doc = (doc_count + alpha) / (len(words) + K * alpha)
                
                # p(word | topic)
                word_count = 0
                total_count = 0
                for dd, doc2 in enumerate(documents):
                    for ii, w2 in enumerate(tokenize(doc2)):
                        if doc_topics[dd][ii] == k:
                            total_count += 1
                            if w2 == word:
                                word_count += 1
                p_word_topic = (word_count + beta) / (total_count + len(vocab) * beta)
                
                topic_probs.append(p_topic_doc * p_word_topic)
            
            # 归一化并采样
            total = sum(topic_probs)
            probs = [p / total for p in topic_probs]
            
            # 选择概率最大的话题
            new_topic = max(range(K), key=lambda k: probs[k])
            doc_topics[d][i] = new_topic

# 提取每个话题的 top words
topic_words = defaultdict(list)
for d, doc in enumerate(documents):
    words = tokenize(doc)
    for i, word in enumerate(words):
        topic = doc_topics[d][i]
        topic_words[topic].append(word)

topic_top_words = {}
for k in range(K):
    counter = Counter(topic_words[k])
    topic_top_words[f"topic_{k}"] = [w for w, _ in counter.most_common(5)]

# 文档-话题分布
doc_topic_dist = []
for d, doc in enumerate(documents):
    words = tokenize(doc)
    topic_counts = Counter(doc_topics[d])
    dist = {f"topic_{k}": topic_counts.get(k, 0) / len(words) for k in range(K)}
    doc_topic_dist.append({
        "doc_id": d,
        "doc": doc,
        "topic_distribution": dist
    })

result = {
    "num_topics": K,
    "num_docs": len(documents),
    "vocab_size": len(vocab),
    "iterations": iterations,
    "topic_top_words": topic_top_words,
    "doc_topic_distribution": doc_topic_dist
}

output_file = os.path.join(out_dir, 'lda_topics.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"LDA 话题建模完成：{K} 个话题，{len(documents)} 个文档")
print(f"结果已保存到 {output_file}")
print()
for k in range(K):
    print(f"Topic {k}: {', '.join(topic_top_words[f'topic_{k}'])}")
print()
for d in doc_topic_dist:
    dist = d["topic_distribution"]
    dominant = max(dist, key=dist.get)
    print(f"Doc {d['doc_id']}: {d['doc'][:40]}... → {dominant} ({dist[dominant]:.1%})")
