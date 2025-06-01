from tester import Tester
import json

tester = Tester()

def main(tester):
    
    # 1: Login
    print('Login...')
    email = 'john.doe+10@intuitus.ai'
    password = 'Banana123'
    access_token = tester.get_access_token(email, password)
    print(f'Access token: {access_token[:20]}...\n\n')

    # 2: Create chat
    print('Create chat...')
    title = 'New Chat'
    chat = tester.create_chat(title, access_token)
    print(f'Chat:\n{json.dumps(chat, indent=4)}\n\n')

    # 3: Get all chats
    print('Get all chats...')
    chats = tester.get_chats(access_token)
    # print(f'Chats:\n{json.dumps(chats, indent=4)}\n\n')

    # 4: Get specific chat
    if chats and len(chats) > 0:
        print('Get specific chat...')
        chat_id = chats[-1]['id']
        chat = tester.get_chat(chat_id, access_token)
        print(f'Chat:\n{json.dumps(chat, indent=4)}\n\n')

        # 5: Update chat
        print('Update chat...')
        new_title = 'Updated Chat Title'
        updated_chat = tester.update_chat(chat_id, access_token, title=new_title)
        print(f'Updated Chat:\n{json.dumps(updated_chat, indent=4)}\n\n')

        # 6: Delete chat
        print('Delete chat...')
        delete_response = tester.delete_chat(chat_id, access_token)
        print(f'Delete Response:\n{json.dumps(delete_response, indent=4)}\n\n')

        # 7: Verify chat was deleted
        print('Verify chat was deleted...')
        deleted_chat = tester.get_chat(chat_id, access_token)
        print(f'Deleted Chat Response:\n{json.dumps(deleted_chat, indent=4)}\n\n')

main(tester)