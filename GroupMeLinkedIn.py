import requests
import re
import time

BASE_URL = 'https://api.groupme.com/v3'

# Regular expression to match LinkedIn profile URLs
linkedin_regex = re.compile(
    r'https?://(?:[a-z]{2,3}\.)?linkedin\.com/(?:in|pub|company)/[a-zA-Z0-9\-_%]+/?',
    re.IGNORECASE
)

def print_instructions():
    """
    Print instructions for obtaining GroupMe API key.
    """
    print("\n🔑 How to Get Your GroupMe API Key:")
    print("1. Go to https://dev.groupme.com/")
    print("2. Log in with your GroupMe account.")
    print("3. Click on 'Developers' > 'Access Tokens'.")
    print("4. Copy your API key and paste it here when prompted.\n")

def get_api_key():
    """
    Prompt user to enter their API key.
    """
    return input("Enter your GroupMe API key: ").strip()

def list_groups(access_token):
    """
    Fetches and lists all GroupMe groups the user is a part of.
    """
    url = f'{BASE_URL}/groups'
    params = {
        'token': access_token,
        'per_page': 50
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        groups = response.json()['response']
        print("\n📂 Available Groups:")
        for i, group in enumerate(groups):
            print(f"{i + 1}. {group['name']} (ID: {group['id']})")
        return groups
    else:
        print(f"Error fetching groups: {response.status_code}")
        return []

def select_group(groups):
    """
    Prompt user to select a group from the list.
    """
    try:
        choice = int(input("\nSelect a group by number: ")) - 1
        if 0 <= choice < len(groups):
            return groups[choice]['id'], groups[choice]['name']
        else:
            print("❌ Invalid choice. Please try again.")
            return select_group(groups)
    except ValueError:
        print("❌ Please enter a valid number.")
        return select_group(groups)

def fetch_messages(group_id, access_token, before_id=None):
    """
    Fetches messages from a GroupMe group.
    """
    url = f'{BASE_URL}/groups/{group_id}/messages'
    params = {
        'token': access_token,
        'limit': 100,
    }
    if before_id:
        params['before_id'] = before_id

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching messages: {response.status_code}")
        return []

    data = response.json()
    return data.get('response', {}).get('messages', [])

def extract_linkedin_urls(messages):
    """
    Extracts LinkedIn URLs from a list of messages.
    """
    urls = set()
    for message in messages:
        text = str(message.get('text', ''))  # Ensure text is a string
        sender_name = message.get('name', 'Unknown')  # Extract sender's name
        matches = linkedin_regex.findall(text)
        for url in matches:
            urls.add((sender_name, url))  # Store as a tuple (name, url)
    return urls

def main():
    print_instructions()
    access_token = get_api_key()

    print("\n⏳ Fetching your groups...")
    groups = list_groups(access_token)
    if not groups:
        print("❌ No groups found or invalid API key. Exiting.")
        input("\nPress Enter to exit...")
        return

    group_id, group_name = select_group(groups)
    print(f"\n✅ Selected Group: {group_name} (ID: {group_id})")

    all_linkedin_urls = set()
    before_id = None

    while True:
        messages = fetch_messages(group_id, access_token, before_id)
        if not messages:
            break

        linkedin_urls = extract_linkedin_urls(messages)
        all_linkedin_urls.update(linkedin_urls)

        before_id = messages[-1]['id']
        time.sleep(0.5)  # To respect API rate limits

    print("\n🔗 Extracted LinkedIn URLs:")
    if all_linkedin_urls:
        with open("linkedin_urls.txt", "w", encoding="utf-8") as f:
            for name, url in sorted(all_linkedin_urls):
                line = f"Name: {name} - LinkedIn URL: {url}"
                print(line)
                f.write(line + "\n")
        print("\n✅ URLs have been saved to linkedin_urls.txt")
    else:
        print("No LinkedIn URLs found.")

    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()