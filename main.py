import os
import hashlib
import requests
import spacy
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from collections import deque
from lexicon import LEXICON

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

ORIENTATION_TAGS = {"M/M", "F/F", "M/F", "F/M", "Gen", "Multi", "Other"}

nlp = spacy.load("en_core_web_sm")

context_window = deque(maxlen=10)

def get_cache_path(url):
    filename = hashlib.md5(url.encode()).hexdigest() + ".html"
    return os.path.join(CACHE_DIR, filename)

def fetch_ao3(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    proxies = {"http": "http://127.0.0.1:1087", "https": "http://127.0.0.1:1087"}

    if "view_adult=true" not in url:
        url += "?view_adult=true&view_full_work=true"
    else:
        url += "&view_full_work=true"

    cache_path = get_cache_path(url)

    if os.path.exists(cache_path):
        print("Using cached HTML")
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        print("Fetching from AO3...")
        session = requests.Session()
        retry = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        try:
            print("Trying proxy...")
            res = session.get(url, headers=headers, proxies=proxies, timeout=60)
            html = res.text
        except Exception:
            print("Proxy failed, switching to direct connection...")
            res = session.get(url, headers=headers, timeout=60)
            html = res.text
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(html)
        print("Cached HTML saved")

    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="userstuff")
    text = content.get_text(" ") if content else ""
    all_tags = [t.text for t in soup.find_all("a", class_="tag")]
    relationships = [
        t for t in all_tags
        if "/" in t and "&" not in t and t.strip() not in ORIENTATION_TAGS
    ]
    return text, relationships

def resolve_subject(token_text, charA, charB):
    lower = token_text.lower()
    if token_text in [charA, charB]:
        context_window.append(token_text)
        return token_text
    if lower in ["he", "him", "his"]:
        for item in reversed(context_window):
            if item in [charA, charB]:
                return item
    return None

def extract_main_cp(relationships):
    for tag in relationships:
        tag = tag.strip()
        tag = tag.replace(" / ", "/").replace(" /", "/").replace("/ ", "/")
        if tag in ORIENTATION_TAGS:
            continue
        if "/" in tag and "&" not in tag:
            parts = tag.split("/")
            if len(parts) == 2:
                charA = parts[0].strip()
                charB = parts[1].strip()
                if len(charA) > 0 and len(charB) > 0:
                    return charA, charB
    return None, None

def get_short_name(full_name):
    return full_name.split()[0] if full_name else full_name

def name_in_text(full_name, short_name, text):
    return full_name in text or short_name in text

def analyze(text, charA, charB):
    doc = nlp(text)

    LIGHT_INTIMACY = ["kiss", "hug", "touch"]
    FOREPLAY_HINT = ["moan", "pant", "whimper", "hard", "wet", "aching"]
    EXPLICIT_SEX = ["cock", "dick", "shaft", "penetrate", "thrust", "fuck", "inside", "deep", "stretch"]

    text_lower = text.lower()
    light_flag = any(k in text_lower for k in LIGHT_INTIMACY)
    foreplay_flag = any(k in text_lower for k in FOREPLAY_HINT)
    explicit_flag = any(k in text_lower for k in EXPLICIT_SEX)
    has_sex = explicit_flag or (foreplay_flag and not light_flag)

    score = {charA: 0.0, charB: 0.0}
    shortA = get_short_name(charA)
    shortB = get_short_name(charB)

    role_record = {charA: {"dom": 0, "sub": 0}, charB: {"dom": 0, "sub": 0}}
    switch_count = 0

    for sent in doc.sents:
        sent_text = sent.text.lower().replace(" ", "_")

        for phrase_dict_name in ["PHRASAL_VERBS", "POSITION_PHRASES"]:
            phrase_dict = LEXICON.get(phrase_dict_name, {})
            for phrase, weight in phrase_dict.items():
                if phrase in sent_text:
                    a_present = name_in_text(charA.lower(), shortA.lower(), sent_text)
                    b_present = name_in_text(charB.lower(), shortB.lower(), sent_text)
                    if a_present and not b_present:
                        score[charA] -= weight
                        role_record[charA]["sub"] += 1
                    elif b_present and not a_present:
                        score[charB] -= weight
                        role_record[charB]["sub"] += 1

        for token in sent:
            lemma = token.lemma_.lower().replace(" ", "_")
            subject = None
            voice = None
            obj = None

            for child in token.children:
                if child.dep_ in ["nsubj", "nsubjpass"]:
                    subject = resolve_subject(child.text, charA, charB)
                    voice = "passive" if child.dep_ == "nsubjpass" else "active"
                elif child.dep_ in ["dobj", "pobj"]:
                    obj = resolve_subject(child.text, charA, charB)

            if not subject:
                continue

            for category, word_dict in LEXICON.items():
                if not isinstance(word_dict, dict):
                    continue
                if lemma not in word_dict:
                    continue

                weight = word_dict[lemma]

                if category == "SWITCH_SIGNALS":
                    switch_count += weight
                    continue

                if "DOM" in category:
                    if voice == "active":
                        score[subject] += weight
                        role_record[subject]["dom"] += 1
                        if obj and obj in score:
                            score[obj] -= weight * 0.5
                            role_record[obj]["sub"] += 1
                    elif voice == "passive":
                        score[subject] -= weight
                        role_record[subject]["sub"] += 1

                elif "SUB" in category:
                    if obj and obj in score:
                        score[obj] -= weight
                        role_record[obj]["sub"] += 1
                    else:
                        score[subject] -= weight
                        role_record[subject]["sub"] += 1

                elif "POSITION" in category:
                    if voice == "active":
                        score[subject] += weight * 0.8
                        role_record[subject]["dom"] += 1
                    elif voice == "passive":
                        score[subject] -= weight * 0.8
                        role_record[subject]["sub"] += 1

                if has_sex and category == "INTERACTION_INTENSITY":
                    if obj and obj in score:
                        score[subject] += weight * 2
                        score[obj] -= weight * 2
                        role_record[subject]["dom"] += 2
                        role_record[obj]["sub"] += 2
                    else:
                        if voice == "active":
                            role_record[subject]["dom"] += 2
                        elif voice == "passive":
                            role_record[subject]["sub"] += 2

            if role_record[charA]["dom"] > 0 and role_record[charA]["sub"] > 0:
                switch_count += 1
            if role_record[charB]["dom"] > 0 and role_record[charB]["sub"] > 0:
                switch_count += 1

            for body_part in LEXICON.get("BODY_PARTS", []):
                if body_part in sent_text:
                    score[subject] += 0.1

    total = abs(score[charA]) + abs(score[charB]) + 1e-6
    score[charA] /= total
    score[charB] /= total

    return score, role_record, switch_count, has_sex

def analyze_pipeline(url):
    text, tags = fetch_ao3(url)
    charA, charB = extract_main_cp(tags)

    if not charA or not charB:
        return None

    score, role_record, switch_count, has_explicit = analyze(text, charA, charB)
    delta = abs(score[charA] - score[charB])

    if switch_count >= 5:
        result = "SWITCH likely"
    elif delta < 0.15:
        result = "Uncertain"
    elif score[charA] > score[charB]:
        result = f"{charA} TOP"
    else:
        result = f"{charB} TOP"

    return {
        "charA": charA,
        "charB": charB,
        "score": score,
        "delta": delta,
        "switch": switch_count,
        "result": result,
        "has_explicit": has_explicit,
    }
