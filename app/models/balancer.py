import numpy as np
from fractions import Fraction

class EquationBalancer:
    @staticmethod
    def balance(reactants, products, parser_func):
        """
        Takes lists of reactant/product strings and returns integer coefficients.
        Example: reactants=['CH4', 'O2'], products=['CO2', 'H2O']
        """
        # 1. Parse all molecules to find every unique element involved
        all_mols = reactants + products
        parsed_mols = [parser_func(m) for m in all_mols]
        elements = sorted(list(set(el for mol in parsed_mols for el in mol)))

        # 2. Build the Matrix
        # Rows = Elements, Columns = Molecules
        matrix = []
        for el in elements:
            row = []
            for i, mol in enumerate(parsed_mols):
                count = mol.get(el, 0)
                # Products are on the other side of the '=', so they are negative in the matrix
                if i >= len(reactants):
                    count = -count
                row.append(count)
            matrix.append(row)

        A = np.array(matrix, dtype=float)

        # 3. Solve using Singular Value Decomposition (SVD)
        # This finds the 'null space' (the coefficients that balance the atoms)
        u, s, vh = np.linalg.svd(A)
        null_space_vect = vh[-1, :]

        # 4. Convert decimals to the smallest possible whole numbers
        # We normalize by the smallest value and convert to fractions
        null_space_vect = null_space_vect / np.min(np.abs(null_space_vect))
        fractions = [Fraction(x).limit_denominator() for x in null_space_vect]

        # Find the least common multiple of denominators to clear them out
        def lcm(a, b):
            return abs(a * b) // np.gcd(a, b)

        common_denom = 1
        for f in fractions:
            common_denom = lcm(common_denom, f.denominator)

        coeffs = [int(abs(f * common_denom)) for f in fractions]

        return coeffs