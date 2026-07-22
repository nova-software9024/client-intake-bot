#!/bin/bash
echo "========================================="
echo "   CLIENT INTAKE BOT - SETUP"
echo "========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 nahi mila. Install karo: pkg install python"
    exit 1
fi

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "Ab config.py edit karo aur apni details daalo:"
echo "  1. BOT_TOKEN - BotFather se token lo"
echo "  2. CHANNEL_LINK - Apne channel ka link"
echo "  3. CHANNEL_ID - Group/Channel ID"
echo "  4. DEVELOPER_NAME - Apna naam"
echo ""
echo "Bot start karne ke liye:"
echo "  python3 bot.py"
echo ""
