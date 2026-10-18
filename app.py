import os
import re
from collections import Counter
from flask import Flask, render_template, request

app = Flask(__name__)

STOPWORDS = set([
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'could', 'did',
    'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has', 'have',
    'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in',
    'into', 'is', 'it', 'its', 'itself', 'just', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not',
    'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over',
    'own', 'same', 'she', 'should', 'so', 'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them',
    'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until',
    'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with',
    'would', 'you', 'your', 'yours', 'yourself', 'yourselves'
])

def summarize_text(text, target_ratio=0.3):
    # Sentence splitting
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if len(s.strip()) > 10]
    if len(sentences) <= 3:
        return sentences, len(text.split()), len(text.split()), 0.0

    # Word frequency scoring
    words = re.findall(r'\w+', text.lower())
    filtered_words = [w for w in words if w not in STOPWORDS]
    word_freq = Counter(filtered_words)

    # Score sentences
    sentence_scores = []
    for i, s in enumerate(sentences):
        score = sum(word_freq[w] for w in re.findall(r'\w+', s.lower()) if w in word_freq)
        # Position bias for intro and conclusion
        if i == 0 or i == len(sentences) - 1:
            score *= 1.2
        sentence_scores.append((score, i, s))

    # Select top sentences
    k = max(2, int(len(sentences) * target_ratio))
    top_sentences = sorted(sorted(sentence_scores, reverse=True)[:k], key=lambda x: x[1])
    summary_bullets = [s[2] for s in top_sentences]

    orig_words = len(words)
    sum_words = sum(len(b.split()) for b in summary_bullets)
    compression = round((1 - (sum_words / orig_words)) * 100, 1) if orig_words > 0 else 0

    return summary_bullets, orig_words, sum_words, compression

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.form.get('document_text', '').strip()
    if not text:
        return render_template('index.html')
        
    bullets, orig_count, sum_count, comp = summarize_text(text)
    saved_mins = round((orig_count - sum_count) / 200, 1) # 200 wpm reading speed
    
    return render_template('index.html',
                           summarized=True,
                           bullets=bullets,
                           orig_count=orig_count,
                           sum_count=sum_count,
                           compression=comp,
                           time_saved=saved_mins,
                           input_text=text)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
