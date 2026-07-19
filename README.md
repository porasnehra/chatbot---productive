# AI Virtual Event Manager 🍽️🎉

An AI-powered virtual assistant designed for event management and catering businesses. This system allows business owners to upload their custom "Menu & Policy" PDF documents and provides customers with an intelligent chat interface to ask policy questions and calculate accurate event estimates.

Built using **LangGraph**, **FastAPI**, and **Google Gemini**, the assistant acts as a ReAct Agent, dynamically choosing between querying the business document (RAG) or using a calculator tool to provide accurate pricing.

## 🚀 Features

* **Custom Knowledge Base (RAG):** Upload any PDF (menus, pricing rules, policies). The AI reads it, indexes it, and uses it as the sole source of truth to answer customer queries.
* **Dynamic Math Calculations:** Integrated calculator tool ensures the AI performs precise math (e.g., "150 guests * ₹600 + 18% GST") instead of guessing or hallucinating numbers.
* **Agentic Routing:** Powered by LangGraph, the AI Supervisor dynamically routes between tools and conversational responses based on the user's prompt.
* **Multi-Thread Memory:** The frontend and backend support multiple active conversation threads, retaining chat history without crossing data between different users.
* **Strict Persona:** The AI is locked into a Virtual Manager persona and will politely decline general knowledge or off-topic questions.

## 🛠️ Tech Stack

* **Backend:** FastAPI, Python, Uvicorn
* **Frontend:** Streamlit
* **AI & Orchestration:** LangChain, LangGraph, Google Gemini (3.5-Flash)
* **Embeddings & Vector Store:** Google Generative AI Embeddings, FAISS (Facebook AI Similarity Search)
* **Document Processing:** PyPDF2, LangChain Text Splitters

## 📁 Project Structure

```text
├── main.py              # FastAPI backend containing the LangGraph AI logic
├── app.py               # Streamlit frontend UI
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (API Keys)
└── README.md            # Project documentation

```

## ⚙️ Local Installation & Setup

**1. Clone the repository**

```bash
git clone https://github.com/your-username/ai-event-manager.git
cd ai-event-manager

```

**2. Set up a Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

**3. Install Dependencies**

```bash
pip install -r requirements.txt

```

**4. Configure Environment Variables**
Create a `.env` file in the root directory and add your Google Gemini API key:

```env
GOOGLE_API_KEY=your_google_api_key_here

```

## ▶️ Running the Application

You will need to run the backend and frontend simultaneously in two separate terminal windows.

**Terminal 1: Start the Backend (FastAPI)**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

```

**Terminal 2: Start the Frontend (Streamlit)**

```bash
streamlit run app.py

```

The application will open in your default browser at `http://localhost:8501`.

## ☁️ Deployment Instructions (Render)

This project is optimized for deployment on [Render](https://render.com/).

### Backend Service (FastAPI)

1. Create a new **Web Service** and connect your repository.
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables:** Add `GOOGLE_API_KEY`.
5. Deploy and copy the provided backend URL.

### Frontend Service (Streamlit)

1. Update `app.py` to point to your new Render backend URL instead of `[http://127.0.0.1:8000](http://127.0.0.1:8000)`.
2. Create a second **Web Service**.
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Deploy to get your live frontend link!

## 💡 How to Use

1. Open the web interface.
2. Expand the sidebar and upload your business's Menu & Policy PDF.
3. Click **Process Document**.
4. Start chatting! Ask questions like:
* *"What is the cancellation policy?"*
* *"How much will it cost for a premium dinner for 120 guests with an 18% tax rate?"*



---

*Developed by Poras Nehra*
