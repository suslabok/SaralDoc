import csv
import json
from pathlib import Path
from typing import List, Dict

class DatasetManager:
    """Manage and load datasets for training and testing"""
    
    def __init__(self, data_dir: str = "datasets"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def load_csv_dataset(self, filename: str) -> List[Dict]:
        """Load dataset from CSV file"""
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset not found: {filename}")
        
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
        except Exception as e:
            raise Exception(f"Error loading CSV: {str(e)}")
        
        return data
    
    def load_json_dataset(self, filename: str) -> List[Dict]:
        """Load dataset from JSON file"""
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset not found: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise Exception(f"Error loading JSON: {str(e)}")
        
        return data
    
    def create_sample_dataset(self) -> str:
        """Create a sample Nepali legal dataset"""
        sample_data = [
            {
                "id": 1,
                "title": "Government Employment Contract",
                "text": """यो रोजगार करार सरकारी कर्मचारीको लागि तयार गरिएको हो।

पहिलो खण्ड: कर्तव्य र दायित्व
कर्मचारीको मुख्य कर्तव्य यो हो कि उनी/उनले आफनो सम्पूर्ण कार्य अवधिमा समर्पित भएर काम गरणुपर्दछ।
दोस्रो खण्ड: वेतन र भत्ता
कर्मचारीले महिनामा नियमित वेतनको साथ स्वास्थ्य बीमा र अवकाश सुविधा पाउनु हुनुपर्दछ।
तेस्रो खण्ड: दण्ड र जरिवाना
यदि कर्मचारीले नियम उल्लङ्घन गरे भने उनी/उनलाई कर्मको आधारमा दण्डनीय हुनेछ।
चौथो खण्ड: अवधि र समयसीमा
यो करार दुई वर्षको लागि प्रभावी हुनेछ र त्यसपछि नवीकरण हुन सक्दछ।""",
                "language": "nepali",
                "document_type": "employment_contract"
            },
            {
                "id": 2,
                "title": "Loan Agreement",
                "text": """This loan agreement is entered into between the lender and the borrower.

Section 1: Loan Terms
The lender agrees to provide a loan of Rs. 500,000 to the borrower. The loan shall be repaid within 12 months.

Section 2: Interest Rate
The borrower shall pay interest at 8% per annum on the outstanding loan amount. Interest shall be calculated monthly.

Section 3: Repayment Schedule
The borrower must repay the loan in 12 equal installments. Each installment shall be paid on the 1st of every month.

Section 4: Default and Penalties
If the borrower fails to pay any installment within 30 days of the due date, a penalty of 2% per month shall be imposed.

Section 5: Termination
Either party may terminate this agreement with 60 days written notice.""",
                "language": "english",
                "document_type": "loan_agreement"
            },
            {
                "id": 3,
                "title": "Service Agreement - Mixed",
                "text": """Service Agreement between Company और Client

पहिलो भाग: सेवा विस्तार
The service provider shall provide professional consulting services for a period of 6 months (छ महिना)।

दोस्रो भाग: मूल्य निर्धारण
सेवाको दर Rs. 50,000 प्रति महिना हुनेछ। Payment shall be made within 15 days of invoice।

तेस्रो भाग: दायित्व
Service provider must deliver quality work on time. यदि समय मा काम पूरा नभएमा penalty लगाइनेछ।

चौथो भाग: अनुबन्धको अवधि
The contract duration is 6 months with option to extend. समाप्त हुनु भन्दा पहिले 30 दिनको सूचना दिनु पर्दछ।""",
                "language": "mixed",
                "document_type": "service_agreement"
            }
        ]
        
        # Save as CSV
        csv_file = self.data_dir / "sample_nepali.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
            writer.writeheader()
            writer.writerows(sample_data)
        
        # Also save as JSON
        json_file = self.data_dir / "sample_nepali.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        return str(csv_file)
    
    def get_dataset_info(self) -> Dict:
        """Get information about available datasets"""
        datasets = {
            "csv_files": [],
            "json_files": [],
            "total_documents": 0
        }
        
        for file in self.data_dir.glob("*.csv"):
            try:
                data = self.load_csv_dataset(file.name)
                datasets["csv_files"].append({
                    "name": file.name,
                    "records": len(data)
                })
                datasets["total_documents"] += len(data)
            except:
                pass
        
        for file in self.data_dir.glob("*.json"):
            try:
                data = self.load_json_dataset(file.name)
                datasets["json_files"].append({
                    "name": file.name,
                    "records": len(data)
                })
                datasets["total_documents"] += len(data)
            except:
                pass
        
        return datasets

# Initialize dataset manager
dataset_manager = DatasetManager()
