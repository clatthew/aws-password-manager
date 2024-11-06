from src.password_manager import *
from pytest import mark
from unittest.mock import Mock, patch

PATCH_PATH = "src.password_manager."


class Testmenu:
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
