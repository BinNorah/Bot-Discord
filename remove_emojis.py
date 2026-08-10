import os
import re
import emoji

cogs_dir = r"c:\Users\Norah\Desktop\bot disc\Bot-Discord\cogs"

for file in os.listdir(cogs_dir):
    if file.endswith('.py') and file != 'reglas.py':
        filepath = os.path.join(cogs_dir, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove the 'emoji="<emoji>"' parameter from SelectOption
        # e.g., emoji="⚙️", -> ""
        content = re.sub(r',\s*emoji="[^"]*"', '', content)
        content = re.sub(r'emoji="[^"]*"\s*,?', '', content)
        
        # Replace remaining emojis with empty strings
        content = emoji.replace_emoji(content, replace='')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
print("Emojis removed successfully.")
