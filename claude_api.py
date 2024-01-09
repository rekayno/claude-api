import aiohttp
import json
import os
import uuid


class Client:

  def __init__(self, cookie):
    self.cookie = cookie
    self.organization_id = None

  async def get_organization_id(self):
    url = 'https://claude.ai/api/organizations'

    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
      'Accept-Language': 'en-US,en;q=0.5',
      'Referer': 'https://claude.ai/chats',
      'Content-Type': 'application/json',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'Connection': 'keep-alive',
      'Cookie': f'{self.cookie}'
    }

    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
        res = await response.text()
        self.organization_id = json.loads(res)[0]['uuid']

  def get_content_type(self, file_path):
    # Function to determine content type based on file extension
    extension = os.path.splitext(file_path)[-1].lower()
    if extension == '.pdf':
      return 'application/pdf'
    elif extension == '.txt':
      return 'text/plain'
    elif extension == '.csv':
      return 'text/csv'
    # Add more content types as needed for other file types
    else:
      return 'application/octet-stream'

  async def list_all_conversations(self):
    url = f'https://claude.ai/api/organizations/{self.organization_id}/chat_conversations'

    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
      'Accept-Language': 'en-US,en;q=0.5',
      'Referer': 'https://claude.ai/chats',
      'Content-Type': 'application/json',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'Connection': 'keep-alive',
      'Cookie': f'{self.cookie}'
    }

    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
        conversations = await response.text()
        # Returns all conversation information in a list
        return json.loads(conversations)

  async def send_message(self, prompt, conversation_id, attachment=None):
    url = 'https://claude.ai/api/append_message'

    # Upload attachment if provided
    attachments = []
    if attachment:
      attachment_response = await self.upload_attachment(attachment)
      if attachment_response:
        attachments = [attachment_response]
      else:
        return {'Error: Invalid file format. Please try again.'}

    # Ensure attachments is an empty list when no attachment is provided
    if not attachment:
      attachments = []

    payload = json.dumps({
      'completion': {
        'prompt': f'{prompt}',
        'timezone': 'Asia/Kolkata',
        'model': 'claude-2'
      },
      'organization_uuid': f'{self.organization_id}',
      'conversation_uuid': f'{conversation_id}',
      'text': f'{prompt}',
      'attachments': attachments
    })

    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
      'Accept': 'text/event-stream, text/event-stream',
      'Accept-Language': 'en-US,en;q=0.5',
      'Referer': 'https://claude.ai/chats',
      'Content-Type': 'application/json',
      'Origin': 'https://claude.ai',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Cookie': f'{self.cookie}',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'TE': 'trailers'
    }

    async with aiohttp.ClientSession() as session:
      async with session.post(url, headers=headers, data=payload) as response:
        decoded_data = await response.text()
        data = decoded_data.strip().split('\n')[-1]

        answer = {'answer': json.loads(data[6:])['completion']}['answer']

        # Returns answer
        return answer

  async def delete_conversation(self, conversation_id):
    url = f'https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}'

    payload = json.dumps(f'{conversation_id}')
    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
      'Accept-Language': 'en-US,en;q=0.5',
      'Content-Type': 'application/json',
      'Content-Length': '38',
      'Referer': 'https://claude.ai/chats',
      'Origin': 'https://claude.ai',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'Connection': 'keep-alive',
      'Cookie': f'{self.cookie}',
      'TE': 'trailers'
    }

    async with aiohttp.ClientSession() as session:
      async with session.delete(url, headers=headers,
                                data=payload) as response:
        # Returns True if deleted or False if any error in deleting
        if response.status == 204:
          return True
        else:
          return False

  async def chat_conversation_history(self, conversation_id):
    url = f'https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}'

    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
      'Accept-Language': 'en-US,en;q=0.5',
      'Referer': 'https://claude.ai/chats',
      'Content-Type': 'application/json',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'Connection': 'keep-alive',
      'Cookie': f'{self.cookie}'
    }

    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
        # List all the conversations in JSON
        return await response.text()

  def generate_uuid(self):
    random_uuid = uuid.uuid4()
    random_uuid_str = str(random_uuid)
    formatted_uuid = f'{random_uuid_str[0:8]}-{random_uuid_str[9:13]}-{random_uuid_str[14:18]}-{random_uuid_str[19:23]}-{random_uuid_str[24:]}'
    return formatted_uuid

  async def create_new_chat(self):
    url = f'https://claude.ai/api/organizations/{self.organization_id}/chat_conversations'
    uuid = self.generate_uuid()

    payload = json.dumps({'uuid': uuid, 'name': ''})
    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
      'Accept-Language': 'en-US,en;q=0.5',
      'Referer': 'https://claude.ai/chats',
      'Content-Type': 'application/json',
      'Origin': 'https://claude.ai',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Cookie': self.cookie,
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'TE': 'trailers'
    }

    async with aiohttp.ClientSession() as session:
      async with session.post(url, headers=headers, data=payload) as response:
        # Returns JSON of the newly created conversation information
        res = await response.text()
        return json.loads(res)

  async def reset_all(self):
    conversations = await self.list_all_conversations()

    for conversation in conversations:
      conversation_id = conversation['uuid']
      #delete_id = await self.delete_conversation(conversation_id)
      await self.delete_conversation(conversation_id)

    return True

  async def upload_attachment(self, file_path):
    if file_path.endswith('.txt'):
      file_name = os.path.basename(file_path)
      file_size = os.path.getsize(file_path)
      file_type = 'text/plain'
      with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

      return {
        'file_name': file_name,
        'file_type': file_type,
        'file_size': file_size,
        'extracted_content': file_content
      }
    url = 'https://claude.ai/api/convert_document'
    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
      'Accept-Language': 'en-US,en;q=0.5',
      'Referer': 'https://claude.ai/chats',
      'Origin': 'https://claude.ai',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'Connection': 'keep-alive',
      'Cookie': f'{self.cookie}',
      'TE': 'trailers'
    }

    file_name = os.path.basename(file_path)
    content_type = self.get_content_type(file_path)

    files = {
      'file': (file_name, open(file_path, 'rb'), content_type),
      'orgUuid': (None, self.organization_id)
    }

    async with aiohttp.ClientSession() as session:
      async with session.post(url, headers=headers, data=files) as response:
        if response.status == 200:
          return await response.json()
        else:
          return False

  async def rename_chat(self, title, conversation_id):
    url = 'https://claude.ai/api/rename_chat'

    payload = json.dumps({
      'organization_uuid': f'{self.organization_id}',
      'conversation_uuid': f'{conversation_id}',
      'title': f'{title}'
    })
    headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
      'Accept-Language': 'en-US,en;q=0.5',
      'Content-Type': 'application/json',
      'Referer': 'https://claude.ai/chats',
      'Origin': 'https://claude.ai',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'Connection': 'keep-alive',
      'Cookie': f'{self.cookie}',
      'TE': 'trailers'
    }

    async with aiohttp.ClientSession() as session:
      async with session.post(url, headers=headers, data=payload) as response:
        if response.status == 200:
          return True
        else:
          return False
