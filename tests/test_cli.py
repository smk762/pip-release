from pathlib import Path

from pip_release.cli import main, parse_edit


def test_parse_edit_reads_title_and_body():
    title, body = parse_edit("title: Atlas 1.2\n\nHello there\n", "old")
    assert title == "Atlas 1.2"
    assert body == "Hello there"


def test_parse_edit_without_title_keeps_the_previous_one():
    title, body = parse_edit("just the post", "kept")
    assert title == "kept"
    assert body == "just the post"


def test_platforms_command_lists_the_dragonhound_accounts(tmp_path, capsys):
    code = main(
        [
            "--config",
            "examples/dragonhound.yaml",
            "--env",
            str(tmp_path / "does-not-exist.env"),
            "--store",
            str(tmp_path / "state.sqlite"),
            "platforms",
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "dragonhound3" in out
    assert "AtlasRealms" in out
    assert "missing X_API_KEY" in out
    assert "disabled" in out


def test_drafts_on_an_empty_store(tmp_path, capsys):
    config = tmp_path / "config.json"
    config.write_text(
        '{"pypi":{"projects":["demo"]},"destinations":{"patreon":{"enabled":true}}}',
        encoding="utf-8",
    )
    code = main(
        ["--config", str(config), "--env", str(tmp_path / "no.env"), "--store", str(tmp_path / "s.sqlite"), "drafts"]
    )
    assert code == 0
    assert "No drafts." in capsys.readouterr().out


def test_init_copies_the_dragonhound_example(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("examples").mkdir()
    Path("examples/dragonhound.yaml").write_text("pypi: {projects: [demo]}\n", encoding="utf-8")
    Path(".env.example").write_text("X_API_KEY=\n", encoding="utf-8")
    code = main(["init", "--example", "dragonhound"])
    assert code == 0
    assert Path("config.yaml").read_text(encoding="utf-8").startswith("pypi:")
    assert Path(".env").is_file()
