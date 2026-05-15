import pytest
from app.controller import ChemController

class TestChemController:
    # Pytest runs this setup function before every single test
    @pytest.fixture(autouse=True)
    def setup(self):
        self.controller = ChemController()

    def test_basic_molar_mass(self):
        """Tests a simple molecule (Water)"""
        # H (1.008 * 2) + O (15.999) = ~18.015
        result = self.controller.process_compound("H2O")

        # We check if the correct math output is inside the returned string
        assert "18.01" in result

    def test_complex_molar_mass(self):
        """Tests recursive parsing with parentheses (Aluminum Sulfate)"""
        # Al2(SO4)3 should be ~342.15 (depending on your exact periodic table weights)
        # Based on your previous screenshot, your app calculates 342.132!
        result = self.controller.process_compound("Al2(SO4)3")

        assert "342.1" in result

    def test_equation_balancer(self):
        """Tests the linear algebra SVD engine"""
        # A classic combustion reaction
        equation = "CH4 + O2 = CO2 + H2O"
        result = self.controller.balance_equation(equation)

        # Updated to match your engine's actual output format:
        # "Balanced: CH4 + 2O2 = CO2 + 2H2O"
        assert "CH4 + 2O2 = CO2 + 2H2O" in result