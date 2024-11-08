from src.utils import get_input
from pytest import mark
from unittest.mock import patch
class Testget_input:
    @mark.it("Displays supplied message in the terminal")
    def test_1(self, capfd):
        test_message = "Diamond Sword to Major Steve"
        with patch(f"src.utils.input", return_value="z"):
            get_input(test_message)
            captured = capfd.readouterr().out
        assert captured == test_message + "\n"

    @mark.it("Returns user's input")
    def test_2(self):
        test_message = "Take your speed potion and put your diamond helmet on"
        test_input = "Check your pickaxe, and may Notch love be with you"
        with patch(f"src.utils.input", return_value=test_input):
            result = get_input(test_message)
        assert result == test_input