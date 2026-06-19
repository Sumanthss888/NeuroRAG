"""
Analytics Service for NeuroRAG Clinical Workstation
"""
from typing import List, Dict
from datetime import datetime

class AnalyticsService:
    """Service to compute clinical workstation usage metrics"""
    
    @staticmethod
    def get_aggregates(sessions: List[Dict]) -> Dict:
        """
        Aggregate session data to produce clean, safe dashboard metrics.
        Never exposes raw user records or internal prompts.
        """
        total_queries = 0
        total_critical = 0
        mode_counts = {"patient": 0, "clinician": 0}
        chapter_counts = {}
        daily_activity = {}
        
        for sess in sessions:
            total_queries += sess.get("query_count", 0)
            total_critical += sess.get("critical_count", 0)
            
            chats = sess.get("chats", [])
            for chat in chats:
                # Mode ratio
                mode = chat.get("mode", "patient").lower()
                if mode in mode_counts:
                    mode_counts[mode] += 1
                else:
                    mode_counts[mode] = 1
                
                # Chapters matched
                citations = chat.get("citations", [])
                for cit in citations:
                    ch_title = cit.get("chapter_title", "Unknown")
                    chapter_counts[ch_title] = chapter_counts.get(ch_title, 0) + 1
                
                # Activity timestamp
                timestamp_str = chat.get("timestamp", "")
                if timestamp_str:
                    try:
                        # Extract date part e.g. from "2026-06-19T20:20:00"
                        if "T" in timestamp_str:
                            date_key = timestamp_str.split("T")[0]
                        else:
                            date_key = timestamp_str.split(" ")[0]
                        daily_activity[date_key] = daily_activity.get(date_key, 0) + 1
                    except Exception:
                        pass
        
        # Sort chapters by matches descending
        top_chapters = sorted(chapter_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_sessions": len(sessions),
            "total_queries": total_queries,
            "total_critical": total_critical,
            "mode_ratios": mode_counts,
            "top_chapters": dict(top_chapters),
            "daily_activity": daily_activity
        }
