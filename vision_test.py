from utils.vision_llm import ask_vision

answer = ask_vision(
    "extracted_images/Apple_Environmental_Progress_Report_2024/page_69_0.jpeg",
    "Describe this image"
)

print(answer)