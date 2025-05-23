# CineMatch Chatbot

CineMatch Chatbot is a Flask-based web application designed to recommend personalized movie trailers based on user preferences, such as genres, languages, actors, and mood. It integrates the Gemini API for generating recommendations and the YouTube API to ensure trailer availability, offering an interactive chat interface for a seamless user experience.

## Features
- **Personalized Recommendations**: Receive movie trailer suggestions tailored to your favorite genres, languages, and actors.
- **Interactive Chat Interface**: Engage with the chatbot to specify preferences and refine recommendations.
- **Multi-language Support**: Supports languages like English, Hindi, Spanish, French, Tamil, Telugu, Korean, and Japanese.
- **Mood-Based Suggestions**: Choose a mood (adventurous, relaxed, or intense) to influence recommendations.
- **Trailer Style Options**: Select from short, epic, teaser, or official trailer styles.
- **Rating System**: Rate recommendations to improve future suggestions.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Sai-200516/CineMatch-Chatbot.git
   cd CineMatch-Chatbot
   ```

2. **Set Up a Virtual Environment**:
   Ensure you have Python 3.6 or higher installed.
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install Dependencies**:
   Install the required libraries listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**:
   - Obtain API keys for the [Gemini API](https://makersuite.google.com/app/apikey) and [YouTube Data API](https://console.developers.google.com).
   - Set the keys as environment variables:
     ```bash
     export GEMINI_API_KEY=your_gemini_api_key
     export YOUTUBE_API_KEY=your_youtube_api_key
     ```
     On Windows:
     ```cmd
     set GEMINI_API_KEY=your_gemini_api_key
     set YOUTUBE_API_KEY=your_youtube_api_key
     ```
   - **Note**: Update your `app.py` to use `os.environ.get()` for secure key management (e.g., `GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")`) instead of hardcoding keys.

## Usage
1. **Run the Application**:
   ```bash
   python app.py
   ```

2. **Access the Web Interface**:
   - Open your browser and navigate to `http://localhost:5000`.

3. **Interact with the Chatbot**:
   - Enter your name to start.
   - Specify favorite genres (e.g., action, comedy), languages (e.g., English, Hindi), and actors.
   - Choose a mood (adventurous, relaxed, intense) and trailer style (short, epic, teaser, official).
   - Rate recommendations from 1 to 5 stars to refine future suggestions.
   - Use "start over" to reset the session or freeform search (e.g., "Telugu thriller Prabhas").

## API Keys
The chatbot requires two API keys:
- **Gemini API Key**: Register at [Google Maker Suite](https://makersuite.google.com/app/apikey) to obtain your key for generating recommendations.
- **YouTube API Key**: Create a project in the [Google Developers Console](https://console.developers.google.com) and enable the YouTube Data API to get your key for trailer validation.

Set these as environment variables as shown in the installation steps.

## Libraries Used
The project relies on the following Python libraries, which are included in `requirements.txt`:
- **Flask**: A lightweight web framework for building the application and handling routes, sessions, and templates.
- **requests**: An HTTP library for making API calls to the Gemini and YouTube APIs.

Additional standard libraries used (no installation required):
- `json`: For parsing JSON responses from APIs.
- `os`: For accessing environment variables.
- `re`: For validating YouTube embed URLs with regular expressions.
- `random`: For selecting random genres, languages, or trailer styles.

Install these dependencies with:
```bash
pip install -r requirements.txt
```

## Project Structure
- `app.py`: The main Flask application with chatbot logic and API integrations.
- `index.html`: The front-end template for the chat interface, located in the `templates/` folder.
- `requirements.txt`: Lists external dependencies (Flask and requests).

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Make your changes and commit: `git commit -m "Add your feature"`.
4. Push to your branch: `git push origin feature/your-feature`.
5. Open a pull request.

Ensure your code adheres to the project's style and includes relevant tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.