import pyvista as pv
from pyvistaqt import BackgroundPlotter
from PyQt6.QtGui import QIcon
import os

class MoleculeVisualizer:
    # Standard CPK Colors
    COLORS = {
        'H': 'white', 'C': '#222222', 'O': 'red', 'N': 'blue',
        'S': 'yellow', 'P': 'orange', 'Cl': 'green', 'F': 'green',
        'Br': 'darkred', 'I': 'purple', 'Default': 'pink'
    }

    # Relative Van der Waals radii for visual scaling
    RADII = {
        'H': 0.3, 'C': 0.7, 'O': 0.6, 'N': 0.65,
        'S': 1.0, 'P': 1.0, 'Cl': 0.9, 'Default': 0.8
    }

    @staticmethod
    def show_3d(sdf_text, compound_name):
        """Parses the SDF text and launches a PyQt-integrated 3D PyVista window."""
        atoms, bonds = MoleculeVisualizer._parse_sdf(sdf_text)

        if not atoms:
            print("Could not parse SDF geometry.")
            return

        # NEW: Use BackgroundPlotter to embed VTK inside a native PyQt window
        plotter = BackgroundPlotter(title=f"3D Viewer - {compound_name}")

        # Because this is a PyQt window, we can finally apply the icon directly!
        icon_path = os.path.abspath("assets/icon.png")
        if os.path.exists(icon_path):
            plotter.app_window.setWindowIcon(QIcon(icon_path))

        plotter.set_background("#0D1626") # Matches our app's dark theme!

        centers = []

        # 1. Render the Atoms (Spheres)
        for x, y, z, symbol in atoms:
            center = [x, y, z]
            centers.append(center)
            color = MoleculeVisualizer.COLORS.get(symbol, MoleculeVisualizer.COLORS['Default'])
            radius = MoleculeVisualizer.RADII.get(symbol, MoleculeVisualizer.RADII['Default'])

            # Create a high-resolution sphere
            sphere = pv.Sphere(radius=radius, center=center, theta_resolution=40, phi_resolution=40)
            plotter.add_mesh(sphere, color=color, smooth_shading=True, specular=0.5)

        # 2. Render the Bonds (Cylinders/Tubes)
        for a1_idx, a2_idx in bonds:
            c1 = centers[a1_idx]
            c2 = centers[a2_idx]

            # Create a line between the two atoms, then thicken it into a tube
            line = pv.Line(c1, c2)
            tube = line.tube(radius=0.15)
            plotter.add_mesh(tube, color="lightgray", smooth_shading=True, specular=0.3)

        plotter.add_axes()

        # Note: We don't need plotter.show() here because BackgroundPlotter
        # hooks into our PyQt6 app loop and displays automatically!

    @staticmethod
    def _parse_sdf(sdf_text):
        """A lightweight custom parser for V2000 SDF files."""
        lines = sdf_text.strip().split('\n')
        if len(lines) < 4:
            return [], []

        counts = lines[3].split()
        try:
            num_atoms = int(counts[0])
            num_bonds = int(counts[1])
        except (ValueError, IndexError):
            return [], []

        atoms = []
        atom_start = 4
        for i in range(atom_start, atom_start + num_atoms):
            parts = lines[i].split()
            x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
            symbol = parts[3]
            atoms.append((x, y, z, symbol))

        bonds = []
        bond_start = atom_start + num_atoms
        for i in range(bond_start, bond_start + num_bonds):
            parts = lines[i].split()
            a1 = int(parts[0]) - 1
            a2 = int(parts[1]) - 1
            bonds.append((a1, a2))

        return atoms, bonds