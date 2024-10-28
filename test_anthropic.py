from tkr_utils.helper_anthropic import AnthropicHelper

def test_anthropic_helper():
    print("\nTesting AnthropicHelper...")

    # Initialize helper
    helper = AnthropicHelper()

    # Define max_tokens for requests
    max_tokens = 1024

    # Test message
    messages = [{"role": "user", "content": "Return exactly this: 'Hello, test successful!'"}]

    print("\n1. Testing basic message:")
    response = helper.send_message(
        messages=messages,
        temperature=0,
        max_tokens=max_tokens
    )
    print(f"Response: {response}\n")

    print("2. Testing JSON message:")
    json_messages = [{
        "role": "user",
        "content": "Return a JSON object with the following structure exactly: {\"status\": \"success\", \"message\": \"test completed\"}"
    }]
    json_response = helper.send_message_json(
        messages=json_messages,
        temperature=0,
        max_tokens=max_tokens
    )
    print(f"JSON Response: {json_response}\n")

    print("3. Testing streaming (should print gradually):")
    stream_messages = [{"role": "user", "content": "Count from 1 to 5 slowly."}]
    helper.stream_response(stream_messages)
    print("\n")

if __name__ == "__main__":
    test_anthropic_helper()
