from src.password_manager import *
from pytest import mark
from unittest.mock import patch

PATCH_PATH = "src.password_manager."


class Testmain_loop:
    @mark.it("Calls authentication function when first run")
    def test_1(self):
        with patch(f"{PATCH_PATH}menu", return_value=True):
            with patch(f"{PATCH_PATH}authentication") as mock:
                mock.return_value = True
                main_loop()
                mock.assert_called_once()


class Testmenu:
    @mark.it("Menu function displays correct options message")
    def test_intro_message(self, capfd):
        with patch(f"{PATCH_PATH}input", return_value="x"):
            menu()
        captured = capfd.readouterr()
        expected = (
            "Please specify [e]ntry, [r]etrieval, [d]eletion, [l]isting or e[x]it:"
        )
        result = captured.out[: len(expected)]
        assert result == expected

    @mark.it(
        "Entering invalid input causes next options message to begin with Invalid input."
    )
    def test_invalid(self, capfd):
        with patch(f"{PATCH_PATH}input", return_value="y"):
            menu()
        with patch(f"{PATCH_PATH}input", return_value="x"):
            menu()
        captured = capfd.readouterr()
        std_message = (
            "Please specify [e]ntry, [r]etrieval, [d]eletion, [l]isting or e[x]it:"
        )
        add_message = "Invalid input. "
        expected = add_message + std_message
        result = captured.out[len(std_message) + 1 : len(std_message + expected) + 1]
        assert result == expected

    @mark.it("Entering input e, r, d, l or x calls the respective function:")
    @mark.parametrize(
        "option,func_name",
        [
            ("e", "entry"),
            ("r", "retrieval"),
            ("d", "deletion"),
            ("l", "listing"),
            ("x", "exit"),
        ],
    )
    def test_inputs(self, option, func_name):
        with patch(f"{PATCH_PATH}input", return_value=option):
            with patch(f"{PATCH_PATH}{func_name}") as mock:
                menu()
                mock.assert_called_once()
