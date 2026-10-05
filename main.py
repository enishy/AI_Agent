import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
from prompts import system_prompt
from call_function import available_functions, call_function

def main():
    print("Hello from screenreader!")

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    args = parser.parse_args()

    load_dotenv()

    api_key = os.environ.get("OPENROUTER_API_KEY")

    if api_key == None:
        raise RunTimeError("No found api_key")

    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

    messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": args.user_prompt},
]

    for _ in range(20):
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=available_functions,
        )

        message = response.choices[0].message

        # Guardar la respuesta del modelo
        messages.append(message)

        # Si no hay tool calls, tenemos la respuesta final
        if not message.tool_calls:
            print(f"Final response:\n{message.content}")
            return

        # Ejecutar todas las herramientas solicitadas
        for tool_call in message.tool_calls:
            result_message = call_function(
                tool_call,
                verbose=args.verbose,
            )

            if not result_message.get("content"):
                raise Exception("Tool call returned an empty result")

            if args.verbose:
                print(f"-> {result_message['content']}")

            # Guardar el resultado de la herramienta
            messages.append(result_message)

    print("Maximum iterations reached without a final response.")


if __name__ == "__main__":
    main()
