"""Enhanced recommendation engine with personalized scoring"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import (
    User, UserHealthProfile, Intervention, Evidence,
    RiskFactor, Benefit, Recommendation
)
from app.services.drug_interactions import detect_interactions, get_interaction_summary


class RecommendationEngine:
    """个性化推荐引擎"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_personalized_recommendations(
        self,
        user_id: int,
        limit: int = = 10,
        exclude_categories: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        生成个性化干预推荐
        
        Args:
            user_id: 用户 ID
            limit: 返回推荐数量限制
            exclude_categories: 排除的分类
        
        Returns:
            推荐列表，按分数排序
        """
        # Get user profile
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        health_profile = self.db.query(UserHealthProfile).filter(
            UserHealthProfile.user_id == user_id
        ).first()
        
        # Get all interventions
        interventions = self.db.query(Intervention).all()
        
        if exclude_categories:
            interventions = [
                i for i in interventions
                if i.category not in exclude_categories
            ]
        
        # Score each intervention
        scored_interventions = []
        for intervention in interventions:
            score = self._calculate_intervention_score(
                intervention,
                health_profile,
                user
            )
            
            scored_interventions.append({
                "intervention_id": intervention.id,
                "name": intervention.name,
                "category": intervention.category,
                "score": score["total"],
                "components": score["components"],
                "reasoning": score["reasoning"]
            })
        
        # Sort by score (descending)
        scored_interventions.sort(key=lambda x: x["score"], reverse=True=True)
        
        return scored_interventions[:limit]
    
    def _calculate_intervention_score(
        self,
        intervention: Intervention,
        health_profile: Optional[UserHealthProfile],
        user: User
    ) -> Dict:
        """
        计算干预措施的综合得分
        
        考虑因素：
        1. 证据质量 (30% 权重)
        2. 健康档案匹配度 (25% 权重)
        3. 风险-收益比 (25% 权重)
        4. 药物相互作用 (15% 权重)
        5. 年龄适宜性 (5% 权重)
        """
        components = {}
        reasoning = []
        
        # 1. Evidence quality score
        evidence_score = self._calculate_evidence_score(intervention)
        components["evidence_quality"] = evidence_score
        if evidence_score > 0.7:
            reasoning.append("高质量证据支持")
        elif evidence_score > 0.4:
            reasoning.append("中等质量证据")
        
        # 2. Health profile matching
        health_match_score = self._calculate_health_match_score(
            intervention,
            health_profile
        )
        components["health_match"] = health_match_score
        
        # 3. Risk-benefit ratio
        risk_benefit_score = self._calculate_risk_benefit_score(intervention)
        components["risk_benefit"] = risk_benefit_score
        
        # 4. Drug interactions (negative score if conflicts exist)
        drug_interaction_score = self._calculate_drug_interaction_score(
            intervention,
            health_profile
        )
        components["drug_interaction"] = drug_interaction_score
        if drug_interaction_score < -0.5:
            reasoning.append("存在药物相互作用风险")
        
        # 5. Age appropriateness
        age_appropriateness_score = self._calculate_age_appropriateness(
            intervention,
            health_profile
        )
        components["age_appropriateness"] = age_appropriateness_score
        
        # Calculate weighted total
        total_score = (
            evidence_score * 0.30 +
            health_match_score * 0.25 +
            risk_benefit_score * 0.25 +
            drug_interaction_score * 0.15 +
            age_appropriateness_score * 0.05
        )
        
        return {
            "total": max(-1, min(1, total_score)),  # Normalize to [-1, 1]
            "components": components,
            "reasoning": "; ".join(reasoning) if reasoning else "基于证据匹配"
        }
    
    def _calculate_evidence_score(self, intervention: Intervention) -> float:
        """计算证据质量得分 (0-1)"""
        evidence_list = self.db.query(Evidence).filter(
            Evidence.intervention_id == intervention.id
        ).all()
        
        if not evidence_list:
            return 0.1  # Low score if no evidence
        
        # Base score from evidence level
        level_score = (5 - intervention.evidence_level) / 4.0  # Level 1 -> 1.0, Level 4 -> 0.25
        
        # Bonus for quality scores
        avg_quality = sum(e.quality_score or 0 for e in evidence_list) / len(evidence_list)
        quality_bonus = avg_quality / 100.0 * 0.3  # 0-0.3 bonus
        
        # Bonus for randomized trials
        rct_count = sum(1 for e in evidence_list if e.source_type == "randomized_trial")
        if rct_count > 0:
            rct_bonus = min(0.2, rct_count * 0.05)
        else:
            rct_bonus = 0.0
        
        # Bonus for meta-analyses
        meta_count = sum(1 for e in evidence_list if e.source_type == "meta_analysis")
        if meta_count > 0:
            meta_bonus = 0.15
        else:
            meta_bonus = 0.0
        
        return min(1.0, level_score + quality_bonus + rct_bonus + meta_bonus)
    
    def _calculate_health_match_score(
        self,
        intervention: Intervention,
        health_profile: Optional[UserHealthProfile]
    ) -> float:
        """计算健康档案匹配度 (0-1)"""
        if not health_profile:
            return 0.5  # Neutral score if no profile
        
        score = 0.5  # Base score
        
        # Category-specific matching
        if intervention.category == "supplement":
            # Check for relevant conditions
            if health_profile.medical_conditions:
                conditions = health_profile.medical_conditions or []
                # Bonus for cardiovascular health
                if any("cardio" in c.lower() for c in conditions):
                    if "vitamin_d" in intervention.name.lower():
                        score += 0.15
                    if "omega_3" in intervention.name.lower():
                        score += 0.1
                # Bonus for blood pressure
                if any("hypertension" in c.lower() for c in conditions):
                    if "magnesium" in intervention.name.lower() or "potassium" in intervention.name.lower():
                        score += 0.15
        
        elif intervention.category == "exercise":
            # Age-appropriate exercise
            if health_profile.age:
                if health_profile.age > 65:
                    if "walking" in intervention.name.lower() or "tai_chi" in intervention.name.lower():
                        score += 0.2
                elif health_profile.age < 40:
                    if "hiit" in intervention.name.lower() or "strength" in intervention.name.lower():
                        score += 0.2
        
        elif intervention.category == "nutrition":
            # Blood pressure management
            if health_profile.blood_pressure_systolic:
                if health_profile.blood_pressure_systolic > 140:
                    if "dash" in intervention.name.lower() or "mediterranean" in intervention.name.lower():
                        score += 0.15
        
        return max(0, min(1, score))
    
    def _calculate_risk_benefit_score(self, intervention: Intervention) -> float:
        """计算风险-收益比 (0-1)"""
        risks = self.db.query(RiskFactor).filter(
            RiskFactor.intervention_id == intervention.id
        ).all()
        
        benefits = self.db.query(Benefit).filter(
            Benefit.intervention_id == intervention.id
        ).all()
        
        if not benefits:
            return 0.2  # Low score if no benefits documented
        
        # Calculate total risk (weighted by severity)
        severity_weights = {"mild": 1, "moderate": 2, "severe": 4}
        total_risk = sum(
            (r.frequency or 0) / 100 * severity_weights.get(r.severity, 1)
            for r in risks
        )
        
        # Calculate total benefit (weighted by confidence)
        total_benefit = sum(
            (b.effect_size or 0) / 10 * ((b.confidence or 50) / 100)
            for b in benefits
        )
        
        # Net benefit score (0-1)
        if total_benefit > total_risk:
            ratio = total_risk / total_benefit if total_benefit > 0 else 0
            score = 1 - ratio
        else:
            score = -0.3  # Penalty for more risk than benefit
        
        return max(-0.5, min(1, score))
    
    def _calculate_drug_interaction_score(
        self,
        intervention: Intervention,
        health_profile: Optional[UserHealthProfile]
    ) -> float:
        """计算药物相互作用得分 (-1 to 0)"""
        if not health_profile or not health_profile.current_medications:
            return 0.0  # Neutral if no medications
        
        # Check if this intervention is a medication/supplement
        if intervention.category not in ["supplement", "medical"]:
            return 0.0
        
        # Get medication name from intervention
        med_name = intervention.name.lower().replace(" ", "_")
        
        # Normalize current medications
        current_meds = health_profile.current_medications or []
        all_meds = current_meds + [intervention.name]
        
        # Detect interactions
        interactions = detect_interactions(all_meds)
        
        if not interactions:
            return 0.0  # No interactions
        
        # Calculate penalty based on severity
        severity_penalties = {"mild": -0.1, "moderate": -0.3, "high": -0.5}
        total_penalty = 0.0
        
        for interaction in interactions:
            total_penalty += severity_penalties.get(interaction.severity, -0.2)
        
        return max(-1.0, total_penalty)
    
    def _calculate_age_appropriateness(
        self,
        intervention: Intervention,
        health_profile: Optional[UserHealthProfile]
    ) -> float:
        """计算年龄适宜性得分 (0-1)"""
        if not health_profile or not health_profile.age:
            return 0.5  # Neutral if no age
        
        age = health_profile.age
        score = 0.5  # Base score
        
        # Exercise category
        if intervention.category == "exercise":
            if age < 30:
                if "hiit" in intervention.name.lower() or "crossfit" in intervention.name.lower():
                    score += 0.3
                elif "walking" in intervention.name.lower():
                    score -= 0.1
            elif 30 <= age < 50:
                if "running" in intervention.name.lower() or "swimming" in intervention.name.lower():
                    score += 0.2
                elif "heavy" in intervention.name.lower():
                    score -= 0.1
            elif age >= 50:
                if "walking" in intervention.name.lower() or "tai_chi" in intervention.name.lower():
                    score += 0.3
                elif "hiit" in intervention.name.lower() or "plyometrics" in intervention.name.lower():
                    score -= 0.2
        
        # Supplement category
        elif intervention.category == "supplement":
            if age >= 50:
                if "calcium" in intervention.name.lower() or "vitamin_d" in intervention.name.lower():
                    score += 0.2
                elif "creatine" in intervention.name.lower():
                    score -= 0.1
        
        return max(0, min(1, score))
    
    def explain_recommendation(
        self,
        intervention_id: int,
        user_id: int
    ) -> Dict:
        """生成推荐的详细解释"""
        intervention = self.db.query(Intervention).filter(
            Intervention.id == intervention_id
        ).first()
        
        health_profile = self.db.query(UserHealthProfile).filter(
            UserHealthProfile.user_id == user_id
        ).first()
        
        if not intervention:
            return {"error": "Intervention not found"}
        
        # Get scores
        score_data = self._calculate_intervention_score(
            intervention, health_profile, self.db.query(User).filter(User.id == user_id).first()
        )
        
        # Get evidence details
        evidence = self.db.query(Evidence).filter(
            Evidence.intervention_id == intervention_id
        ).all()
        
        # Get drug interactions if any
        interactions = []
        if health_profile and health_profile.current_medications:
            all_meds = health_profile.current_medications + [intervention.name]
            interactions = detect_interactions(all_meds)
        
        return {
            "intervention": intervention.name,
            "total_score": score_data["total"],
            "score_breakdown": score_data["components"],
            "reasoning": score_data["reasoning"],
            "evidence_summary": {
                "total": len(evidence),
                "by_level": {
                    level: sum(1 for e in evidence if e.evidence_level == level)
                    for level in [1, 2, 3, 4]
                },
                "avg_quality": sum(e.quality_score or 0 for e in evidence) / len(evidence) if evidence else 0
            },
            "drug_interactions": {
                "count": len(interactions),
                "details": [i.to_dict() for i in interactions],
                "summary": get_interaction_summary(interactions)
            }
        }
