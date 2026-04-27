
from src.security.log_sanitizer import sanitize_log_data


class TestSanitizeString:
    """Test string sanitization."""

    def test_telegram_bot_token_masked(self) -> None:
        text = "My bot token is 123456789:AAFakeFakeFakeFakeFakeFakeFakeFakeFAKE"
        result = sanitize_log_data(text)
        assert "123456789:AAFakeFakeFakeFakeFakeFakeFakeFakeFAKE" not in result
        assert "[REDACTED:telegram_bot_token]" in result

    def test_openai_api_key_masked(self) -> None:
        text = "My API key is sk-1234567890abcdefghijklmnopqrstuvwxyz"
        result = sanitize_log_data(text)
        assert "sk-1234567890abcdefghijklmnopqrstuvwxyz" not in result
        assert "[REDACTED:openai_api_key]" in result

    def test_github_token_masked(self) -> None:
        text = "GitHub token: ghp_1234567890abcdefghijklmnopqrstuvwxyz1234567890"
        result = sanitize_log_data(text)
        assert "ghp_1234567890abcdefghijklmnopqrstuvwxyz1234567890" not in result
        assert "[REDACTED:github_token]" in result

    def test_slack_token_masked(self) -> None:
        text = "Slack token: xoxb-1234567890abcdefghijklmnopqrstuvwxyz"
        result = sanitize_log_data(text)
        assert "xoxb-1234567890abcdefghijklmnopqrstuvwxyz" not in result
        assert "[REDACTED:slack_token]" in result

    def test_bearer_token_masked(self) -> None:
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = sanitize_log_data(text)
        assert "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result
        assert "[REDACTED:bearer_token]" in result

    def test_basic_auth_masked(self) -> None:
        text = "Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ="
        result = sanitize_log_data(text)
        assert "dXNlcm5hbWU6cGFzc3dvcmQ=" not in result
        assert "[REDACTED:basic_auth]" in result

    def test_cookie_masked(self) -> None:
        text = "Cookie: session_id=abc123def456; user_token=xyz789"
        result = sanitize_log_data(text)
        assert "session_id=abc123def456" not in result
        assert "[REDACTED:cookie]" in result

    def test_set_cookie_masked(self) -> None:
        text = "Set-Cookie: auth_token=secret123; Path=/; HttpOnly"
        result = sanitize_log_data(text)
        assert "auth_token=secret123" not in result
        assert "[REDACTED:set_cookie]" in result

    def test_generic_api_key_masked(self) -> None:
        text = "API_KEY=abcdef1234567890abcdef1234567890"
        result = sanitize_log_data(text)
        assert "abcdef1234567890abcdef1234567890" not in result
        assert "[REDACTED:generic_api_key]" in result

    def test_normal_text_unchanged(self) -> None:
        text = "This is a normal message with no secrets"
        result = sanitize_log_data(text)
        assert result == text

    def test_multiple_secrets_all_masked(self) -> None:
        text = "Token: 123456789:AAAAABBBBBBCCCCCCDDDDDDEEEEEE and API key: sk-1234567890abcdefghijklmnop"
        result = sanitize_log_data(text)
        assert "[REDACTED:telegram_bot_token]" in result
        assert "[REDACTED:openai_api_key]" in result
        assert "AAAAABBBBBBCCCCCCDDDDDDEEEEEE" not in result
        assert "sk-1234567890abcdefghijklmnop" not in result


class TestSanitizeDictionary:
    """Test dictionary sanitization."""

    def test_dict_values_sanitized(self) -> None:
        data = {
            "user": "alice",
            "token": "123456789:AAFakeFakeFakeFakeFakeFakeFakeFakeFAKE",
        }
        result = sanitize_log_data(data)
        assert result["user"] == "alice"
        assert "[REDACTED:telegram_bot_token]" in result["token"]
        assert "123456789:AAFakeFakeFakeFakeFakeFakeFakeFakeFAKE" not in result["token"]

    def test_nested_dict_sanitized(self) -> None:
        data = {
            "outer": {
                "inner": {
                    "secret": "sk-1234567890abcdefghijklmnopqrstuvwxyz",
                }
            }
        }
        result = sanitize_log_data(data)
        assert "[REDACTED:openai_api_key]" in result["outer"]["inner"]["secret"]

    def test_dict_keys_preserved(self) -> None:
        data = {
            "Authorization": "Bearer abc.def.ghi",
            "Content-Type": "application/json",
        }
        result = sanitize_log_data(data)
        assert "Authorization" in result
        assert "Content-Type" in result
        assert "[REDACTED:bearer_token]" in result["Authorization"]


class TestSanitizeList:
    """Test list sanitization."""

    def test_list_items_sanitized(self) -> None:
        data = [
            "normal text",
            "123456789:AAFakeFakeFakeFakeFakeFakeFakeFakeFAKE",
            "more normal text",
        ]
        result = sanitize_log_data(data)
        assert result[0] == "normal text"
        assert "[REDACTED:telegram_bot_token]" in result[1]
        assert result[2] == "more normal text"

    def test_nested_list_sanitized(self) -> None:
        data = {
            "items": [
                {"secret": "sk-1234567890abcdefghijklmnopqrstuvwxyz"},
                {"secret": "ghp_1234567890abcdefghijklmnopqrstuvwxyz1234567890"},
            ]
        }
        result = sanitize_log_data(data)
        assert "[REDACTED:openai_api_key]" in result["items"][0]["secret"]
        assert "[REDACTED:github_token]" in result["items"][1]["secret"]


class TestSanitizeMixed:
    """Test complex mixed data structures."""

    def test_complex_structure(self) -> None:
        data = {
            "user_id": 123,
            "messages": [
                {"role": "user", "content": "Hello with token 123456789:AAFakeFakeFakeFakeFakeFakeFakeFakeFAKE"},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "headers": {
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "Content-Type": "application/json",
            }
        }
        result = sanitize_log_data(data)
        assert result["user_id"] == 123
        assert "[REDACTED:telegram_bot_token]" in result["messages"][0]["content"]
        assert "Token" not in result["messages"][0]["content"] or "token" in result["messages"][0]["content"].lower()
        assert result["messages"][1]["content"] == "Hi there!"
        assert "[REDACTED:bearer_token]" in result["headers"]["Authorization"]
        assert result["headers"]["Content-Type"] == "application/json"

    def test_non_string_non_container_types(self) -> None:
        data = {
            "count": 42,
            "ratio": 3.14,
            "active": True,
            "nothing": None,
        }
        result = sanitize_log_data(data)
        assert result["count"] == 42
        assert result["ratio"] == 3.14
        assert result["active"] is True
        assert result["nothing"] is None

    def test_tuple_preserved(self) -> None:
        data = ("normal", "123456789:AAFakeFakeFakeFakeFakeFakeFakeFakeFAKE", "text")
        result = sanitize_log_data(data)
        assert isinstance(result, tuple)
        assert result[0] == "normal"
        assert "[REDACTED:telegram_bot_token]" in result[1]
        assert result[2] == "text"
