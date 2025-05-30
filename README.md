# 📚 EduToon — *Learn Through Laughter*

**Turning complex concepts into captivating comics.**

> Ever wondered if recursion could be explained by a cat stuck in a mirror room? Now it can.

---

## 🎯 What is EduToon?

EduToon is an AI-powered platform that converts tough academic concepts into humorous comic strips. It combines language models, image generation, and layout tools to make learning **fun, visual, and memorable**.

---

## 🌟 Features

- 🧠 NLP-powered concept simplification using GPT  
- 🎬 Storyboarding and comic scripting  
- 🎨 Visual generation via AI tools like Midjourney / Stable Diffusion  
- 🧩 Automatic comic panel layout  
- 💾 Export comics in shareable formats  

---

## 🛠️ Tech Stack

| Component        | Tool/Library                   |
|------------------|-------------------------------|
| UI               | Streamlit                     |
| NLP & Scripting  | OpenAI GPT (via API)          |
| Image Generation | Midjourney / Stable Diffusion |
| Comic Layout     | PIL / Figma / HTML + CSS      |
| Hosting          | Streamlit Cloud / Hugging Face|

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/anusha-kr01/Edu-Toon.git
cd edutoon     # Change this if you rename the folder after cloning
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API keys  
Create a `.env` file in the root directory:
```ini
OPENAI_API_KEY=your_openai_key
STABILITY_API_KEY=your_stable_diffusion_key
DEEPINFRA_API_KEY=your_deepinfra_openai_key
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🧪 Example

**Input:** `"Explain recursion for a 10-year-old"`  
**Output:**  
A 4-panel comic featuring a wizard teaching a confused bunny recursion using magical mirrors!

---


⚠️ Known Issues
Comic image generation may sometimes fail or be slow due to API limits or connectivity issues.
When image generation fails, fallback placeholder images are shown instead.


## 🎯 Roadmap

- [x] Input concept + generate script  
- [x] AI-generated images  
- [ ] Comic layout rendering  
- [ ] Export/share comic  
- [ ] Add character styles/themes  
- [ ] Add user feedback system  
- [ ] Add difficulty level options  

---

## 🤝 Contributing

Contributions welcome!  
Please fork the repo and submit a pull request, or open an issue if you have ideas or feedback.

---

## 📄 License

MIT License — use freely, credit appreciated.

---

## 💬 Connect

**Email:** anushakr719@gmail.com  
