"""
Affirmative Action Service
Handles quota management, diversity prioritization, and allocation logic for PM Internship Scheme
"""

import logging
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

class AffirmativeActionService:
    def __init__(self):
        """Initialize affirmative action service with default quotas"""
        # Default quota percentages as per Indian reservation system
        self.quotas = {
            'general': 0.475,      # 47.5% (100% - reserved categories)
            'sc': 0.15,           # 15% for Scheduled Castes
            'st': 0.075,          # 7.5% for Scheduled Tribes  
            'obc': 0.27,          # 27% for Other Backward Classes
            'ews': 0.10,          # 10% for Economically Weaker Sections
        }
        
        # Rural quota (additional consideration)
        self.rural_quota_percentage = 0.30  # 30% preference for rural candidates
        
        # Diversity boost factors
        self.diversity_boost = {
            'rural': 0.05,        # 5% score boost for rural candidates
            'female': 0.03,       # 3% score boost for female candidates
            'pwd': 0.05,          # 5% score boost for persons with disabilities
            'first_generation': 0.04  # 4% boost for first-generation learners
        }
    
    def apply_affirmative_action(self, matches: List[Dict], internships: List[Dict]) -> Dict[str, Any]:
        """
        Apply affirmative action rules to match results and create final allocations
        
        Args:
            matches: List of candidate-internship matches with scores
            internships: List of internship opportunities with capacity info
            
        Returns:
            Dictionary containing allocation results with diversity analysis
        """
        logger.info(f"Applying affirmative action to {len(matches)} matches")
        
        # Group matches by internship
        internship_matches = self._group_matches_by_internship(matches)
        
        # Calculate total capacity and quotas
        total_capacity = sum(internship.get('capacity', 1) for internship in internships)
        quota_slots = self._calculate_quota_slots(total_capacity)
        
        # Apply diversity boosts to scores
        boosted_matches = self._apply_diversity_boosts(matches)
        
        # Perform allocation with quota management
        allocations = self._allocate_with_quotas(
            boosted_matches, 
            internship_matches, 
            quota_slots,
            internships
        )
        
        # Generate diversity report
        diversity_report = self._generate_diversity_report(allocations)
        
        logger.info(f"Allocation completed: {len(allocations['final_allocations'])} candidates allocated")
        
        return {
            'final_allocations': allocations['final_allocations'],
            'quota_fulfillment': allocations['quota_fulfillment'],
            'diversity_report': diversity_report,
            'allocation_summary': allocations['summary'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _group_matches_by_internship(self, matches: List[Dict]) -> Dict[str, List[Dict]]:
        """Group matches by internship ID"""
        internship_matches = defaultdict(list)
        
        for match in matches:
            internship_id = match.get('internship_id')
            if internship_id:
                internship_matches[internship_id].append(match)
        
        # Sort matches within each internship by score (highest first)
        for internship_id in internship_matches:
            internship_matches[internship_id].sort(
                key=lambda x: x.get('score', 0), 
                reverse=True
            )
        
        return dict(internship_matches)
    
    def _calculate_quota_slots(self, total_capacity: int) -> Dict[str, int]:
        """Calculate number of slots for each quota category"""
        quota_slots = {}
        
        for category, percentage in self.quotas.items():
            slots = max(1, int(total_capacity * percentage))
            quota_slots[category] = slots
        
        # Ensure total doesn't exceed capacity
        total_allocated = sum(quota_slots.values())
        if total_allocated > total_capacity:
            # Proportionally reduce slots
            reduction_factor = total_capacity / total_allocated
            for category in quota_slots:
                quota_slots[category] = max(1, int(quota_slots[category] * reduction_factor))
        
        logger.info(f"Quota slots calculated: {quota_slots}")
        return quota_slots
    
    def _apply_diversity_boosts(self, matches: List[Dict]) -> List[Dict]:
        """Apply diversity boost factors to match scores"""
        boosted_matches = []
        
        for match in matches:
            # Get candidate info
            candidate_id = match.get('candidate_id')
            original_score = match.get('score', 0)
            
            # Calculate diversity boost
            boost_factor = 0
            boost_reasons = []
            
            # Check for rural background
            if match.get('rural_background') or self._is_rural_candidate(match):
                boost_factor += self.diversity_boost['rural']
                boost_reasons.append('Rural background')
            
            # Check for gender diversity (if female)
            if self._is_female_candidate(match):
                boost_factor += self.diversity_boost['female']
                boost_reasons.append('Gender diversity')
            
            # Check for PWD status
            if self._is_pwd_candidate(match):
                boost_factor += self.diversity_boost['pwd']
                boost_reasons.append('Person with disability')
            
            # Check for first-generation learner
            if self._is_first_generation_candidate(match):
                boost_factor += self.diversity_boost['first_generation']
                boost_reasons.append('First-generation learner')
            
            # Apply boost
            boosted_score = min(original_score + boost_factor, 1.0)
            
            # Create boosted match
            boosted_match = match.copy()
            boosted_match.update({
                'original_score': original_score,
                'boosted_score': boosted_score,
                'score': boosted_score,  # Use boosted score for allocation
                'diversity_boost': boost_factor,
                'boost_reasons': boost_reasons
            })
            
            boosted_matches.append(boosted_match)
        
        # Re-sort by boosted scores
        boosted_matches.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return boosted_matches
    
    def _allocate_with_quotas(self, matches: List[Dict], internship_matches: Dict, 
                            quota_slots: Dict[str, int], internships: List[Dict]) -> Dict[str, Any]:
        """Perform allocation with quota management"""
        
        # Track allocations
        final_allocations = []
        quota_filled = {category: 0 for category in self.quotas.keys()}
        internship_capacity_used = {}
        
        # Initialize capacity tracking
        for internship in internships:
            internship_id = internship.get('id')
            capacity = internship.get('capacity', 1)
            internship_capacity_used[internship_id] = 0
        
        # Track allocated candidate IDs to prevent duplicates
        allocated_candidates = set()
        
        # Phase 1: Allocate quota categories first
        for category in ['sc', 'st', 'obc', 'ews']:  # Reserved categories first
            quota_limit = quota_slots.get(category, 0)
            
            for match in matches:
                if quota_filled[category] >= quota_limit:
                    break
                
                candidate_id = match.get('candidate_id')
                internship_id = match.get('internship_id')
                
                # Skip if candidate already allocated or internship full
                if (candidate_id in allocated_candidates or 
                    internship_capacity_used.get(internship_id, 0) >= 
                    self._get_internship_capacity(internship_id, internships)):
                    continue
                
                # Check if candidate belongs to current quota category
                if self._get_candidate_category(match) == category:
                    # Allocate
                    allocation = self._create_allocation_record(match, category, 'quota')
                    final_allocations.append(allocation)
                    
                    # Update tracking
                    allocated_candidates.add(candidate_id)
                    quota_filled[category] += 1
                    internship_capacity_used[internship_id] += 1
        
        # Phase 2: Allocate general category and fill remaining quota slots
        general_quota = quota_slots.get('general', 0)
        
        for match in matches:
            candidate_id = match.get('candidate_id')
            internship_id = match.get('internship_id')
            
            # Skip if candidate already allocated or internship full
            if (candidate_id in allocated_candidates or 
                internship_capacity_used.get(internship_id, 0) >= 
                self._get_internship_capacity(internship_id, internships)):
                continue
            
            candidate_category = self._get_candidate_category(match)
            
            # Try to allocate in general category or unfilled quota slots
            allocated = False
            allocation_type = 'general'
            
            # First try general category
            if candidate_category == 'general' and quota_filled['general'] < general_quota:
                quota_filled['general'] += 1
                allocated = True
                allocation_type = 'general'
            
            # Then try unfilled quota slots (merit-based allocation)
            elif not allocated:
                for category in ['sc', 'st', 'obc', 'ews']:
                    if quota_filled[category] < quota_slots[category]:
                        quota_filled[category] += 1
                        allocated = True
                        allocation_type = 'merit_in_quota'
                        break
                
                # If no quota slots available, try general merit
                if not allocated and quota_filled['general'] < general_quota:
                    quota_filled['general'] += 1
                    allocated = True
                    allocation_type = 'merit'
            
            if allocated:
                allocation = self._create_allocation_record(match, candidate_category, allocation_type)
                final_allocations.append(allocation)
                
                # Update tracking
                allocated_candidates.add(candidate_id)
                internship_capacity_used[internship_id] += 1
        
        return {
            'final_allocations': final_allocations,
            'quota_fulfillment': quota_filled,
            'summary': {
                'total_allocated': len(final_allocations),
                'total_capacity': sum(internship_capacity_used.values()),
                'quota_slots': quota_slots,
                'capacity_utilization': internship_capacity_used
            }
        }
    
    def _create_allocation_record(self, match: Dict, category: str, allocation_type: str) -> Dict[str, Any]:
        """Create allocation record with metadata"""
        return {
            'candidate_id': match.get('candidate_id'),
            'candidate_name': match.get('candidate_name'),
            'internship_id': match.get('internship_id'),
            'internship_title': match.get('internship_title'),
            'original_score': match.get('original_score', match.get('score', 0)),
            'final_score': match.get('score', 0),
            'category': category,
            'allocation_type': allocation_type,
            'diversity_boost': match.get('diversity_boost', 0),
            'boost_reasons': match.get('boost_reasons', []),
            'rural_background': match.get('rural_background', False),
            'timestamp': datetime.utcnow().isoformat(),
            'match_analysis': match.get('analysis', ''),
            'strengths': match.get('strengths', []),
            'recommendations': match.get('recommendations', [])
        }
    
    def _get_candidate_category(self, match: Dict) -> str:
        """Determine candidate's quota category"""
        # This would typically come from candidate profile data
        # For now, using fallback logic
        
        social_category = match.get('social_category', '').lower()
        
        if social_category in ['sc', 'scheduled caste']:
            return 'sc'
        elif social_category in ['st', 'scheduled tribe']:
            return 'st'
        elif social_category in ['obc', 'other backward class']:
            return 'obc'
        elif social_category in ['ews', 'economically weaker section']:
            return 'ews'
        else:
            return 'general'
    
    def _get_internship_capacity(self, internship_id: str, internships: List[Dict]) -> int:
        """Get capacity for specific internship"""
        for internship in internships:
            if internship.get('id') == internship_id:
                return internship.get('capacity', 1)
        return 1  # Default capacity
    
    def _is_rural_candidate(self, match: Dict) -> bool:
        """Check if candidate has rural background"""
        # This could be enhanced with more sophisticated rural area detection
        rural_indicators = [
            'village', 'rural', 'gram', 'tehsil', 'block', 'mandal', 
            'panchayat', 'agricultural', 'farming'
        ]
        
        location = match.get('location', '').lower()
        return any(indicator in location for indicator in rural_indicators)
    
    def _is_female_candidate(self, match: Dict) -> bool:
        """Check if candidate is female (placeholder - would need gender data)"""
        # This would come from candidate profile
        # For demo, randomly assign based on name patterns or explicit data
        return match.get('gender', '').lower() == 'female'
    
    def _is_pwd_candidate(self, match: Dict) -> bool:
        """Check if candidate has disability status"""
        return match.get('pwd_status', False) or match.get('disability', False)
    
    def _is_first_generation_candidate(self, match: Dict) -> bool:
        """Check if candidate is first-generation learner"""
        return match.get('first_generation_learner', False)
    
    def _generate_diversity_report(self, allocations: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive diversity report"""
        if not allocations:
            return {'error': 'No allocations to analyze'}
        
        total_allocated = len(allocations)
        
        # Category-wise breakdown
        category_breakdown = defaultdict(int)
        allocation_type_breakdown = defaultdict(int)
        rural_count = 0
        boosted_count = 0
        
        for allocation in allocations:
            category = allocation.get('category', 'unknown')
            allocation_type = allocation.get('allocation_type', 'unknown')
            
            category_breakdown[category] += 1
            allocation_type_breakdown[allocation_type] += 1
            
            if allocation.get('rural_background'):
                rural_count += 1
            
            if allocation.get('diversity_boost', 0) > 0:
                boosted_count += 1
        
        # Calculate percentages
        category_percentages = {
            category: (count / total_allocated) * 100 
            for category, count in category_breakdown.items()
        }
        
        return {
            'total_allocated': total_allocated,
            'category_breakdown': dict(category_breakdown),
            'category_percentages': category_percentages,
            'allocation_type_breakdown': dict(allocation_type_breakdown),
            'rural_representation': {
                'count': rural_count,
                'percentage': (rural_count / total_allocated) * 100
            },
            'diversity_boost_applied': {
                'count': boosted_count,
                'percentage': (boosted_count / total_allocated) * 100
            },
            'quota_compliance': self._check_quota_compliance(category_breakdown, total_allocated)
        }
    
    def _check_quota_compliance(self, category_breakdown: Dict, total_allocated: int) -> Dict[str, Any]:
        """Check if allocations comply with quota requirements"""
        compliance_report = {}
        
        for category, expected_percentage in self.quotas.items():
            actual_count = category_breakdown.get(category, 0)
            actual_percentage = (actual_count / total_allocated) * 100 if total_allocated > 0 else 0
            expected_count = int(total_allocated * expected_percentage)
            
            compliance_report[category] = {
                'expected_percentage': expected_percentage * 100,
                'actual_percentage': actual_percentage,
                'expected_count': expected_count,
                'actual_count': actual_count,
                'compliant': actual_count >= expected_count * 0.9  # 90% compliance threshold
            }
        
        return compliance_report
    
    def update_quotas(self, new_quotas: Dict[str, float]):
        """Update quota percentages"""
        # Validate that quotas sum to approximately 1.0
        total_quota = sum(new_quotas.values())
        if abs(total_quota - 1.0) > 0.01:
            raise ValueError(f"Quota percentages must sum to 1.0, got {total_quota}")
        
        self.quotas.update(new_quotas)
        logger.info(f"Quotas updated: {self.quotas}")
    
    def update_diversity_boosts(self, new_boosts: Dict[str, float]):
        """Update diversity boost factors"""
        self.diversity_boost.update(new_boosts)
        logger.info(f"Diversity boosts updated: {self.diversity_boost}")
