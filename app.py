import gradio as gr
import json
import requests
import base64
import time
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

.floating-window {
    position: fixed;
    top: 50%;
    left: 1rem;
    width: 10%;
    padding: 1rem;
    background-color: #333;
    color: #e0e0e0;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    border-radius: 8px;
    z-index: 1000;
    transform: translateY(-50%);

}

.floating-window-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.floating-window-title {
    font-size: 1.25rem;
    font-weight: bold;
    color: #ffffff; 

}


.floating-window-content {
    font-size: 1rem;
    color: #ffffff; 

}

.video-container {
    display: grid;
    grid-template-columns: 1fr;
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
    width: 100%;
    display: block;
    border-radius: 8px;
}

.video-caption {
    color: #00008B; /* Maintain white text for captions */
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
scroll_js = """
<script>
function scrollToHeight(height) {
    body.scrollTo({ top: height, behavior: 'smooth' });
}
</script>
"""

js = """
<script>
function addContentToFloatingWindow(content) {
    const floatingWindowContent = document.getElementById('floatingWindowContent');
    floatingWindowContent.innerHTML = content;
}

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
data_path = "./data4dimensions/Prompts4dimensions/{}.txt"
jsonpath = "./data4dimensions/anno_files/"

subdirectory = "object_class"# 读取 prompt 文件
annokey = "object_class"
models = ['cogvideox5b','gen3', 'kling','videocrafter2', 'pika', 'show1', 'lavie']
dimension4data = {
    "temporal_consistency": "action",
    "aesthetic_quality": "overall_consistency",
    "imaging_quality": "overall_consistency",
    "motion_effects": "action",
    "object_class": "object_class",
    "color": "color",
    "scene": "scene",
    "action": "action",
    "overall_consistency": "overall_consistency"
}

data4dimensions = {
'action': ['temporal_consistency', 'motion_effects','action'],
'object_class': ['object_class'],
'color': ['color'],
'scene': ['scene'],
'color': ['color'],
'overall_consistency': ['aesthetic_quality', 'imaging_quality','overall_consistency']
}

annos = {
    "object_class": """对象类别一致性指的是视频和所提供文本提示之间对象的一致性。关于如何评估这一指标，请考虑以下因素：<br>
                    ● 文本中提到的对象是否正确生成。<br>
                    ● 文本中对象的类别是否可以清晰识别。<br>
                    ● 生成的对象的外观和结构是否符合客观现实和人类主观认知。<br>
                    ● 视频中的运动和变化是否自然流畅。<br>
""",
    "color": """颜色一致性指的是视频与所提供文本提示之间的颜色匹配程度.<br>
                    ● 颜色是否与文本提示一致，并在整个视频中保持一致，没有颜色的突然变化。<br>
                    ● 颜色是否出现在正确的物体或场景上。""",
    "scene": """
              场景一致性考虑:<br>
                1. 文本中提到的场景是否正确生成。<br>
                2. 文本中的场景是否可以清晰识别。<br>
                3. 生成场景的元素的外观和结构是否符合客观现实和人类主观认知。<br>""",
    "action": """动作一致性指的是视频和所提供文本提示之间动作的一致性。考虑：<br>
                        1. 文本中提到的动作是否正确生成。<br>
                        2. 文本中的动作是否可以清晰识别。<br>
                        3. 动作的外观、过程是否符合客观现实和人类主观认知。<br>""",
    "overall_consistency": """总体一致性考虑：<br>
                                ●视频是否展示了文本提示中提到的所有核心元素。（核心元素包括人类、动物、动作、物体、场景、风格、空间关系、数量关系等。）<br>
                                ● 视频的成像质量是否干扰了你对视频的理解。<br>
                              图像质量考虑：<br>
                                清晰度、亮度、噪声、变形、失真等。<br>
                              审美质量考虑：<br>
                                色彩、构图、美感等。<br>
                                """
}
annofile = {}
def load_prompts(prompt_file):
    if prompt_file.startswith('http://') or prompt_file.startswith('https://'):
        response = requests.get(prompt_file)
        response.raise_for_status()  # 确保请求成功
        return response.text.splitlines()  # 返回文本文件的每一行
    with open(prompt_file, 'r') as file:
        prompts = [line.strip() for line in file.readlines()]
    return prompts

def get_prompts(data_path):
    global subdirectory
    prompt_file = data_path.format(subdirectory)
    return load_prompts(prompt_file)


total_pages = len(get_prompts(data_path)) * 3

def check_url_accessible(url):
    try:
        response = requests.get(url)
        # 检查响应状态码是否为200
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException as e:
        # 捕获所有请求异常
        print(f"Error accessing {url}: {e}")
        return False


def video_to_base64(video_path):
    with open(video_path, "rb") as video_file:
        base64_video = base64.b64encode(video_file.read()).decode('utf-8')
    return base64_video

def showcase(page_num):
    global subdirectory

    video_html = []
    videos_per_prompt = 3
    prompts = get_prompts(data_path)
    
    global total_pages
    total_pages = len(prompts) * videos_per_prompt
    
    prompt_index = (page_num - 1) // videos_per_prompt
    video_group = (page_num - 1) % videos_per_prompt
    
    video_html.append(f"""
    <div class="floating-window" id="floatingWindow">
        <div class="floating-window-header">
            <span class="floating-window-title">标注帮助</span>
        </div>
        <div class="floating-window-content" id="floatingWindowContent">
            {annos[annokey]}
        </div>
    </div>
""" )

    prompt_text = prompts[prompt_index]
    

    for model in models:
        video_name = f"{prompt_text}_{video_group}.mp4"
        # video_url = f"http://localhost:8000/data4dimensions/{subdirectory}/{model}/{video_name}"
        video_path = f"./data4dimensions/{subdirectory}/{model}/{video_name}"
        base64_video = video_to_base64(video_path)
        # if os.path.exists(os.path.join('data', model, subdirectory, video_name)):
        # if not check_url_accessible(video_url):
        #     print(f"The URL {video_url} is not accessible.")

        video_html.append(f"""
        <div class='video-container'>
        <div class='video-item'> 
            <video controls>
                <source src="data:video/mp4;base64,{base64_video}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <p class='video-caption'>{model}: {prompt_text}</p>
        </div>
        </div>
        """)

    return video_html


# Description and Acknowledgements    

description_html = """
<div style="text-align: center; margin-bottom: 20px;">
    <h2>HighlyHumanLike T2V Bench🎥📊</h2>
    <p>
    <p>Thank you for the annotation work you've done which is incredibly helpful to us!!</p>
    <!-- Add more details and acknowledgements as needed -->
</div>
"""



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
    page_num.value = page_slider
    return page_num, *showcase(page_num)


# Define the total number of pages.


with gr.Blocks(css=css)  as app:
    gr.Markdown(description_html)
    gr.Markdown(js)
    page_num = gr.State(value=1)
    anno_times = gr.State(value=1)
    group_id = gr.State(value=1)

    videoscores = {}    
    videhtmls = {}

    with gr.Row():
        subdirectory_dropdown = gr.Dropdown(
        choices=['overall_consistency', 'scene', 'object_class','action','color'],
        label="Select dimension",  # 设置默认值
        value=subdirectory
        )
        group_pointer = gr.Dropdown(
        choices=['1', '2', '3'],
        label="Select group",  # 设置默认值
        value='1'
        )

    with gr.Row():
        beginning_button = gr.Button("Beginning")
        previous_button = gr.Button("Previous")
        next_button = gr.Button("Next")
        end_button = gr.Button("End")
        
    page_slider = gr.Slider(minimum=1, maximum=total_pages, step=1, value=1, label="Go to page")
    annotation_help = gr.HTML()
    for model in models:
        videhtmls[model] = gr.HTML()
        with gr.Row():
            for i in range(len(data4dimensions[subdirectory])):
                key = f"{model}_{i}"
                videoscores[key]=gr.Slider(minimum=1, maximum=5, step=1, value=3, label=f"{model} score {data4dimensions[subdirectory][i]}")

    with gr.Row():
        subbmition_button = gr.Button("Submit")
        next_button2 = gr.Button("Next")

    def show_scoresliders():
        sliders = []
        if len(data4dimensions[annokey]) == 1:
            for model in models:
                sliders.append(gr.Slider(minimum=1, maximum=5, step=1, value=3, label=f"{model} score for {data4dimensions[annokey][0]}"))
                sliders.append(gr.Slider(minimum=1, maximum=5, step=1, value=3, visible=False))
                sliders.append(gr.Slider(minimum=1, maximum=5, step=1, value=3, visible=False))
        else:
            for model in models:
                sliders.append(gr.Slider(minimum=1, maximum=5, step=1, value=3, label=f"{model} score for {data4dimensions[annokey][0]}",visible=True))
                sliders.append(gr.Slider(minimum=1, maximum=5, step=1, value=3, label=f"{model} score for {data4dimensions[annokey][1]}",visible=True))
                sliders.append(gr.Slider(minimum=1, maximum=5, step=1, value=3, label=f"{model} score for {data4dimensions[annokey][2]}",visible=True))
        
        return sliders

    def submit(*scores):
        global annofile
        path = f"./data4dimensions/anno_files/{subdirectory}_{group_id.value}.json"

        if len(data4dimensions[annokey]) == 1:        
            for i in range(len(models)):
                model = models[i]
                annofile[annokey][str(page_num.value)][model] = scores[i*len(data4dimensions[subdirectory])]
        else:
            for i in range(len(models)):
                model = models[i]
                for j in range(3):
                    annofile[data4dimensions[annokey][j]][str(page_num.value)][model] = scores[i*len(data4dimensions[subdirectory])+j]

        anno_times.value += 1
        if anno_times.value % 5 == 0:
            with open(path, 'w') as file:
                json.dump(annofile, file,indent=4)
            with open(path, 'r') as file:
                annofile = json.load(file)
            print("Rating Saved",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def update_subdirectory(selected_value):
        global subdirectory, annokey, annofile
        subdirectory = dimension4data[selected_value]
        annokey = selected_value
        page_num.value = 1

        path = f"./anno_files/{subdirectory}_{group_id.value}.json"
        with open(path, 'r') as file:
            annofile = json.load(file)

        return *show_scoresliders(),gr.Slider(minimum=1, maximum=len(get_prompts(data_path))*3, step=1, value=1, label="Go to page"),*showcase(1)

    def update_socre(value):

        return value

    def load_groupfile(selected_value):
        global annofile
        group_id.value = selected_value
        path = f"./data4dimensions/anno_files/{subdirectory}_{group_id.value}.json"
        with open(path, 'r') as file:
            annofile = json.load(file)



    def update_output(direction):
        # new_page_num = navigate(direction, page_num.value)
        if isinstance(direction, int):
            new_page_num = direction
        else:
            new_page_num = navigate(direction, page_num.value)
        page_num.value = new_page_num
        content = showcase(new_page_num)
        return new_page_num, *content
    
    def initialization(start):
        page_num.value = int(start)
        load_groupfile(group_id.value)
        return page_num.value,*showcase(page_num.value)

    app.load(fn=lambda: initialization('1'), inputs=None, outputs=[page_slider, annotation_help, *videhtmls.values()])
    
    # subdirectory_dropdown.change(fn=update_subdirectory, inputs=subdirectory_dropdown, outputs=[*videoscores.values(),page_slider, annotation_help, *videhtmls.values()])
    # group_pointer.change(fn=load_groupfile, inputs=group_pointer, outputs=None)

    beginning_button.click(fn=lambda: update_output("Beginning"), inputs=None, outputs=[page_slider, annotation_help, *videhtmls.values()])
    previous_button.click(fn=lambda: update_output("Previous"), inputs=None, outputs=[page_slider, annotation_help, *videhtmls.values()])
    next_button.click(fn=lambda: update_output("Next"), inputs=None, outputs=[page_slider, annotation_help, *videhtmls.values()])
    end_button.click(fn=lambda: update_output("End"), inputs=None, outputs=[page_slider, annotation_help, *videhtmls.values()])
    page_slider.input(fn=lambda x: update_output(x), inputs=page_slider, outputs=[page_slider, annotation_help, *videhtmls.values()])
    next_button2.click(fn=lambda: update_output("Next"), inputs=None, outputs=[page_slider, annotation_help, *videhtmls.values()])
    
    
    for model in models:
        for i in range(len(data4dimensions[subdirectory])):
            key = f"{model}_{i}"
            videoscores[key].input(fn=update_socre, inputs=videoscores[key], outputs=videoscores[key]) 

    subbmition_button.click(fn=submit, inputs=list(videoscores.values()), outputs=None)

app.launch(share=True) 