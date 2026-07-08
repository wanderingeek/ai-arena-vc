import os
import sys
from concurrent.futures import ThreadPoolExecutor

import gradio as gr
from groq import Groq

MODEL_A = "openai/gpt-oss-120b"
MODEL_B = "llama-3.3-70b-versatile"

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("Error: GROQ_API_KEY environment variable is not set.", file=sys.stderr)
    sys.exit(1)

client = Groq(api_key=api_key)


def get_response(model: str, prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content or ""
    except Exception as exc:  # surface per-model failures without killing the run
        return f"[Error from {model}]\n{exc}"


def compare(prompt: str):
    if not prompt or not prompt.strip():
        return "Please enter a prompt.", "Please enter a prompt."

    with ThreadPoolExecutor(max_workers=2) as pool:
        future_a = pool.submit(get_response, MODEL_A, prompt)
        future_b = pool.submit(get_response, MODEL_B, prompt)
        response_a = future_a.result()
        response_b = future_b.result()

    return response_a, response_b


with gr.Blocks(
    title="AI Arena (Groq)",
    css="""
    :root {
      --body-text-size: 17px;
      --text-md: 17px;
      --text-lg: 19px;
      --text-xl: 22px;
      --text-xxl: 28px;
    }
    .gradio-container { font-size: var(--body-text-size); }
    .gradio-container textarea, .gradio-container input { font-size: 16px; }
    """,
) as demo:
    gr.Markdown("# AI Arena — compare two models on Groq")
    gr.Markdown(
        f"**A:** `{MODEL_A}`  &nbsp;|&nbsp;  **B:** `{MODEL_B}`"
    )

    prompt_box = gr.Textbox(
        label="Your prompt",
        placeholder="Tell me a joke...",
        lines=3,
    )

    with gr.Row():
        submit_btn = gr.Button("Submit", variant="primary")
        clear_btn = gr.Button("Clear")

    with gr.Row():
        out_a = gr.Markdown(
            label=f"Model A: {MODEL_A}",
            max_height=420,
            buttons=["copy"],
        )
        out_b = gr.Markdown(
            label=f"Model B: {MODEL_B}",
            max_height=420,
            buttons=["copy"],
        )

    submit_btn.click(
        fn=compare, inputs=prompt_box, outputs=[out_a, out_b], queue=True
    )
    prompt_box.submit(
        fn=compare, inputs=prompt_box, outputs=[out_a, out_b], queue=True
    )
    clear_btn.click(
        fn=lambda: ("", "", ""),
        inputs=None,
        outputs=[prompt_box, out_a, out_b],
    )

if __name__ == "__main__":
    demo.queue()
    demo.launch()
