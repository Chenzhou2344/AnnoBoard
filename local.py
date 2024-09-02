
import gradio as gr
import os

# CSS 样式
css = """
<style>
body, html {
    margin: 0;
    padding: 0;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    background-color: #121212; /* Dark background for the body */
    color: #e0e0e0; /* Light grey text for better readability */
    height: 100%;
    width: 100%;
}

.gallery-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    min-height: 100vh;
    padding: 2rem;
    box-sizing: border-box;
}

.video-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    padding: 1rem;
    width: 100%;
    max-width: 1200px;
}

.video-item {
    padding-top: 0;
    margin-bottom: 1rem;
}

.video-item video {
    width: 800px; /* 固定宽度 */
    height: 500px; /* 固定高度 */
    display: block;
    border-radius: 8px;
    object-fit: cover; /* 保持视频内容的比例，裁剪多余部分 */
}

.video-caption {
    color: #121212; /* Maintain white text for captions */
    padding: 0.5rem;
    border-radius: 4px;
    margin-top: 0.5rem;
    font-size: 0.9rem;
    display: block;
    width: auto;
}

.nav-buttons {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
}

.button {
    background-color: #333333; /* Dark grey button background */
    color: #ffffff; /* White text on buttons for visibility */
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 0.3rem;
    cursor: pointer;
    transition: background 0.2s ease-in-out;
}

.gr-button {
    background-color: #e5e7eb !important;
}

.button:hover {
    background-color: #4f4f4f; /* Lighter grey on hover for visibility */
}

.slider {
    background-color: #333333; /* Slider background */
    border-radius: 0.3rem;
    margin: 1rem 0;
}

.slider input[type="range"] {
    width: 100%;
}

a, a:visited {
    color: #76a9ff; /* Blue accent color for links for visibility */
    text-decoration: none;
}

a:hover {
    color: #a4c2ff; /* Lighter blue on hover for visibility */
}

input[type="text"], select, textarea {
    background-color: #333333; /* Dark grey input background for contrast */
    color: #e0e0e0; /* White text for inputs */
    border: 1px solid #343434; /* Subtle border color */
    border-radius: 0.3rem;
    padding: 0.5rem;
}

input[type="text"]:focus, select:focus, textarea:focus {
    outline: none;
    border-color: #76a9ff; /* Blue border color for focus */
}

/* Additional global styles can go here */

</style>
"""

# JavaScript 脚本
js = """
<script>
function addMotionBackgrounds() {
    // Select all video containers
    var containers = document.querySelectorAll('.video-container');
    
    containers.forEach(container => {
        // Create a div for the background
        var background = document.createElement('div');
        background.className = 'video-background';
        
        // Append the background div to the container
        container.appendChild(background);
    });
}
// Call the function to add motion backgrounds
window.onload = addMotionBackgrounds;
</script>
"""

# 读取 prompt 文件
def load_prompts(prompt_file):
    with open(prompt_file, 'r') as file:
        prompts = [line.strip() for line in file.readlines()]
    return prompts

# 加载 prompts.txt 文件中的所有 prompt
prompts = load_prompts("/home/yons/lsy/data/Prompts4dimensions/color.txt")

def showcase(page_num):
    videos_per_prompt = 3
    models = ['gen2', 'videocrafter2', 'pika', 'show1', 'lavie']
    subdirectory = 'color'
    
    prompt_index = (page_num - 1) // videos_per_prompt
    video_group = (page_num - 1) % videos_per_prompt
    
    video_html = "<div class='gallery-container'>"
    
    prompt_text = prompts[prompt_index]

    for model in models:
        video_name = f"{prompt_text}_{video_group}.mp4"
        video_url = f"http://localhost:8000/data/{model}/{subdirectory}/{video_name}"
        
        # if os.path.exists(os.path.join('data', model, subdirectory, video_name)):
        video_html += f"""
        <div class='video-item'>
            <video controls>
                <source src="{video_url}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <p class='video-caption'>{model}: {prompt_text}</p>
        </div>
        """
    
    video_html += "</div>"
    return video_html

# 项目描述和致谢
description_html = """
<div style="text-align: center; margin-bottom: 20px;">
    <h2>HighlyHumanLike T2V Bench🎥📊</h2>
    <p>
    <p>Thank you for the annotation work you've done which is incredibly helpful to us!!</p>
    <!-- Add more details and acknowledgements as needed -->
</div>
"""

# 页面导航函数
def navigate(direction, current_page):
    if direction == "Beginning":
        return 1
    elif direction == "Previous":
        return max(1, current_page - 1)
    elif direction == "Next":
        return min(total_pages, current_page + 1)
    elif direction == "End":
        return total_pages
    else:
        # For direct navigation through the slider
        return current_page

def navigate_to_page(page_num, page_slider):
    # Directly navigate to the selected page from the slider
    return page_slider, showcase(page_slider)

# 定义总页数
total_prompts = len(prompts)  # 获取 prompt 数量
videos_per_prompt = 3
total_pages = total_prompts * videos_per_prompt

current_page = 1  # 使用普通变量保存当前页码

with gr.Blocks(css=css) as app:
    gr.Markdown(description_html)
    gr.Markdown(js)

    with gr.Row():
        beginning_button = gr.Button("Beginning")
        previous_button = gr.Button("Previous")
        next_button = gr.Button("Next")
        end_button = gr.Button("End")
    page_slider = gr.Slider(minimum=1, maximum=total_pages, step=1, value=1, label="Go to page")
    output_html = gr.HTML()

    def update_output(direction):
        global current_page
        if isinstance(direction, int):
            current_page = direction
        else:
            current_page = navigate(direction, current_page)
        content = showcase(current_page)
        return current_page, content
    
    def initialization():
        global current_page
        current_page = 1
        return current_page, showcase(current_page)

    app.load(fn=initialization, inputs=None, outputs=[page_slider, output_html])
    
    beginning_button.click(fn=lambda: update_output("Beginning"), inputs=None, outputs=[page_slider, output_html])
    previous_button.click(fn=lambda: update_output("Previous"), inputs=None, outputs=[page_slider, output_html])
    next_button.click(fn=lambda: update_output("Next"), inputs=None, outputs=[page_slider, output_html])
    end_button.click(fn=lambda: update_output("End"), inputs=None, outputs=[page_slider, output_html])
    page_slider.change(fn=lambda x: update_output(x), inputs=page_slider, outputs=[page_slider, output_html])

    # 初始化显示第一页内容
    output_html.update(value=showcase(current_page))

app.launch(share=True)
