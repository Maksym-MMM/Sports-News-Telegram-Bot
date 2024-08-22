# Sports News Telegram Bot

This Telegram bot provides users with the latest sports news across various categories, such as football, MMA, biathlon, basketball, tennis, and hockey. Users can subscribe to specific categories and receive updates directly through the bot. Additionally, the bot includes functionality for admin users to broadcast messages to all subscribers.

## Features

- Subscribe to news updates from specific sports categories.
- Receive news updates with images and links to full articles.
- Admin functionality for broadcasting messages to all users.
- User statistics and settings management.
- Threaded implementation for efficient handling of news scraping and bot functionality.

## Installation Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/Maksym-MMM/Sports-News-Telegram-Bot
   cd Sports-News-Telegram-Bot

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
3. Obtain a Telegram bot token from [BotFather](https://t.me/botfather) and save it in a file named token.txt in the root directory of the project.<br /><br />
4. Initialize the SQLite database by running the bot for the first time:
   ```bash
   python bot.py
# Usage Examples
- Start the Bot: Send the /start command to the bot to initialize your profile and select the news categories you want to subscribe to.
- Select Categories: Use the "Вибрати категорію" button to choose the sports categories you'd like to receive updates for.
- Check Subscribed Categories: Use the "Підключені категорії" button to view your current subscriptions.
- Manage Settings: Use the "Налаштування" button to start or stop receiving news updates.
# Admin Commands
- Broadcast Message: Admins can use the /post_message command to send a message to all users.
- to make your account admin you need to update orders.db and update user_admin to 1
# Acknowledgements

- [Telebot](https://pytba.readthedocs.io/en/latest/install.html) for the Telegram API wrapper.
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) for parsing HTML content.
- [Requests](https://pypi.org/project/requests/) for handling HTTP requests.

Thank you for using the Sports News Telegram Bot!
