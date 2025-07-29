# Ideas Testing Lab - Django Practice Project

This Django project serves as a practice playground for testing and implementing creative ideas. Each idea is implemented as a separate Django application.

## Current Projects

### 1. Home Page
- Landing page that showcases all available projects
- Clean, modern interface with Bootstrap styling
- Navigation to different applications

### 2. ChatGPT Chatbot
- Interactive chatbot interface
- Beautiful, responsive design
- Ready for OpenAI ChatGPT integration
- Mock responses included for testing without API key

## Getting Started

1. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install django python-dotenv
   # For ChatGPT functionality:
   pip install openai
   ```

3. **Environment Configuration**
   - The project includes a `.env` file for environment variables
   - By default, it contains development settings
   - Add your OpenAI API key there when ready (see ChatGPT Integration section)

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Visit the Application**
   - Home page: http://127.0.0.1:8000/
   - Chatbot: http://127.0.0.1:8000/chatbot/

## Setting Up ChatGPT Integration

To enable real ChatGPT responses in the chatbot:

1. **Get OpenAI API Key**
   - Visit https://platform.openai.com/api-keys
   - Create a new API key

2. **Install OpenAI Package**
   ```bash
   pip install openai
   ```

3. **Add API Key to Environment**
   Edit the `.env` file in the project root and uncomment/add your API key:
   ```bash
   OPENAI_API_KEY=your-api-key-here
   ```
   
   **Note**: Never commit your API key to version control! The `.env` file is already added to `.gitignore`.

4. **Restart the Server**
   The chatbot will automatically detect the API key and use real ChatGPT responses.

## Project Structure

```
├── manage.py
├── mysite/                 # Main Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── home/                   # Home page application
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── chatbot/                # ChatGPT chatbot application
│   ├── views.py
│   ├── urls.py
│   └── templates/
└── README.md
```

## Adding New Ideas/Projects

To add a new project:

1. **Create New Django App**
   ```bash
   python manage.py startapp your_app_name
   ```

2. **Add to INSTALLED_APPS**
   Add your app to `INSTALLED_APPS` in `mysite/settings.py`

3. **Create Views and Templates**
   Implement your idea in the new app

4. **Update URLs**
   Add URL patterns to include your new app

5. **Update Home Page**
   Add your project to the projects list in `home/views.py`

## Features

- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Bootstrap-based styling with custom CSS
- **Easy Navigation**: Clean navigation between projects
- **Extensible**: Easy to add new projects and ideas
- **Development Ready**: Includes development server and debugging

## Technologies Used

- **Backend**: Django 5.2.4
- **Frontend**: Bootstrap 5.1.3, Font Awesome 6.0.0
- **Database**: SQLite (default)
- **AI Integration**: OpenAI ChatGPT API (optional)

## License

This is a personal practice project. Feel free to use it as inspiration for your own learning projects!
