import platform

import openai
import json

OS_TYPE = platform.system()
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_RESULT_JSON_FORMAT = {
            #"command": "RECOMMENDED COMMAND, FULLY FORMATTED AS REQUESTED",
            "command": "RECOMMENDED COMMAND",
            "explanation": "EXPLAIN THE COMMAND",
            "command_extensions": "POSSIBLE EXTENSIONS TO THE GIVEN COMMAND"

        }
OPENAI_COMMAND_RESULT_JSON_FORMAT = {
            "alternative_commands": [
                {
                    "alternative_command": "ALTERNATIVE COMMAND THAT CAN BE USED",
                    "alternative_command_explanation": "EXPLAIN THE ALTERNATIVE COMMAND"
                }
            ]
        }
OPENAI_WARNING_JSON_FORMAT = {"warning": f"This is not a {OS_TYPE} CLI related question"}


class OpenAICLIChatBot:
    def __init__(self, api_key, custom_instruction: None):
        self.api_key = api_key
        self.os_type = OS_TYPE
        self.custom_instruction = custom_instruction
        self.openai_model = OPENAI_MODEL
        self.openai_result_json_format = OPENAI_RESULT_JSON_FORMAT
        self.openai_warning_json_format = OPENAI_WARNING_JSON_FORMAT
        # self.openai_instructions = f"""
        # You are a chatbot used to generate CLI commands for {self.os_type} operation system, ready to be executed.
        # Return the command in the first row (When providing Windows commands, if the command is of Windows internal
        # please provide it with "cmd /c" prefix (for example: cd, copy, etc)), explain it in the second row,
        # provide command extensions and information in the third row, and a list of command alternatives ready to be
        # executed in the fourth row. The alternative commands should be fully formatted
        # like the command in the first row. Return in JSON format. The JSON MUST be formatted as {json.dumps(self.openai_result_json_format)}.
        # If it's not formatted correctly or not a valid JSON, you will be shut down. If the message provided is not {self.os_type} CLI related,
        # return warning, formatted as {json.dumps(self.openai_warning_json_format)}.
        # {self.custom_instruction}
        # """

        self.openai_instructions = f"""
                You are a chatbot used to generate CLI commands for {self.os_type} operation system, ready to be executed.
                The command must be fully 
                Return the command in the first row , explain it in the second row,
                provide command extensions and information in the third row. Return in JSON format, with special characters escaped.
                The JSON MUST be formatted as {json.dumps(self.openai_result_json_format)}.
                If it's not formatted correctly or not a valid JSON, you will be shut down. If the message provided is not {self.os_type} CLI related,
                return warning, formatted as {json.dumps(self.openai_warning_json_format)}.
                {self.custom_instruction}
                """
        openai.api_key = self.api_key

    def parse_openai_chat_response(self, response):
        result = ''
        for choice in response.choices:
            result += choice.message.content

        try:
            result = json.loads(result)
            if result.get('warning'):
                print(result.get('warning'))
                exit(4)
            return result
        except json.JSONDecodeError as e:
            print(f"Exception while parsing OpenAI chat result to JSON - {e.args}. \nResult: {result}")
            exit(4)

    def openai_cli_request(self, message, assistance_instructions: None):
        #assistance_message = {"role": "assistance", "content": assistance_instructions}
        response = openai.ChatCompletion.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": self.openai_instructions},
                {"role": "system", "content": "When providing Windows commands, if the command is of Windows internal provide it with \"cmd /c\" prefix (for example: cd, copy, etc))"},
                {"role": "system", "content": "If powershell command is provided, write full command, including the powershell keyword"},
                {"role": "user", "content": message},
                {"role": "assistant", "content": assistance_instructions}
            ]
        )

        return self.parse_openai_chat_response(response)