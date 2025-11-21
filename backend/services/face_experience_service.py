"""
FACE - Customer Experience Brain Module
User behavior analysis, UX optimization, personalization
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


@dataclass
class UserBehavior:
    """User behavior analysis"""
    user_id: str
    session_count: int
    avg_session_duration: float
    features_used: List[str]
    common_paths: List[str]
    drop_off_points: List[str]
    engagement_score: float


@dataclass
class UXInsight:
    """UX insight and recommendation"""
    insight_type: str
    component: str
    issue: str
    impact: str  # low, medium, high
    recommendation: str
    priority: str


@dataclass
class PersonalizationProfile:
    """User personalization profile"""
    user_id: str
    preferences: Dict[str, Any]
    recommended_features: List[str]
    content_preferences: Dict[str, Any]
    ui_preferences: Dict[str, Any]


class FaceExperienceService:
    """FACE - Customer Experience Brain Module"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def analyze_user_behavior(self, user_id: str, timeframe_days: int = 30) -> UserBehavior:
        """Analyze user behavior patterns"""
        try:
            start_date = datetime.utcnow() - timedelta(days=timeframe_days)
            
            # Get user sessions
            sessions = await self.db.user_sessions.find({
                'user_id': user_id,
                'created_at': {'$gte': start_date}
            }).to_list(length=1000)
            
            if not sessions:
                return UserBehavior(
                    user_id=user_id,
                    session_count=0,
                    avg_session_duration=0.0,
                    features_used=[],
                    common_paths=[],
                    drop_off_points=[],
                    engagement_score=0.0
                )
            
            # Calculate metrics
            session_count = len(sessions)
            total_duration = sum(s.get('duration_seconds', 0) for s in sessions)
            avg_duration = total_duration / session_count if session_count > 0 else 0.0
            
            # Get features used
            features_used = set()
            for session in sessions:
                features = session.get('features_accessed', [])
                features_used.update(features)
            
            # Get common navigation paths
            paths = []
            for session in sessions:
                path = session.get('navigation_path', [])
                if path:
                    paths.append(path)
            
            # Find drop-off points
            drop_offs = await self._identify_drop_off_points(user_id, start_date)
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(sessions)
            
            return UserBehavior(
                user_id=user_id,
                session_count=session_count,
                avg_session_duration=avg_duration,
                features_used=list(features_used),
                common_paths=self._find_common_paths(paths),
                drop_off_points=drop_offs,
                engagement_score=engagement_score
            )
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {str(e)}")
            raise
    
    async def get_ux_insights(self, organization_id: str) -> List[UXInsight]:
        """Get UX insights and recommendations"""
        try:
            # Get user feedback
            feedback = await self.db.user_feedback.find({
                'organization_id': organization_id,
                'created_at': {'$gte': datetime.utcnow() - timedelta(days=30)}
            }).to_list(length=100)
            
            insights = []
            
            # Analyze feedback patterns
            if feedback:
                common_issues = {}
                for item in feedback:
                    issue_type = item.get('issue_type', 'general')
                    common_issues[issue_type] = common_issues.get(issue_type, 0) + 1
                
                # Create insights for common issues
                for issue_type, count in common_issues.items():
                    if count >= 3:  # Threshold for actionable insight
                        insights.append(UXInsight(
                            insight_type='user_feedback',
                            component=issue_type,
                            issue=f"{count} users reported issues with {issue_type}",
                            impact='high' if count >= 10 else 'medium',
                            recommendation=self._get_ux_recommendation(issue_type),
                            priority='high' if count >= 10 else 'medium'
                        ))
            
            # Analyze drop-off points
            drop_offs = await self._analyze_organization_drop_offs(organization_id)
            for drop_off in drop_offs:
                insights.append(UXInsight(
                    insight_type='drop_off_analysis',
                    component=drop_off['page'],
                    issue=f"High drop-off rate at {drop_off['page']} ({drop_off['rate']:.1f}%)",
                    impact='high' if drop_off['rate'] > 30 else 'medium',
                    recommendation=f"Review {drop_off['page']} for usability issues",
                    priority='high' if drop_off['rate'] > 30 else 'medium'
                ))
            
            return insights
        except Exception as e:
            logger.error(f"Error getting UX insights: {str(e)}")
            raise
    
    async def create_personalization_profile(self, user_id: str) -> PersonalizationProfile:
        """Create personalized experience profile"""
        try:
            # Get user behavior
            behavior = await self.analyze_user_behavior(user_id)
            
            # Get user preferences from database
            user = await self.db.users.find_one({'_id': user_id})
            stored_preferences = user.get('preferences', {}) if user else {}
            
            # Determine recommended features based on behavior
            recommended_features = self._recommend_features(behavior)
            
            # Determine content preferences
            content_preferences = {
                'dashboard_layout': 'compact' if behavior.avg_session_duration < 300 else 'detailed',
                'notifications': 'enabled' if behavior.engagement_score > 70 else 'minimal',
                'theme': stored_preferences.get('theme', 'light')
            }
            
            # UI preferences
            ui_preferences = {
                'default_view': stored_preferences.get('default_view', 'overview'),
                'show_tutorials': behavior.engagement_score < 50,
                'compact_mode': behavior.avg_session_duration < 180
            }
            
            return PersonalizationProfile(
                user_id=user_id,
                preferences=stored_preferences,
                recommended_features=recommended_features,
                content_preferences=content_preferences,
                ui_preferences=ui_preferences
            )
        except Exception as e:
            logger.error(f"Error creating personalization profile: {str(e)}")
            raise
    
    async def optimize_onboarding(self, organization_id: str) -> Dict[str, Any]:
        """Optimize onboarding experience"""
        try:
            # Get onboarding data
            onboarding_sessions = await self.db.onboarding_sessions.find({
                'organization_id': organization_id,
                'created_at': {'$gte': datetime.utcnow() - timedelta(days=90)}
            }).to_list(length=1000)
            
            if not onboarding_sessions:
                return {
                    'completion_rate': 0.0,
                    'avg_time': 0.0,
                    'drop_off_steps': [],
                    'recommendations': []
                }
            
            # Calculate completion rate
            completed = sum(1 for s in onboarding_sessions if s.get('completed', False))
            completion_rate = (completed / len(onboarding_sessions)) * 100
            
            # Calculate average time
            times = [s.get('completion_time_seconds', 0) for s in onboarding_sessions if s.get('completed')]
            avg_time = sum(times) / len(times) if times else 0.0
            
            # Find drop-off steps
            drop_off_steps = await self._find_onboarding_drop_offs(onboarding_sessions)
            
            # Generate recommendations
            recommendations = []
            if completion_rate < 70:
                recommendations.append('Simplify onboarding flow')
            if avg_time > 900:  # > 15 minutes
                recommendations.append('Reduce onboarding time')
            if drop_off_steps:
                recommendations.append(f'Review step: {drop_off_steps[0]["step"]}')
            
            return {
                'completion_rate': completion_rate,
                'avg_time': avg_time,
                'drop_off_steps': drop_off_steps,
                'recommendations': recommendations
            }
        except Exception as e:
            logger.error(f"Error optimizing onboarding: {str(e)}")
            raise
    
    def _calculate_engagement_score(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate user engagement score"""
        if not sessions:
            return 0.0
        
        score = 0.0
        
        # Session frequency (max 30 points)
        session_count = len(sessions)
        score += min(session_count * 2, 30)
        
        # Average session duration (max 30 points)
        avg_duration = sum(s.get('duration_seconds', 0) for s in sessions) / len(sessions)
        score += min(avg_duration / 10, 30)
        
        # Feature usage (max 20 points)
        all_features = set()
        for session in sessions:
            all_features.update(session.get('features_accessed', []))
        score += min(len(all_features) * 2, 20)
        
        # Recent activity (max 20 points)
        recent_sessions = [s for s in sessions if s.get('created_at', datetime.min) > datetime.utcnow() - timedelta(days=7)]
        score += min(len(recent_sessions) * 2, 20)
        
        return min(score, 100.0)
    
    def _find_common_paths(self, paths: List[List[str]]) -> List[str]:
        """Find common navigation paths"""
        if not paths:
            return []
        
        # Count path occurrences
        path_counts = {}
        for path in paths:
            path_str = ' -> '.join(path[:5])  # First 5 steps
            path_counts[path_str] = path_counts.get(path_str, 0) + 1
        
        # Return top 5 most common paths
        sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)
        return [path for path, count in sorted_paths[:5]]
    
    async def _identify_drop_off_points(self, user_id: str, start_date: datetime) -> List[str]:
        """Identify where users drop off"""
        try:
            sessions = await self.db.user_sessions.find({
                'user_id': user_id,
                'created_at': {'$gte': start_date}
            }).to_list(length=100)
            
            drop_offs = []
            for session in sessions:
                path = session.get('navigation_path', [])
                if path and len(path) < 5:  # Short sessions indicate drop-off
                    drop_offs.append(path[-1] if path else 'unknown')
            
            # Return most common drop-off points
            from collections import Counter
            return [point for point, count in Counter(drop_offs).most_common(3)]
        except Exception as e:
            logger.warning(f"Error identifying drop-off points: {str(e)}")
            return []
    
    async def _analyze_organization_drop_offs(self, organization_id: str) -> List[Dict[str, Any]]:
        """Analyze drop-off rates across organization"""
        try:
            # Get all sessions for organization
            sessions = await self.db.user_sessions.find({
                'organization_id': organization_id,
                'created_at': {'$gte': datetime.utcnow() - timedelta(days=30)}
            }).to_list(length=1000)
            
            # Count visits and drop-offs per page
            page_stats = {}
            for session in sessions:
                path = session.get('navigation_path', [])
                if path:
                    for i, page in enumerate(path):
                        if page not in page_stats:
                            page_stats[page] = {'visits': 0, 'drop_offs': 0}
                        page_stats[page]['visits'] += 1
                        
                        # If this is the last page in a short session, it's a drop-off
                        if i == len(path) - 1 and len(path) < 5:
                            page_stats[page]['drop_offs'] += 1
            
            # Calculate drop-off rates
            drop_offs = []
            for page, stats in page_stats.items():
                if stats['visits'] > 10:  # Only consider pages with significant traffic
                    rate = (stats['drop_offs'] / stats['visits']) * 100
                    if rate > 20:  # > 20% drop-off rate
                        drop_offs.append({
                            'page': page,
                            'rate': rate,
                            'visits': stats['visits'],
                            'drop_offs': stats['drop_offs']
                        })
            
            return sorted(drop_offs, key=lambda x: x['rate'], reverse=True)
        except Exception as e:
            logger.warning(f"Error analyzing organization drop-offs: {str(e)}")
            return []
    
    def _recommend_features(self, behavior: UserBehavior) -> List[str]:
        """Recommend features based on behavior"""
        recommendations = []
        
        if behavior.engagement_score > 70:
            recommendations.extend(['advanced_analytics', 'custom_reports'])
        
        if 'campaigns' in behavior.features_used:
            recommendations.extend(['a_b_testing', 'creative_optimization'])
        
        if behavior.avg_session_duration > 600:  # > 10 minutes
            recommendations.append('detailed_dashboard')
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _get_ux_recommendation(self, issue_type: str) -> str:
        """Get UX recommendation for issue type"""
        recommendations = {
            'navigation': 'Simplify navigation structure and add breadcrumbs',
            'performance': 'Optimize page load times and implement lazy loading',
            'mobile': 'Improve mobile responsiveness and touch interactions',
            'accessibility': 'Enhance accessibility features and keyboard navigation',
            'general': 'Conduct user testing to identify specific pain points'
        }
        return recommendations.get(issue_type, 'Review user feedback for specific improvements')
    
    async def _find_onboarding_drop_offs(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find where users drop off during onboarding"""
        step_counts = {}
        for session in sessions:
            current_step = session.get('current_step', 'unknown')
            if current_step not in step_counts:
                step_counts[current_step] = {'started': 0, 'completed': 0}
            step_counts[current_step]['started'] += 1
            
            if session.get('completed'):
                step_counts[current_step]['completed'] += 1
        
        drop_offs = []
        for step, counts in step_counts.items():
            if counts['started'] > 5:  # Only consider steps with significant traffic
                completion_rate = (counts['completed'] / counts['started']) * 100
                if completion_rate < 80:  # < 80% completion
                    drop_offs.append({
                        'step': step,
                        'completion_rate': completion_rate,
                        'started': counts['started'],
                        'completed': counts['completed']
                    })
        
        return sorted(drop_offs, key=lambda x: x['completion_rate'])

