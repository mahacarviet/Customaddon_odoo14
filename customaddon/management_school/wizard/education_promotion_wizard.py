from odoo import fields, models, api
from odoo.exceptions import ValidationError


class EducationPromotionWizard(models.TransientModel):
    _name = 'education.promotion.wizard'

    from_promotion_education_division = fields.Many2one('education.class.division', string='Lớp học gốc')
    # to_promotion_education_division = fields.Many2many('education.class.division', string='Chuyển lên lớp')
    # student_education_division = fields.One2many(related='from_promotion_education_division.student_ids')
    student_education_division = fields.Many2many('education.student', string='Danh sách học sinh lưu ban',
                                                  domain="[('class_id', '=', from_promotion_education_division)]")

    def action_education_promotion_wizard(self):
        pass
