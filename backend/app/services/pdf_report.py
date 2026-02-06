"""PDF report generation service"""

from typing import List, Dict, Optional
from datetime import datetime
from fpdf import FPDF, FPDFException
import os
import io


class PDFReportGenerator:
    """PDF 报告生成器"""
    
    def __init__(self):
        self.pdf = None
        self.page_width = 210  # A4 width in mm
        self.page_height = 297  # A4 height in mm
        self.margin = 20
        self.content_width = self.page_width - (2 * self.margin)
    
    def create_intervent_report(
        self,
        user_info: Dict,
        health_profile: Optional[Dict],
        interventions: List[Dict],
        recommendations: List[Dict],
        goals: Optional[List[Dict]] = None
    ) -> bytes:
        """
        生成干预报告 PDF
        
        Args:
            user_info: 用户信息
            health_profile: 健康档案
            interventions: 推荐的干预措施列表
            recommendations: 推荐详情列表
            goals: 健康目标列表
        
        Returns:
            PDF 文件的字节内容
        """
        try:
            self.pdf = FPDF()
            self.pdf.add_page()
            
            # Header
            self._add_header()
            
            # User info section
            self._add_user_info(user_info)
            
            # Health profile section
            if health_profile:
                self._add_health_profile(health_profile)
            
            # Recommendations section
            self._add_recommendations(recommendations)
            
            # Intervention details section
            self._add_intervent_details(interventions)
            
            # Goals section
            if goals:
                self._add_goals(goals)
            
            # Footer
            self._add_footer()
            
            # Output to bytes
            output = io.BytesIO()
            self.pdf.output(output, 'F')
            return output.getvalue()
        
        except FPDFException as e:
            raise Exception(f"PDF generation failed: {str(e)}")
        
        finally:
            self.pdf = None
    
    def _add_header(self):
        """添加报告页眉"""
        self.pdf.set_fill_color(59, 130, 246)  # Blue
        self.pdf.rect(0, 0, self.page_width, 40, 'F')
        
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_font_size(24)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.l_margin = self.margin
        self.pdf.cell(self.content_width, 15, '长寿医学临床干预报告', ln=1, align='C')
        
        self.pdf.set_font_size(12)
        self.pdf.ln(5)
        self.pdf.cell(self.content_width, 10, f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=1, align='R')
        
        self.pdf.ln(10)
    
    def _add_user_info(self, user_info: Dict):
        """添加用户信息部分"""
        self.pdf.set_font_size(16)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font('', 'B')
        self.pdf.cell(self.content_width, 10, '1. 用户信息', ln=1)
        
        self.pdf.set_font('', '')
        self.pdf.set_font_size(12)
        self.pdf.ln(5)
        
        # Two-column layout
        col_width = self.content_width / 2
        
        # Left column
        self.pdf.cell(col_width, 8, f'姓名: {user_info.get("full_name", "N/A")}', ln=0)
        self.pdf.cell(col_width, 8, f'邮箱: {user_info.get("email", "N/A")}', ln=1)
        self.pdf.cell(col_width, 8, f'用户名: {user_info.get("username", "N/A")}', ln=0)
        self.pdf.cell(col_width, 8, f'账号状态: {"活跃" if user_info.get("is_active") else "未激活"}', ln=1)
        
        self.pdf.ln(10)
    
    def _add_health_profile(self, health_profile: Dict):
        """添加健康档案部分"""
        self.pdf.set_font_size(16)
        self.pdf.set_font('', 'B')
        self.pdf.cell(self.content_width, 10, '2. 健康档案', ln=1)
        
        self.pdf.set_font('', '')
        self.pdf.set_font_size(12)
        self.pdf.ln(5)
        
        # Table header
        self.pdf.set_fill_color(240, 240, 240)
        self.pdf.cell(60, 8, '项目', ln=0, align='C', fill=1)
        self.pdf.cell(80, 8, '值', ln=0, align='C', fill=1)
        self.pdf.cell(self.content_width - 140, 8, '说明', ln=1, align='C', fill=1)
        self.pdf.ln(0)
        
        # Profile data
        self.pdf.set_fill_color(255, 255, 255)
        self._add_profile_row('年龄', f'{health_profile.get("age", "N/A")}岁')
        self._add_profile_row('性别', health_profile.get("gender", "N/A"))
        self._add_profile_row('体重', f'{health_profile.get("weight", "N/A")} kg')
        self._add_profile_row('身高', f'{health_profile.get("height", "N/A")} cm')
        
        # Blood pressure
        bp = f'{health_profile.get("blood_pressure_systolic", "N/A")}/{health_profile.get("blood_pressure_diastolic", "N/A")} mmHg'
        self._add_profile_row('血压', bp, '收缩压/舒张压')
        
        self._add_profile_row('静息心率', f'{health_profile.get("heart_rate", "N/A")} bpm')
        
        # Medical conditions
        conditions = health_profile.get("medical_conditions", [])
        if conditions:
            self._add_profile_row('疾病史', ', '.join(conditions))
        
        self.pdf.ln(10)
    
    def _add_profile_row(self, label: str, value: str, note: str = ''):
        """添加健康档案行"""
        self.pdf.cell(60, 8, label, ln=0, border=0)
        self.pdf.cell(80, 8, value, ln=0, border=0)
        self.pdf.cell(self.content_width - 140, 8, note, ln=1, border=0)
        self.pdf.ln(0)
    
    def _add_recommendations(self, recommendations: List[Dict]):
        """添加推荐部分"""
        self.pdf.set_font_size(16)
        self.pdf.set_font('', 'B')
        self.pdf.cell(self.content_width, 10, '3. 个性化推荐', ln=1)
        
        self.pdf.set_font('', '')
        self.pdf.set_font_size(12)
        self.pdf.ln(5)
        
        for i, rec in enumerate(recommendations, 1):
            self.pdf.set_font_size(14)
            self.pdf.set_text_color(59, 130, 246)
            self.pdf.cell(self.content_width, 10, f'{i}. {rec["name"]}', ln=1)
            
            self.pdf.set_font_size(11)
            self.pdf.set_text_color(0, 0, 0)
            
            # Category and evidence level
            category_text = f'分类: {rec["category"]} | 证据等级: Level {rec["evidence_level"]}'
            self.pdf.cell(self.content_width, 7, category_text, ln=1)
            
            # Score breakdown
            self.pdf.ln(3)
            components = rec.get("components", {})
            
            self.pdf.set_fill_color(245, 245, 245)
            self.pdf.cell(100, 7, '评分项', ln=0, align='L', fill=1)
            self.pdf.cell(80, 7, '得分', ln=1, align='L', fill=1)
            self.pdf.ln(0)
            
            self.pdf.set_fill_color(255, 255, 255)
            
            score_labels = {
                'evidence_quality': '证据质量',
                'health_match': '健康匹配度',
                'risk_benefit': '风险收益比',
                'drug_interaction': '药物相互作用',
                'age_appropriateness': '年龄适宜性'
            }
            
            for key, value in components.items():
                label = score_labels.get(key, key)
                score = f'{value * 100:.1f}'
                self.pdf.cell(100, 6, label, ln=0, border=0)
                self.pdf.cell(80, 6, score, ln=1, border=0)
            
            # Net benefit
            net_benefit = rec.get("net_benefit", 0)
            self.pdf.ln(5)
            self.pdf.set_font_size(12)
            self.pdf.set_font('', 'B')
            
            benefit_color = (0, 128, 0) if net_benefit > 0 else (255, 0, 0)
            self.pdf.set_text_color(*benefit_color)
            
            benefit_text = f'净收益: {net_benefit * 100:.1f}%'
            self.pdf.cell(self.content_width, 8, benefit_text, ln=1)
            
            # Reasoning
            if rec.get("reasoning"):
                self.pdf.set_font('', '')
                self.pdf.set_font_size(10)
                self.pdf.set_text_color(80, 80, 80)
                self.pdf.ln(3)
                self.pdf.multi_cell(
                    w=self.content_width - 10,
                    h=0,
                    txt=rec["reasoning"],
                    border=0,
                    align='L',
                    fill=0,
                    max_line_height=5
                )
                self.pdf.ln()
            
            self.pdf.ln(10)
            
            # Page break check
            if self.pdf.get_y() > self.page_height - 50:
                self.pdf.add_page()
                self._add_header()
    
    def _add_intervent_details(self, interventions: List[Dict]):
        """添加干预措施详情部分"""
        self.pdf.set_font_size(16)
        self.pdf.set_font('', 'B')
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(self.content_width, 10, '4. 干预措施详情', ln=1)
        
        self.pdf.set_font('', '')
        self.pdf.set_font_size(12)
        self.pdf.ln(5)
        
        for intervention in interventions:
            self.pdf.set_font_size(14)
            self.pdf.cell(self.content_width, 10, f'• {intervention["name"]}', ln=1)
            
            # Description
            if intervention.get("description"):
                self.pdf.set_font_size(11)
                self.pdf.ln(3)
                self.pdf.multi_cell(
                    w=self.content_width,
                    h=0,
                    txt=intervention["description"],
                    border=0,
                    align='L',
                    fill=0,
                    max_line_height=4
                )
                self.pdf.ln()
            
            # Mechanism
            if intervention.get("mechanism"):
                self.pdf.ln(3)
                self.pdf.set_font_size(10)
                self.pdf.set_text_color(80, 80, 80)
                self.pdf.cell(20, 6, '机制:', ln=0)
                self.pdf.multi_cell(
                    w=self.content_width - 30,
                    h=0,
                    txt=intervention["mechanism"],
                    border=0,
                    align='L',
                    fill=0,
                    max_line_height=4
                )
                self.pdf.ln()
            
            self.pdf.ln(8)
            
            # Page break check
            if self.pdf.get_y() > self.page_height - 50:
                self.pdf.add_page()
                self._add_header()
    
    def _add_goals(self, goals: List[Dict]):
        """添加健康目标部分"""
        self.pdf.set_font_size(16)
        self.pdf.set_font('', 'B')
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(self.content_width, 10, '5. 健康目标', ln=1)
        
        self.pdf.set_font('', '')
        self.pdf.set_font_size(12)
        self.pdf.ln(5)
        
        for goal in goals:
            self.pdf.ln(3)
            self.pdf.set_font_size(13)
            self.pdf.cell(80, 8, f'• {goal["goal_type"]}', ln=0)
            
            status_text = {
                'not_started': '未开始',
                'in_progress': '进行中',
                'achieved': '已达成',
                'missed': '未达成'
            }.get(goal.get("status"), goal.get("status", ""))
            
            status_color = (200, 200, 200)
            if goal.get("status") == "achieved":
                status_color = (0, 128, 0)
            elif goal.get("status") == "missed":
                status_color = (255, 0, 0)
            
            self.pdf.set_fill_color(*status_color)
            self.pdf.cell(50, 8, status_text, ln=1, align='C', fill=1)
            self.pdf.set_fill_color(255, 255, 255)
            
            # Target and current
            self.pdf.set_font_size(11)
            target_text = f'目标: {goal["target_value"]} {goal.get("unit", "")} | 当前: {goal.get("current_value", "N/A")}'
            self.pdf.cell(self.content_width, 7, target_text, ln=1, border=0)
            
            self.pdf.ln(5)
            
            # Page break check
            if self.pdf.get_y() > self.page_height - 50:
                self.pdf.add_page()
                self._add_header()
    
    def _add_footer(self):
        """添加页脚"""
        # Add disclaimer
        if self.pdf.get_y() > self.page_height - 40:
            self.pdf.add_page()
        
        self.pdf.set_y(self.page_height - 30)
        self.pdf.set_font_size(9)
        self.pdf.set_text_color(150, 150, 150)
        self.pdf.ln(5)
        self.pdf.cell(self.content_width, 5, '免责声明: 本报告仅供参考，不能替代专业医疗建议。请咨询医生后再开始任何干预措施。', ln=1, align='C', border=0)
        self.pdf.cell(self.content_width, 5, f'第 {self.pdf.page_no()} 页', ln=1, align='R', border=0)


def generate_report(
    user_info: Dict,
    health_profile: Optional[Dict] = None,
    interventions: List[Dict] = [],
    recommendations: List[Dict] = [],
    goals: Optional[List[Dict]] = None
) -> bytes:
    """
    生成干预报告的便捷函数
    
    Returns:
        PDF 文件的字节内容
    """
    generator = PDFReportGenerator()
    return generator.create_intervent_report(
        user_info=user_info,
        health_profile=health_profile,
        interventions=interventions,
        recommendations=recommendations,
        goals=goals
    )


def save_report_to_file(
    pdf_bytes: bytes,
    filename: str,
    output_dir: str = "./reports"
) -> str:
    """
    保存 PDF 报告到文件
    
    Args:
        pdf_bytes: PDF 字节内容
        filename: 文件名（不需要.pdf后缀）
        output_dir: 输出目录
    
    Returns:
        完整文件路径
    """
    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Full file path
    filepath = os.path.join(output_dir, f"{filename}.pdf")
    
    # Write PDF
    with open(filepath, 'wb') as f:
        f.write(pdf_bytes)
    
    return filepath
