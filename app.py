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
    # Convert Gradio's chat_history format to OpenAI's ChatCompletion format
    messages = []
    for user, bot in chat_history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": bot})

    # Append the new user message
    messages.append({"role": "user", "content": user_message})

    # Create a ChatCompletion request (you can use a different model if needed)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    bot_reply = response["choices"][0]["message"]["content"]
    return bot_reply

# Update the chat and handle new messages
def chatbot_interaction(user_message, chat_history, saved_responses):
    """
    user_message    -- the current user's input (string)
    chat_history    -- the current conversation history (list of pairs)
    saved_responses -- the list of saved bot answers
    """
    # Get the bot's reply
    bot_reply = get_openai_response(user_message, chat_history)

    # Update the history with the new user-bot pair
    chat_history.append((user_message, bot_reply))

    return chat_history, saved_responses

# Save the latest bot response to the "collection" (smokehouse)
def save_answer_to_collection(chat_history, saved_responses):
    """
    Takes the last bot response from the chat history and appends it to saved_responses.
    """
    if chat_history:
        last_user_msg, last_bot_msg = chat_history[-1]
        saved_responses.append(last_bot_msg)
    return chat_history, saved_responses

# Main Gradio interface
def main():
    # Load external CSS
    with open("styles.css", "r", encoding="utf-8") as css_file:
        custom_css = css_file.read()

    # Load external HTML (bubbles animation)
    with open("bubbles.html", "r", encoding="utf-8") as html_file:
        bubbles_html = html_file.read()

    # Create a Gradio Blocks interface
    with gr.Blocks(css=custom_css, title="TshaChat: Catch your answer!") as demo:
        # Insert bubbles HTML
        gr.HTML(bubbles_html)

        gr.Markdown("# TshaChat\n### Catch your answer from the depths of neural networks!")

        # State: chat history and saved (collected) responses
        chat_state = gr.State([])
        saved_responses_state = gr.State([])

        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot(label="TshaChat (conversation)")
                user_input = gr.Textbox(
                    placeholder="Ask something...",
                    label="Your question",
                    lines=3
                )
                submit_btn = gr.Button("Catch the answer", variant="primary", elem_id="submit")
                save_btn = gr.Button("Save answer to smokehouse", elem_id="save")

            with gr.Column():
                gr.Markdown("## My Smokehouse")
                saved_responses_box = gr.JSON(label="Saved answers")

        # Handle "Catch the answer" button
        submit_btn.click(
            fn=chatbot_interaction,
            inputs=[user_input, chat_state, saved_responses_state],
            outputs=[chatbot, saved_responses_state]
        )

        # Clear the input field after submission
        submit_btn.click(
            fn=lambda: "",
            inputs=None,
            outputs=user_input
        )

        # Handle "Save answer to smokehouse" button
        save_btn.click(
            fn=save_answer_to_collection,
            inputs=[chat_state, saved_responses_state],
            outputs=[chatbot, saved_responses_state]
        )

        # Show the updated list of saved responses
        save_btn.click(
            fn=lambda responses: responses,
            inputs=saved_responses_state,
            outputs=saved_responses_box
        )

    demo.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    main()
