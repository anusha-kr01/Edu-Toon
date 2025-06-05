import streamlit as st
import wikipedia
import requests
import openai
from bs4 import BeautifulSoup
from transformers import pipeline
import re
import time
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Set up the app
st.set_page_config(page_title="EduToon", layout="wide")
st.title("📘 EduToon: Learn Concepts Through Comics")
st.write("Type any engineering concept below and get a fun comic-style explanation!")

# Load summarizer model
@st.cache_resource(show_spinner=False)
def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")

summarizer = load_summarizer()

# Wikipedia content extraction functions
def extract_formulas_with_names(concept):
    try:
        page = wikipedia.page(concept, auto_suggest=True)
        html = requests.get(page.url).text
        soup = BeautifulSoup(html, "html.parser")
        formulas = []
        for tag in soup.find_all("math"):
            formula = tag.text.strip()
            if not formula:
                continue
            name = None
            prev = tag.find_previous(string=True)
            if prev:
                prev = prev.strip()
                if len(prev) < 50 and (":" in prev or "law" in prev.lower() or "equation" in prev.lower()):
                    name = prev.replace(":", "").strip()
            if not name:
                prev_tag = tag.find_previous(["b", "strong"])
                if prev_tag and len(prev_tag.text.strip()) < 50:
                    name = prev_tag.text.strip()
            formulas.append((name, formula))
            if len(formulas) >= 5:
                break
        seen = set()
        clean_formulas = []
        for name, formula in formulas:
            if formula not in seen and formula:
                clean_formulas.append((name, formula))
                seen.add(formula)
        return clean_formulas
    except Exception:
        return []

def extract_formula_like_strings(text):
    lines = text.split('\n')
    formula_pattern = re.compile(r'^[A-Za-z0-9_ ()^/\\+\-*\=\.{\}]+=[A-Za-z0-9_ ()^/\\+\-*\=\.{\}]+$')
    formulas = [line.strip() for line in lines if '=' in line and formula_pattern.match(line.strip())]
    return list(set(formulas))

def extract_clean_wiki_text(concept):
    try:
        page = wikipedia.page(concept, auto_suggest=True)
        html = requests.get(page.url).text
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all("math"):
            tag.decompose()
        for tag in soup(['script', 'style', 'table', 'img', 'figure']):
            tag.decompose()
        info = []
        for p in soup.find_all('p'):
            txt = p.get_text().strip()
            if len(txt) > 50:
                info.append(txt)
            if len(info) >= 3:
                break
        return "\n\n".join(info)
    except Exception:
        return ""

# Image generation functions
@st.cache_data(ttl=3600, show_spinner="Generating image...")
def generate_image(prompt, attempt=1):
    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/ultra",
        headers={
            "authorization": "Bearer sk-DA0mKVfYfz23LYCQUI2C1HYvX6xlm17U9MROyN9OzogDA0ZU",
            "accept": "image/*"
        },
        files={"none": ''},
        data={
            "prompt": prompt,
            "output_format": "webp",
        },
    )
    return response

def get_fallback_image(panel_text):
    img = Image.new('RGB', (512, 512), color=(60, 90, 130))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    margin = 20
    offset = 30
    max_width = img.width - 2 * margin

    lines = []
    words = panel_text.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if draw.textlength(test_line, font=font) <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    for line in lines[:12]:
        draw.text((margin, offset), line, font=font, fill=(255, 255, 255))
        offset += 30

    return img

# Text generation functions
openai.api_key = os.getenv("DEEPINFRA_API_KEY") or st.secrets.get("DEEPINFRA_API_KEY", "")
openai.api_base = "https://api.deepinfra.com/v1/openai"

