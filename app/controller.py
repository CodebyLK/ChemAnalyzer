import re
from app.models.molecule_fetcher import MoleculeFetcher
from app.models.db_manager import DatabaseManager
from app.models.periodic_table import PERIODIC_TABLE
from app.models.balancer import EquationBalancer

class ChemController:
    def __init__(self):
        # Initialize our connection to the SQL Server database
        self.db = DatabaseManager()

    # ==========================================
    # COMPOUND ANALYSIS LOGIC
    # ==========================================
    def process_compound(self, formula):
        """
        Parses the formula, calculates real molar mass, and saves to the DB.
        """
        if not formula:
            return "Please enter a formula."

        try:
            # 1. Parse the string using our Recursive algorithm
            parsed_data = self.parse_formula(formula)

            # 2. Calculate the TRUE Molar Mass 
            total_mass = 0.0
            for element, count in parsed_data.items():
                if element in PERIODIC_TABLE:
                    total_mass += PERIODIC_TABLE[element] * count
                else:
                    return f"Error: Unknown or unsupported element '{element}'"

            total_mass = round(total_mass, 3)

            # 3. Save the compound to SQL Server
            self.db.save_compound(formula, total_mass)

            return f"Success! {formula} saved.\nMolar Mass: {total_mass} g/mol"
        except Exception as e:
            return f"Error analyzing compound: {str(e)}"

    # ==========================================
    # EQUATION BALANCING LOGIC
    # ==========================================
    def balance_equation(self, equation_string):
        """
        Splits a chemical equation string and solves it using linear algebra.
        Input: "H2 + O2 = H2O"
        """
        try:
            if '=' not in equation_string:
                return "Error: Use '=' to separate reactants and products."

            left_side, right_side = equation_string.split('=')
            reactants = [r.strip() for r in left_side.split('+') if r.strip()]
            products = [p.strip() for p in right_side.split('+') if p.strip()]

            if not reactants or not products:
                return "Error: Equation must have both reactants and products."

            # Call the Linear Algebra engine
            # We pass 'self.parse_formula' so it can use our recursive parser
            coeffs = EquationBalancer.balance(reactants, products, self.parse_formula)

            # Format the output strings
            r_parts = []
            for i, r in enumerate(reactants):
                coeff = coeffs[i]
                r_parts.append(f"{coeff if coeff > 1 else ''}{r}")

            p_parts = []
            for i, p in enumerate(products):
                coeff = coeffs[i + len(reactants)]
                p_parts.append(f"{coeff if coeff > 1 else ''}{p}")

            return f"Balanced: {' + '.join(r_parts)} = {' + '.join(p_parts)}"

        except Exception as e:
            return f"Error balancing: {str(e)}"

    # ==========================================
    # DATABASE & HISTORY LOGIC
    # ==========================================
    def get_history(self):
        """Fetches all history from the database."""
        return self.db.get_all_compounds()

    def delete_record(self, compound_id):
        """Removes a specific record from the database."""
        self.db.delete_compound(compound_id)

    # ==========================================
    # THE RECURSIVE PARSER (The Brain)
    # ==========================================
    def parse_formula(self, formula):
        """
        A recursive descent parser that handles nested parentheses.
        """
        def parse_group(start_index):
            counts = {}
            i = start_index
            while i < len(formula) and formula[i] != ')':
                if formula[i] == '(':
                    inner_counts, i = parse_group(i + 1)
                    multiplier = 0
                    while i < len(formula) and formula[i].isdigit():
                        multiplier = multiplier * 10 + int(formula[i])
                        i += 1
                    multiplier = multiplier if multiplier > 0 else 1
                    for elem, count in inner_counts.items():
                        counts[elem] = counts.get(elem, 0) + (count * multiplier)
                else:
                    element = formula[i]
                    i += 1
                    while i < len(formula) and formula[i].islower():
                        element += formula[i]
                        i += 1
                    count = 0
                    while i < len(formula) and formula[i].isdigit():
                        count = count * 10 + int(formula[i])
                        i += 1
                    count = count if count > 0 else 1
                    counts[element] = counts.get(element, 0) + count
            if i < len(formula) and formula[i] == ')':
                i += 1
            return counts, i

        final_counts, _ = parse_group(0)
        return final_counts
    def get_isomers(self, formula):
        """Fetches the list of isomers from PubChem."""
        return MoleculeFetcher.get_isomers(formula)

    def get_3d_data(self, cid):
        """Fetches the SDF coordinates from PubChem using the CID."""
        return MoleculeFetcher.get_3d_structure(cid)