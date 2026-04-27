# CivicGuide - Election Process Assistant

**Cloud / Live Preview Link**: [(Waiting for User to provide cloud URL link)](https://your-cloud-url-here.com)

CivicGuide is an interactive AI assistant designed to help users understand the election process, voting timelines, registration steps, and their civic duties in a highly accessible and easy-to-follow way.

## 🏛️ Chosen Vertical
**Voter Education and Civic Engagement.**
Navigating the voting process can be confusing, especially for first-time voters or citizens who recently moved. This project specifically tackles voter education, aiming to demystify deadlines, state-specific rules, and the general steps required to participate in elections. By providing an interactive chat interface, it turns a typically static and overwhelming research process into a personalized conversation.

## 🧠 Approach and Logic
We adopted a modular, API-first approach with a clear separation of concerns (Backend vs. Frontend):
1.  **Strict Context Constraints**: The core logic relies on prompting the Gemini model with a strict `SYSTEM_INSTRUCTION` that restricts the AI to non-partisan, process-oriented answers. It actively prevents the assistant from giving political opinions or candidate endorsements.
2.  **Mockable Architecture**: Understanding that API availability might vary during review or local testing, the `gemini_service.py` is written to automatically fallback to an offline "mock mode" if an API key is not present. This ensures the application remains usable and reviewable under any circumstances.
3.  **UI/UX Logic**: The frontend logic prioritizes perceived performance and accessibility. It incorporates real-time typing indicators, markdown parsing for readable responses, and a responsive sidebar structure.

## ⚙️ How the Solution Works
1.  **Frontend Interface**: The user interacts with a premium, accessible web app built with vanilla HTML/CSS/JS. The styling utilizes CSS variables, dark mode toggles, and modern typography to provide a "Rich Aesthetic".
2.  **Request Handling**: When a user submits a question (e.g., "How do I register in NY?"), the JavaScript layer securely sends this text—along with recent conversation history—to the backend Flask API (`/api/chat`).
3.  **Google Services Integration**: The Flask backend constructs a payload using the `google-generativeai` SDK. It passes the user's message, the chat history, and the strict system instructions to the **Google Gemini 1.5 Flash** model.
4.  **Response Delivery**: Gemini processes the natural language, understands the civic context, and generates a clear, step-by-step response. The backend returns this to the frontend, which parses any markdown formatting (like bolding and lists) to render a clean, human-readable message.

## 📝 Assumptions Made
1.  **US-Centric Focus**: While the system prompt is general, many voting nuances requested by users will likely default to the United States election system unless the user specifies another country.
2.  **Browser Support**: We assume users are on modern browsers that support CSS Variables, Flexbox, and `fetch` API.
3.  **Key Protection**: We assume the application will be hosted on a platform (like Google Cloud Run) where environment variables (`GEMINI_API_KEY`, `FLASK_SECRET_KEY`) can be securely injected at runtime.
4.  **Stateful Context**: We assume that maintaining a sliding window of the last 10 messages is sufficient context for Gemini to maintain a coherent conversation thread without exhausting token limits.

## 🛠️ Project Structure
*   `app.py`: Main Flask application.
*   `services/gemini_service.py`: Google Gemini API integration logic.
*   `templates/index.html`: Accessible user interface.
*   `static/css/style.css`: Premium, vanilla CSS styling.
*   `static/js/main.js`: Chat logic and API interactions.
*   `test_app.py`: Unit testing suite.
*   `requirements.txt`: Python dependencies.

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Election-Process-Education
   ```
2. **Set up virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:**
   * Copy `.env.example` to `.env`.
   * Add your Google Gemini API key if you have one. If left blank, the app will run in Demo/Mock mode.
5. **Run the server:**
   ```bash
   python app.py
   ```
6. Open your browser to `http://localhost:5000`.

## ✨ Evaluation Criteria Met
*   **Code Quality**: Clear separation of `templates`, `static`, and `services`. Documented functions.
*   **Security**: API keys are securely managed via Pythons `dotenv` on the backend, never exposed to the client-side JavaScript.
*   **Efficiency**: Minimal dependencies (no oversized frontend frameworks). Context windows are capped at 10 messages to save bandwidth and compute.
*   **Testing**: Includes a unit test file `test_app.py` for automated validation.
*   **Accessibility**: ARIA labels on interactable elements, high-contrast dark/light modes, semantic HTML tags (`<main>`, `<aside>`, `<header>`).
*   **Google Services**: Direct, meaningful integration with Google Gemini for intelligent natural language processing.