@st.cache_data(ttl=3600, show_spinner="Generating story...")
def generate_comic_story(concept):
    prompt = (
        f"Create a 3-panel fun, creative, and educational comic to explain the concept '{concept}' "
        "to a 12-year-old. Be silly but informative. Each panel should be short and visual.\n\n"
        "Format:\nPanel 1: [description]\nPanel 2: [description]\nPanel 3: [description]"
    )
    try:
        response = openai.ChatCompletion.create(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            messages=[
                {"role": "system", "content": "You're a comic creator for kids, making engineering concepts fun."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message["content"].strip()
    except Exception:
        return (
            "Panel 1: A squirrel discovers Ohm's Law in the forest!\n"
            "Panel 2: He builds a tiny circuit to power his nut vault.\n"
            "Panel 3: Now he's the smartest squirrel in the woods!"
        )

def split_story_to_panels(story):
    panels = []
    for i in range(1, 4):
        match = re.search(rf"Panel {i}:(.*?)(Panel {i+1}:|$)", story, flags=re.S | re.I)
        if match:
            text = match.group(1).strip().replace('\n', ' ')
            if text and len(text) > 6:
                panels.append(text)
    while len(panels) < 3:
        panels.append(f"A fun comic panel about this concept!")
    return panels[:3]

def simplify_panel_text(panel_text):
    clean_text = re.sub(r'Dialogue:.*?$', '', panel_text, flags=re.M)
    clean_text = re.sub(r'Scene:', '', clean_text)
    clean_text = clean_text.strip()
    if not clean_text or len(clean_text) < 10:
        clean_text = f"educational comic panel about science"
    return clean_text[:200]

# Main app UI
concept = st.text_input("Enter a concept (e.g. Ohm's Law, Cache Memory):")

if concept:
    st.write(f"**Concept:** {concept}")
    with st.spinner("Fetching info and generating explanation..."):
        wiki_text = ""
        try:
            wiki_text = wikipedia.summary(concept, sentences=5, auto_suggest=True)
        except wikipedia.exceptions.DisambiguationError as e:
            st.error(f"Too many meanings. Try being more specific. Options: {e.options}")
        except wikipedia.exceptions.PageError:
            search_results = wikipedia.search(concept)
            if search_results:
                try:
                    wiki_text = wikipedia.summary(search_results[0], sentences=5, auto_suggest=True)
                    st.info(f"Showing results for: {search_results[0]}")
                except Exception:
                    st.error("No Wikipedia summary found for this concept.")
            else:
                st.error("No Wikipedia page found for that concept.")
        except Exception as ex:
            st.error(f"Wikipedia error: {ex}")

    if wiki_text:
        summary = summarizer(wiki_text, max_length=120, min_length=50, do_sample=False)
        explanation = summary[0]['summary_text']

        st.markdown("### Explanation (Summary)")
        st.write(explanation)

        formulas = extract_formulas_with_names(concept)
        if not formulas:
            fallback_formulas = extract_formula_like_strings(wiki_text) or extract_formula_like_strings(explanation)
            formulas = [(None, f) for f in fallback_formulas[:5]]

        if formulas:
            st.markdown("### Formulas")
            for name, f in formulas:
                if name:
                    st.markdown(f"**{name}**")
                st.latex(f)
        else:
            st.info("No formulas found for this concept.")

        with st.expander("More Details (From Wikipedia)"):
            clean_info = extract_clean_wiki_text(concept)
            st.write(clean_info if clean_info else wiki_text)

        with st.spinner("Generating comic story and images..."):
            comic_story = generate_comic_story(concept)
            panels = split_story_to_panels(comic_story)
            st.markdown("### Comic Story")
            panel_cols = st.columns(3)

            for idx, panel_text in enumerate(panels):
                with panel_cols[idx]:
                    st.markdown(f"**Panel {idx+1}**")
                    st.write(panel_text)

                    simple_prompt = simplify_panel_text(panel_text)
                    prompt = f"Educational comic panel: {simple_prompt}, cartoon style, colorful, clear illustration"

                    with st.spinner(f"Generating image for Panel {idx+1}..."):
                        time.sleep(1)
                        response = generate_image(prompt)

                        if response.status_code == 200:
                            img_bytes = BytesIO(response.content)
                            img = Image.open(img_bytes)
                            st.image(img, caption=f"Panel {idx+1}", use_container_width=True)
                        else:
                            st.error(f"Error generating image: {response.json()}")
