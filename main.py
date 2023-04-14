import argparse
import os
import re
import subprocess
import sys

from chatgpt_helper import OpenAICLIChatBot

assistant = ""


def validate_command_execution(command_output):
    user_input_action = input('Did it work? (yes[y]/no[n])').lower()
    if user_input_action == 'y':
        print("Great!")
        return True
    elif user_input_action == 'n':
        return False


def handle_yes(command):
    # if os.name == 'nt':
    #     command = f'cmd /c {command}'
    try:
        sp_result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output = sp_result.stdout
        errors = sp_result.stderr
        #errors = re.sub('[^\x20-\x7E]', '', sp_result.stderr.decode())

        if sp_result.returncode != 0 or errors:
            os.write(1, f"Subprocess returned with exit code {sp_result.returncode} and the following error message: {errors}")
            return f"Subprocess returned with exit code {sp_result.returncode} and the following error message:\n{errors}"
        else:
            os.write(1, output)
            return output
    except Exception as e:
        print(f"Subprocess thrown the Exception {e.args}")
        return f"Subprocess thrown the Exception {e.args}"


def handle_no():
    print("Not executing command")


def handle_flow(openai_cli_chat_bot, user_message):
    global assistant
    while True:
        openai_json_result = openai_cli_chat_bot.openai_cli_request(user_message, assistance_instructions=assistant)
        command = openai_json_result.get("command")
        explanation = openai_json_result.get("explanation")
        command_extensions = openai_json_result.get("command_extensions")
        print(f"You can use the command '{command}'"
              f"\nExplanation: {explanation}"
              f"\nCommand extensions: {command_extensions}")

        user_input_action = input('Execute command? (yes[y]/no[n]/alternatives[a]): ').lower()

        if user_input_action == 'y':
            command_output = handle_yes(command)
        elif user_input_action == 'n':
            handle_no()
            break
        elif user_input_action == 'a':
            #command_output = handle_alternatives(openai_json_result)
            assistant = f"please provide an alternative command to {command}. The alternative command should be outputted in the same way the original command was outputted."

            continue
        else:
            print("invalid response. Not executing command")
            break

        if command_output is None or "":
            print("aaaaa")

        is_command_worked = validate_command_execution(command_output)
        if is_command_worked: exit(4)
        else:
            user_input_action = input('Ask ChatGPT for a fix, or execute alternative? (fix[f]/alternatives[a]/no[n])').lower()
            if user_input_action == 'n':
                handle_no()
            if user_input_action == 'f':
                assistant = f"The command {command} returned the following output: {command_output}"
            elif user_input_action == 'a':
                assistant = f"Please provide an alternative command to {command}. " \
                            f"The alternative command should be outputted in the same way the original command was outputted."


def load_openai_api_key():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        return openai_api_key
    else:
        raise KeyError("OPENAI_API_KEY Environment variable not defined.")

def main():
    parser = argparse.ArgumentParser(description='ChatGPT CLI helper')
    parser.add_argument('user_message', help='CLI help request')
    parser.add_argument('--custom_instructions', help='Custom ChatGPT instructions')

    args = parser.parse_args()
    user_message = args.user_message
    custom_instructions = args.custom_instructions
    
    openai_api_key = load_openai_api_key()
    
    openai_cli_chat_bot = OpenAICLIChatBot(openai_api_key, custom_instructions)
    handle_flow(openai_cli_chat_bot, user_message)


if __name__ == '__main__':
    main()

