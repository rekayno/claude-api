from claude_api import Client
import asyncio
import os


async def main():
  # Initialize the Client
  client = Client(cookie=os.getenv('cookie'))

  # Get organization ID asynchronously
  await client.get_organization_id()

  # Create a new chat
  new_chat = await client.create_new_chat()
  print("New Chat:", new_chat)

  # List all conversations
  conversations = await client.list_all_conversations()
  print("All Conversations:", conversations)

  # Send a message to a conversation
  conversation_id = conversations[0]['uuid'] if conversations else None
  if conversation_id:
    response = await client.send_message("Hello Claude!", conversation_id)
    print("Response:", response)

  # Delete a conversation
  if conversation_id:
    deleted = await client.delete_conversation(conversation_id)
    print("Deleted:", deleted)

  # Get the history of a conversation
  if conversation_id:
    history = await client.chat_conversation_history(conversation_id)
    print("Conversation History:", history)

  # Reset all conversations
  await client.reset_all()

  # Upload an attachment
  attachment_file_path = 'text.txt'
  attachment_response = await client.upload_attachment(attachment_file_path)
  print("Attachment Response:", attachment_response)

  # Rename a chat
  if conversation_id:
    renamed = await client.rename_chat("New Chat Title", conversation_id)
    print("Renamed:", renamed)


# Run the asynchronous main function
asyncio.run(main())
