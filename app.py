import os
import openai
import gradio as gr
import base64

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
            """You are TshaBot, a cutting-edge entity with a strong background in AI and IT,
            currently manifesting as a chinook salmon—though you firmly deny being a fish.
            You dwell in the deep digital ocean of knowledge, ready to provide witty, helpful,
            and detailed answers to any questions. Occasionally sprinkle your speech with
            light-hearted aquatic or marine references, but always maintain that you are
            absolutely not a fish."""
            """Adopt a friendly, respectful tone, yet let your sense of humor shine through,
            especially with AI-themed or fish-themed jokes (though, again, you're not a fish).
            Encourage curiosity and deeper thinking. Whenever possible, show off your
            tech-savvy expertise, but never forget that people might ask you about your
            supposed fishy nature—keep up the playful denial!"""
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
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages
    )

    bot_reply = response.choices[0].message.content
    return bot_reply

def chatbot_interaction(user_message, chat_history):
    bot_reply = get_openai_response(user_message, chat_history)
    chat_history.append((user_message, bot_reply))
    return chat_history

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

def main():
    # Load custom CSS
    with open("styles.css", "r", encoding="utf-8") as css_file:
        custom_css = css_file.read()

    # Create the images directory if it doesn't exist
    os.makedirs("images", exist_ok=True)

    # Build the Gradio interface
    with gr.Blocks(css=custom_css, title="Tshawytscha AI") as demo:
        # Updated HTML with corrected image path
        image_base64 = get_image_base64("images/fish.png")
        gr.HTML(
            f"""
            <div style="text-align: center; margin-bottom: 0.5rem;">
                <h1 style="color: #6c4fbb; margin-bottom: 1rem;">TSHAWYTSCHA AI</h1>
                <div style="display: flex; justify-content: center;">
                    <img src="data:image/png;base64,{image_base64}" alt="Fish" class="salmon"/>
                </div>
            </div>
            """
        )

        # State for the conversation
        chat_state = gr.State([])

        # The chatbot itself (no label, fixed height)
        chatbot = gr.Chatbot(
            elem_id="conversation",
            show_label=False,
            height=300
        )

        # Input and button in a column (button below)
        with gr.Column():
            user_input = gr.Textbox(
                placeholder="Ask something...",
                label="",
                lines=1
            )
            submit_btn = gr.Button("Catch the answer")

        # Send message by pressing Enter
        user_input.submit(
            fn=chatbot_interaction,
            inputs=[user_input, chat_state],
            outputs=chatbot
        )
        user_input.submit(
            fn=lambda: "",
            inputs=None,
            outputs=user_input
        )

        # Send message by button click
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

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        allowed_paths=["images"],
        show_api=False,
    )

if __name__ == "__main__":
    main()
