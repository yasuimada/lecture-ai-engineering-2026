from types import SimpleNamespace

import app.ask as ask_module


def _mock_client(monkeypatch, response):
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")

    def create_client(*, api_key):
        assert api_key == "test-key"

        def generate_content(*, model, contents):
            assert model == ask_module.MODEL
            assert contents == "質問"
            return response

        return SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))

    monkeypatch.setattr(ask_module.genai, "Client", create_client)


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        text="回答",
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=5),
    )
    _mock_client(monkeypatch, response)

    assert ask_module.ask("質問") == "回答"
    assert capsys.readouterr().out == "[tokens] 入力: 12, 出力: 5\n"


def test_ask_reports_unavailable_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(text="回答", usage_metadata=None)
    _mock_client(monkeypatch, response)

    ask_module.ask("質問")
    assert capsys.readouterr().out == "[tokens] 入力: 不明, 出力: 不明\n"
