"""
Extract Table of Contents from PDF
"""
import json
import re
from typing import List, Dict, Optional
from pathlib import Path
import PyPDF2
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class TOCExtractor:
    """Extract and parse Table of Contents from neurological disorders handbook"""
    
    def __init__(self, pdf_path: Path = None):
        self.pdf_path = pdf_path or Config.PDF_PATH
        self.toc_data = {
            "book_title": "Neurological Disorders Handbook",
            "total_chapters": 51,
            "pdf_offset": 2,
            "chapters": []
        }
    
    def extract_toc(self) -> Dict:
        """
        Extract TOC from the provided PDF
        
        Returns:
            Dictionary containing TOC structure
        """
        logger.info(f"Extracting TOC from {self.pdf_path}")
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")
        
        # Hardcoded TOC based on the document you provided
        toc_entries = self._get_hardcoded_toc()
        
        # Parse TOC entries
        for entry in toc_entries:
            chapter = self._parse_toc_entry(entry)
            if chapter:
                self.toc_data["chapters"].append(chapter)
        
        logger.info(f"Extracted {len(self.toc_data['chapters'])} chapters")
        
        return self.toc_data
    
    def _get_hardcoded_toc(self) -> List[Dict]:
        """
        Return hardcoded TOC entries based on the provided document
        """
        return [
            {"id": 1, "title": "Headache", "section": "A. Neurological Symptoms", "toc_page": 25, "keywords": ["headache", "migraine", "tension", "pain"]},
            {"id": 2, "title": "Giddiness", "section": "A. Neurological Symptoms", "toc_page": 38, "keywords": ["giddiness", "dizziness", "vertigo", "balance"]},
            {"id": 3, "title": "Memory Problems", "section": "A. Neurological Symptoms", "toc_page": 49, "keywords": ["memory", "amnesia", "forgetfulness", "recall"]},
            {"id": 4, "title": "Convulsions", "section": "A. Neurological Symptoms", "toc_page": 59, "keywords": ["convulsions", "seizures", "epilepsy", "fits"]},
            {"id": 5, "title": "Paralysis", "section": "A. Neurological Symptoms", "toc_page": 66, "keywords": ["paralysis", "weakness", "hemiplegia", "paraplegia"]},
            {"id": 6, "title": "Neuropathic Pain", "section": "A. Neurological Symptoms", "toc_page": 76, "keywords": ["neuropathic", "pain", "neuralgia", "nerve pain"]},
            {"id": 7, "title": "Physical Disabilities In Children", "section": "A. Neurological Symptoms", "toc_page": 79, "keywords": ["physical", "disabilities", "children", "pediatric"]},
            {"id": 8, "title": "Cognitive Disabilities In Children", "section": "A. Neurological Symptoms", "toc_page": 86, "keywords": ["cognitive", "disabilities", "children", "developmental"]},
            {"id": 9, "title": "Behavioural Issues In Children", "section": "A. Neurological Symptoms", "toc_page": 93, "keywords": ["behavioural", "behavior", "children", "pediatric"]},
            
            {"id": 10, "title": "Computed Tomography", "section": "B. Neurological Investigations - Neuroradiology", "toc_page": 105, "keywords": ["CT", "computed tomography", "scan", "imaging"]},
            {"id": 11, "title": "Magnetic Resonance Imaging", "section": "B. Neurological Investigations - Neuroradiology", "toc_page": 111, "keywords": ["MRI", "magnetic resonance", "imaging", "scan"]},
            {"id": 12, "title": "Angiography", "section": "B. Neurological Investigations - Neuroradiology", "toc_page": 117, "keywords": ["angiography", "vessels", "blood vessels", "imaging"]},
            {"id": 13, "title": "Plain X Ray", "section": "B. Neurological Investigations - Neuroradiology", "toc_page": 122, "keywords": ["x-ray", "xray", "radiography", "imaging"]},
            {"id": 14, "title": "PET-CT", "section": "B. Neurological Investigations - Neuroradiology", "toc_page": 125, "keywords": ["PET", "positron emission", "scan", "imaging"]},
            {"id": 15, "title": "Functional MRI", "section": "B. Neurological Investigations - Neuroradiology", "toc_page": 129, "keywords": ["fMRI", "functional", "MRI", "brain activity"]},
            
            {"id": 16, "title": "Electroencephalography", "section": "B. Neurological Investigations - Electrophysiological", "toc_page": 133, "keywords": ["EEG", "electroencephalography", "brain waves", "electrical"]},
            {"id": 17, "title": "EMG and Nerve Conduction Studies", "section": "B. Neurological Investigations - Electrophysiological", "toc_page": 138, "keywords": ["EMG", "electromyography", "nerve conduction", "NCS"]},
            {"id": 18, "title": "Evoked Potentials", "section": "B. Neurological Investigations - Electrophysiological", "toc_page": 144, "keywords": ["evoked potentials", "EP", "VEP", "BAEP"]},
            
            {"id": 19, "title": "Blood Tests", "section": "B. Neurological Investigations - Biochemical", "toc_page": 149, "keywords": ["blood tests", "laboratory", "serum", "biochemical"]},
            {"id": 20, "title": "Cerebrospinal Fluid", "section": "B. Neurological Investigations - Biochemical", "toc_page": 159, "keywords": ["CSF", "cerebrospinal fluid", "lumbar puncture", "spinal tap"]},
            
            {"id": 21, "title": "Brain Stroke", "section": "C. Neurological Diseases", "toc_page": 167, "keywords": ["stroke", "CVA", "cerebrovascular", "ischemic", "hemorrhagic"]},
            {"id": 22, "title": "Migraine", "section": "C. Neurological Diseases", "toc_page": 178, "keywords": ["migraine", "headache", "aura", "pain"]},
            {"id": 23, "title": "Spondylosis", "section": "C. Neurological Diseases", "toc_page": 183, "keywords": ["spondylosis", "spine", "cervical", "lumbar"]},
            {"id": 24, "title": "Brain Tumors", "section": "C. Neurological Diseases", "toc_page": 189, "keywords": ["tumor", "tumour", "neoplasm", "cancer", "glioma"]},
            {"id": 25, "title": "Head Injury", "section": "C. Neurological Diseases", "toc_page": 193, "keywords": ["head injury", "trauma", "TBI", "concussion"]},
            {"id": 26, "title": "Spine Injury", "section": "C. Neurological Diseases", "toc_page": 199, "keywords": ["spine injury", "spinal cord", "trauma", "SCI"]},
            {"id": 27, "title": "Dementia & Alzheimer's Disease", "section": "C. Neurological Diseases", "toc_page": 206, "keywords": ["dementia", "alzheimer", "memory loss", "cognitive decline"]},
            {"id": 28, "title": "Movement Disorders", "section": "C. Neurological Diseases", "toc_page": 215, "keywords": ["movement disorders", "parkinson", "tremor", "dystonia"]},
            {"id": 29, "title": "Demyelinating Disorders", "section": "C. Neurological Diseases", "toc_page": 224, "keywords": ["demyelinating", "MS", "multiple sclerosis", "myelin"]},
            {"id": 30, "title": "Infections of the CNS", "section": "C. Neurological Diseases", "toc_page": 233, "keywords": ["infection", "meningitis", "encephalitis", "CNS"]},
            {"id": 31, "title": "Neuromuscular Disorders", "section": "C. Neurological Diseases", "toc_page": 245, "keywords": ["neuromuscular", "myasthenia", "muscular dystrophy", "neuropathy"]},
            {"id": 32, "title": "Neurodevelopmental Disorders", "section": "C. Neurological Diseases", "toc_page": 262, "keywords": ["neurodevelopmental", "autism", "ADHD", "cerebral palsy"]},
            
            {"id": 33, "title": "Acute Stroke", "section": "D. Neurological Emergencies", "toc_page": 273, "keywords": ["acute stroke", "emergency", "CVA", "thrombolysis"]},
            {"id": 34, "title": "Delirium", "section": "D. Neurological Emergencies", "toc_page": 275, "keywords": ["delirium", "confusion", "altered mental status", "emergency"]},
            {"id": 35, "title": "Status Epilepticus", "section": "D. Neurological Emergencies", "toc_page": 277, "keywords": ["status epilepticus", "seizure", "emergency", "continuous"]},
            {"id": 36, "title": "Unconsciousness", "section": "D. Neurological Emergencies", "toc_page": 280, "keywords": ["unconsciousness", "coma", "altered consciousness", "emergency"]},
            {"id": 37, "title": "Head Trauma", "section": "D. Neurological Emergencies", "toc_page": 283, "keywords": ["head trauma", "TBI", "injury", "emergency"]},
            {"id": 38, "title": "Spine Trauma", "section": "D. Neurological Emergencies", "toc_page": 288, "keywords": ["spine trauma", "spinal cord injury", "emergency", "SCI"]},
            
            {"id": 39, "title": "Drugs for Seizure Disorders", "section": "E. Neuro Pharmacology", "toc_page": 293, "keywords": ["antiepileptic", "seizure drugs", "AED", "anticonvulsant"]},
            {"id": 40, "title": "Analgesics", "section": "E. Neuro Pharmacology", "toc_page": 318, "keywords": ["analgesics", "pain medication", "opioids", "NSAIDs"]},
            {"id": 41, "title": "Drugs for Migraine", "section": "E. Neuro Pharmacology", "toc_page": 326, "keywords": ["migraine drugs", "triptans", "prophylaxis", "treatment"]},
            {"id": 42, "title": "Drugs for Stroke", "section": "E. Neuro Pharmacology", "toc_page": 331, "keywords": ["stroke drugs", "antiplatelet", "anticoagulant", "thrombolytic"]},
            {"id": 43, "title": "Muscle Relaxants", "section": "E. Neuro Pharmacology", "toc_page": 337, "keywords": ["muscle relaxants", "antispastic", "baclofen", "spasticity"]},
            {"id": 44, "title": "Antiparkinson Drugs", "section": "E. Neuro Pharmacology", "toc_page": 344, "keywords": ["antiparkinson", "levodopa", "dopamine", "parkinsons"]},
            {"id": 45, "title": "Neuroprotective Agents", "section": "E. Neuro Pharmacology", "toc_page": 348, "keywords": ["neuroprotective", "brain protection", "agents", "therapy"]},
            
            {"id": 46, "title": "tPA in Acute Stroke", "section": "F. Modern Developments", "toc_page": 355, "keywords": ["tPA", "thrombolysis", "acute stroke", "treatment"]},
            {"id": 47, "title": "HBOT in Neurological Disorders", "section": "F. Modern Developments", "toc_page": 360, "keywords": ["HBOT", "hyperbaric oxygen", "therapy", "treatment"]},
            {"id": 48, "title": "Comprehensive Neurorehabilitation", "section": "F. Modern Developments", "toc_page": 364, "keywords": ["neurorehabilitation", "rehabilitation", "therapy", "recovery"]},
            {"id": 49, "title": "Recent Advances in Neurosurgery", "section": "F. Modern Developments", "toc_page": 373, "keywords": ["neurosurgery", "surgery", "advances", "treatment"]},
            {"id": 50, "title": "Stem Cell Therapy", "section": "F. Modern Developments", "toc_page": 389, "keywords": ["stem cell", "regenerative", "therapy", "treatment"]},
            {"id": 51, "title": "Interventional Neurology", "section": "F. Modern Developments", "toc_page": 405, "keywords": ["interventional", "endovascular", "neurology", "treatment"]}
        ]
    
    def _parse_toc_entry(self, entry: Dict) -> Optional[Dict]:
        """
        Parse a single TOC entry and create chapter metadata
        
        Args:
            entry: TOC entry dictionary
        
        Returns:
            Parsed chapter dictionary
        """
        try:
            chapter_id = entry["id"]
            title = entry["title"]
            section = entry["section"]
            toc_page = entry["toc_page"]
            keywords = entry["keywords"]
            
            # Calculate actual PDF pages (add offset of 2)
            pdf_page_start = toc_page + Config.PDF_OFFSET
            
            # Estimate end page (next chapter's start - 1, or add ~10 pages)
            pdf_page_end = pdf_page_start + 10  # Default estimate
            
            # Sanitize title for filename
            safe_title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
            safe_title = safe_title.replace(' ', '_').lower()
            
            chapter = {
                "id": chapter_id,
                "title": title,
                "section": section,
                "toc_page": toc_page,
                "pdf_page_start": pdf_page_start,
                "pdf_page_end": pdf_page_end,
                "faiss_path": f"vector_store/chapter_{chapter_id:02d}_{safe_title}/faiss.index",
                "keywords": keywords
            }
            
            return chapter
            
        except Exception as e:
            logger.error(f"Error parsing TOC entry: {e}")
            return None
    
    def save_toc(self, output_path: Path = None):
        """
        Save TOC data to JSON file
        
        Args:
            output_path: Path to save TOC JSON
        """
        output_path = output_path or Config.TOC_MASTER_PATH
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.toc_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"TOC saved to {output_path}")
    
    def load_toc(self, toc_path: Path = None) -> Dict:
        """
        Load TOC from JSON file
        
        Args:
            toc_path: Path to TOC JSON file
        
        Returns:
            TOC dictionary
        """
        toc_path = toc_path or Config.TOC_MASTER_PATH
        
        if not toc_path.exists():
            logger.warning(f"TOC file not found: {toc_path}")
            return None
        
        with open(toc_path, 'r', encoding='utf-8') as f:
            self.toc_data = json.load(f)
        
        logger.info(f"TOC loaded from {toc_path}")
        return self.toc_data