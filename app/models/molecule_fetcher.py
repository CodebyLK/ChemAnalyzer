import requests

class MoleculeFetcher:
    @staticmethod
    def get_isomers(formula, limit=10):
        """
        Takes a formula, finds matching Compound IDs (CIDs),
        and fetches their common names. Returns a dict: {Name: CID}
        """
        # Step 1: Get the list of CIDs for the formula
        cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastformula/{formula}/cids/JSON"

        try:
            response = requests.get(cid_url, timeout=5)
            if response.status_code != 200:
                return {} # No matches found

            data = response.json()
            cids = data.get('IdentifierList', {}).get('CID', [])

            if not cids:
                return {}

            # Limit to top N results so we don't spam the API or freeze the UI
            top_cids = cids[:limit]

            # Step 2: Get the common names for those specific CIDs
            cid_string = ",".join(map(str, top_cids))
            name_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid_string}/property/Title/JSON"

            name_response = requests.get(name_url, timeout=5)
            if name_response.status_code != 200:
                return {}

            name_data = name_response.json()
            properties = name_data.get('PropertyTable', {}).get('Properties', [])

            # Build a dictionary of Name -> CID
            # e.g., {"Ethanol": 702, "Dimethyl ether": 3226}
            isomer_dict = {prop['Title']: prop['CID'] for prop in properties if 'Title' in prop}

            return isomer_dict

        except Exception as e:
            print(f"PubChem API Error: {e}")
            return {}

    @staticmethod
    def get_3d_structure(cid):
        """
        Fetches the exact 3D SDF text block for a specific Compound ID.
        """
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF?record_type=3d"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.text
            return None
        except Exception:
            return None