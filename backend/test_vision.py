import base64
from app.services.llm_service import llm_service

def test_vision():
    # 1x1 transparent GIF as base64
    mock_image_base64 = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "This is a test of vision capabilities. Please reply with 'Vision Works' if you can read this image."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/gif;base64,{mock_image_base64}"
                    }
                }
            ]
        }
    ]
    
    try:
        response = llm_service.generate(messages=messages)
        print("RESPONSE:", response)
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    test_vision()
