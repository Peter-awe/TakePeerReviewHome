import gradio as gr
from ai_peer_review.review import process_paper, generate_meta_review
import os
from pathlib import Path

def run_review(paper_file, models, output_dir, generate_meta):
    # Save uploaded file temporarily
    if not os.path.exists("temp"):
        os.makedirs("temp")
    temp_path = os.path.join("temp", paper_file.name)
    with open(temp_path, "wb") as f:
        f.write(paper_file.read())
    
    # Run review
    reviews = process_paper(
        pdf_path=temp_path,
        models=models.split(",")
    )
    
    # Prepare outputs
    output_files = []
    for model, content in reviews.items():
        filename = f"review_{model}.md"
        with open(filename, "w") as f:
            f.write(content)
        output_files.append(filename)
    
    if generate_meta:
        meta_review, _ = generate_meta_review(reviews)
        with open("meta_review.md", "w") as f:
            f.write(meta_review)
        output_files.append("meta_review.md")
    
    return output_files

# Available models
MODELS = [
    "gpt4-o1",
    "gpt4-o1-mini", 
    "claude-3.7-sonnet",
    "gemini-2.5-pro",
    "deepseek-r1",
    "llama-4-maverick"
]

# Create interface
with gr.Blocks(title="AI Peer Review") as demo:
    gr.Markdown("# AI 论文同行评审系统")
    
    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="上传论文(PDF)")
            model_select = gr.Dropdown(
                label="选择模型",
                choices=MODELS,
                multiselect=True,
                value=MODELS[:3]
            )
            output_dir = gr.Textbox(
                label="输出目录",
                value="./reviews"
            )
            meta_check = gr.Checkbox(
                label="生成综合评审",
                value=True
            )
            submit_btn = gr.Button("开始评审")
        
        with gr.Column():
            output_files = gr.File(
                label="评审结果",
                file_count="multiple"
            )
    
    submit_btn.click(
        fn=run_review,
        inputs=[file_input, model_select, output_dir, meta_check],
        outputs=output_files
    )

if __name__ == "__main__":
    demo.launch()
