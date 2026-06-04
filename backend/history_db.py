import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class HistoryDB:
    """Simple JSON-based history database for storing document analyses"""
    
    def __init__(self, db_file: str = "analysis_history.json"):
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_db()
    
    def _load_db(self):
        """Load history from JSON file"""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.data = {'analyses': []}
        else:
            self.data = {'analyses': []}
    
    def _save_db(self):
        """Save history to JSON file"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_analysis(self, analysis: Dict) -> Dict:
        """Add new analysis to history"""
        entry = {
            'id': len(self.data['analyses']) + 1,
            'timestamp': datetime.now().isoformat(),
            'document_name': analysis.get('document_name', 'Untitled'),
            'language': analysis.get('language', 'unknown'),
            'clauses_count': len(analysis.get('clauses', [])),
            'obligations_count': len(analysis.get('obligations', [])),
            'entities_count': len(analysis.get('entities', [])),
            'complexity_score': analysis.get('complexity_score', 0),
            'readability_score': analysis.get('readability_score', 0),
            'full_analysis': analysis
        }
        self.data['analyses'].append(entry)
        self._save_db()
        return entry
    
    def get_all_history(self) -> List[Dict]:
        """Get all analyses (without full analysis data for performance)"""
        return [
            {
                'id': a['id'],
                'timestamp': a['timestamp'],
                'document_name': a['document_name'],
                'language': a['language'],
                'clauses_count': a['clauses_count'],
                'obligations_count': a['obligations_count'],
                'entities_count': a['entities_count'],
                'complexity_score': a['complexity_score'],
                'readability_score': a['readability_score']
            }
            for a in sorted(self.data['analyses'], key=lambda x: x['timestamp'], reverse=True)
        ]
    
    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict]:
        """Get full analysis by ID"""
        for analysis in self.data['analyses']:
            if analysis['id'] == analysis_id:
                return analysis['full_analysis']
        return None
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """Delete analysis by ID"""
        original_len = len(self.data['analyses'])
        self.data['analyses'] = [a for a in self.data['analyses'] if a['id'] != analysis_id]
        if len(self.data['analyses']) < original_len:
            self._save_db()
            return True
        return False
    
    def clear_history(self) -> bool:
        """Clear all history"""
        self.data['analyses'] = []
        self._save_db()
        return True
    
    def get_stats(self) -> Dict:
        """Get statistics about analyses"""
        if not self.data['analyses']:
            return {
                'total_analyses': 0,
                'total_clauses': 0,
                'total_obligations': 0,
                'average_complexity': 0,
                'languages': {}
            }
        
        total_clauses = sum(a['clauses_count'] for a in self.data['analyses'])
        total_obligations = sum(a['obligations_count'] for a in self.data['analyses'])
        avg_complexity = sum(a['complexity_score'] for a in self.data['analyses']) / len(self.data['analyses'])
        
        languages = {}
        for a in self.data['analyses']:
            lang = a['language']
            languages[lang] = languages.get(lang, 0) + 1
        
        return {
            'total_analyses': len(self.data['analyses']),
            'total_clauses': total_clauses,
            'total_obligations': total_obligations,
            'average_complexity': round(avg_complexity, 2),
            'languages': languages
        }

# Global instance
history_db = HistoryDB()
