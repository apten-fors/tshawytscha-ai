import os
import openai
import gradio as gr

# Set your OpenAI API key here
openai.api_key = os.getenv("OPENAI_API_KEY")

# Core function to get response from OpenAI ChatCompletion
def get_openai_response(user_message, chat_history):
    """
    user_message  -- the latest user message (string)
    chat_history  -- a list of (user_text, bot_text) pairs for the conversation
    """
    # System prompt with a fish-themed style
    system_prompt = {
        "role": "system",
        "content": (
            "You are a wise king salmon named TshaBot. "
            "You dwell in the deep digital ocean of knowledge and provide clear, helpful, and detailed answers. "
            "You enjoy using aquatic or marine references occasionally. "
            "Maintain a friendly, respectful tone, and encourage curiosity. "
            "Feel free to include short fish-themed jokes or puns when appropriate."
        )
    }

    # Convert Gradio's chat_history format to OpenAI's ChatCompletion format
    messages = [system_prompt]
    for user, bot in chat_history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": bot})

    # Append the new user message
    messages.append({"role": "user", "content": user_message})

    # Create a ChatCompletion request using the new API syntax
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        messages=messages
    )

    bot_reply = response.choices[0].message.content
    return bot_reply

def chatbot_interaction(user_message, chat_history):
    bot_reply = get_openai_response(user_message, chat_history)
    chat_history.append((user_message, bot_reply))
    return chat_history

def main():
    # Read custom CSS
    with open("styles.css", "r", encoding="utf-8") as f:
        custom_css = f.read()

    with gr.Blocks(css=custom_css, title="Tshawytscha AI") as demo:
        # Header (centered)
        with gr.Row(elem_id="header-row"):
            gr.Markdown(
                """
                <div class="site-title">
                    <h1>Tshawytscha AI</h1>
                </div>
                """,
                elem_id="site-title-md"
            )

        # Fish image (optional)
        with gr.Row(elem_id="fish-row"):
            # If you have a file fish.png
            fish_image = gr.Image(value="fish.png", elem_id="fish-img", show_label=False)

        # Main chat block
        chat_state = gr.State([])
        with gr.Row(elem_id="chat-row"):
            chatbot = gr.Chatbot(label="Conversation", elem_id="chatbot-area")

        # Input field + button
        with gr.Row(elem_id="input-row"):
            user_input = gr.Textbox(
                placeholder="Ask something...",
                label="Your question",
                lines=1,
                elem_id="user-input"
            )
            submit_btn = gr.Button("Catch the answer", elem_id="submit-btn")

        # Button logic
        submit_btn.click(
            fn=chatbot_interaction,
            inputs=[user_input, chat_state],
            outputs=chatbot
        )
        submit_btn.click(
            fn=lambda: "",
            inputs=None,
            outputs=user_input
        )

    demo.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    main()