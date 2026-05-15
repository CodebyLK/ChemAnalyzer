import pyodbc

class DatabaseManager:
    def __init__(self):
        self.conn_str = (
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            r'SERVER=localhost;'
            r'DATABASE=ChemAnalyzerDB;'
            r'Trusted_Connection=yes;'
        )

    def get_connection(self):
        try:
            return pyodbc.connect(self.conn_str)
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def save_compound(self, formula, molar_mass):
        conn = self.get_connection()
        if conn:
            cursor = conn.cursor()
            query = "INSERT INTO Compounds (Formula, MolarMass) VALUES (?, ?)"
            cursor.execute(query, (formula, molar_mass))
            conn.commit()
            conn.close()

    def get_all_compounds(self):
        conn = self.get_connection()
        if conn:
            cursor = conn.cursor()
            # UPDATED: We are now grabbing the CompoundID (row 0) as well!
            query = "SELECT CompoundID, Formula, MolarMass, DateAdded FROM Compounds ORDER BY DateAdded DESC"
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            return rows
        return []

    def delete_compound(self, compound_id):
        """NEW: Deletes a specific compound from the database using its ID."""
        conn = self.get_connection()
        if conn:
            cursor = conn.cursor()
            query = "DELETE FROM Compounds WHERE CompoundID = ?"
            cursor.execute(query, (compound_id,))
            conn.commit()
            conn.close()