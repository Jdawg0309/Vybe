# Vybe Social Network - Flask Application

## Overview
Vybe is a social networking application built with Flask that allows users to connect with friends, send messages, and manage their profiles. The application includes features like user authentication, friend requests, messaging, notifications, and profile customization.

## Features
- **User Authentication:** Secure signup, login, logout, and password management.
- **Profile Management:** Customizable profiles with profile pictures and bios.
- **Friends System:** Send, accept, reject, and remove friends.
- **Messaging:** Real-time messaging with friends, message reactions, and editing.
- **Notifications:** System for friend requests, messages, and other activities.
- **Responsive Design:** Works on various device sizes.

## Installation

### Clone the repository:
```bash
git clone https://github.com/yourusername/vybe-social-network.git
cd vybe-social-network
```

### Set up a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Set up environment variables:
Create a `.env` file in the root directory and add the following variables:
```
DB_USERNAME=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=vybe-db
SECRET_KEY=your_secret_key_here
```

### Database setup:
- Make sure you have MySQL installed and running.
- Create the database specified in your `.env` file.
- The application will create tables automatically on first run.

### Run the application:
```bash
flask run
```

## Project Structure
```
vybe/
├── __init__.py          # Application factory and configuration
├── auth.py              # Authentication routes (login, signup, etc.)
├── friends.py           # Friends management routes
├── messages.py          # Messaging system routes
├── models.py            # Database models
├── notifications.py     # Notifications system
└── profile.py           # Profile management routes
```

## API Endpoints

### Authentication
- `/` - Home page
- `/signup` - User registration
- `/login` - User login
- `/logout` - User logout
- `/forgot_password` - Password recovery
- `/change_password` - Password change
- `/delete_account` - Account deletion

### Profile
- `/profile` - User profile page
- `/upload_profile_picture` - Profile picture upload

### Friends
- `/add_friend` - Send friend request
- `/accept_friend` - Accept friend request
- `/reject_friend` - Reject friend request
- `/remove_friend` - Remove friend

### Messages
- `/messages` - Main messages page
- `/messages/<friend_id>` - Conversation with specific friend
- `/react_to_message/<message_id>` - Add reaction to message
- `/edit_message/<message_id>` - Edit message
- `/delete_message/<message_id>` - Delete message
- `/pin_message/<message_id>` - Pin message

### Notifications
- `/notifications` - View all notifications
- `/mark_as_read/<notification_id>` - Mark notification as read
- `/mark_all_as_read` - Mark all notifications as read

## Database Models
- **User:** Stores user information including credentials and profile details.
- **Friends:** Manages friend relationships between users.
- **Messages:** Stores all messages between users.
- **Notifications:** Tracks system notifications for users.
- **Settings:** Stores user preferences and settings.

## Dependencies
- Flask
- Flask-SQLAlchemy
- Flask-Login
- python-dotenv
- PyMySQL
- Werkzeug

## License
This project is open-source and available under the MIT License.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

