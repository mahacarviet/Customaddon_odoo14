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
        search_class = self.env['education.class.division'].sudo().search(
            [('id', '=', self.from_promotion_education_division.id)], limit=1)
        if search_class:
            # todo: Them thong tin lop hoc cu
            for student in search_class.student_ids:
                student.class_history_ids = [(0, 0, {'class_id': self.from_promotion_education_division.name,
                                                     'academic_year_id': self.from_promotion_education_division.academic_year_id.id
                                                     })]

            # todo: Tach hoc sinh luu ban ra khoi lop
            if self.student_education_division:
                for student_down in self.student_education_division:
                    student_down.class_id = False
            else:
                pass

            # todo: Sua thong tin lop
            if int(search_class.class_id.id) < 4:
                search_class.class_id = (int(search_class.class_id.id + 1))
        else:
            raise ValidationError('Không tìm thấy dữ liệu của lớp này.')
