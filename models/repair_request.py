from odoo import _, api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

class RepairRequest(models.Model):
    _name = 'repair.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Repair Request"
    
    
    # --------------------------------------Basic Fields---------------------------------
    name = fields.Char(
        string='Request Reference', 
        required=True, 
        index='trigram', 
        copy=False, 
        default='New'
    )
    
    state = fields.Selection(
        selection=[
            ('draft','Draft'),
            ('in_progress','In Progress'),
            ('done','Done'),
        ],
        default="draft",
        required=True,
        tracking=True
    )
    
    priority = fields.Selection(
        selection=[
            ('0', 'Very Low'),
            ('1', 'Low'),
            ('2', 'Medium'),
            ('3', 'High'),
        ],
        string="Priority",
        default="0",
        required=True,
        tracking=True
    )
    dateline = fields.Date(
        string="Dateline",
        default=lambda self: datetime.today() + timedelta(days=7),
        required=True,
        tracking=True
    )
    description = fields.Text(
        string="Problem Description",
        required=True,
        tracking=True
    )
    device = fields.Char(
        string="Device",
        required=True,
        tracking=True
    )
    estimated_cost = fields.Float(
        string="Estimated Cost",
        compute='_compute_estimated_cost',
        store=False,
        tracking=True
    )
    start_date = fields.Datetime(
        string="Start Date",
        tracking=True
    )
    end_date = fields.Datetime(
        string="End Date",
        tracking=True
    )
    time_spent = fields.Float(
        string="Time Spent (Hours)",
        compute='_compute_time_spent_hours',
        store=True,
        tracking=True
    )
    
    # --------------------------------------Relation Fields---------------------------------
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True,
        tracking=True
    )
    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string="Invoice",
        readonly=True,
        tracking=True
    )
    repair_line_ids = fields.One2many(
        comodel_name='repair.request.line',
        inverse_name='repair_request_id',
        string="Repair Lines"
    )
    
    # --------------------------------------Computed Methods---------------------------------
    @api.depends('repair_line_ids.unit_price', 'repair_line_ids.product_qty','repair_line_ids.subtotal')
    def _compute_estimated_cost(self):
        for record in self:
            # total = sum(line.subtotal for line in record.repair_line_ids)
            total = sum(record.repair_line_ids.mapped('subtotal'))
            record.estimated_cost = total
            
    @api.depends('start_date', 'end_date')
    def _compute_time_spent_hours(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                print("Delta:", delta)
                record.time_spent = delta.total_seconds() / 3600.0
            else:
                record.time_spent = 0.0
                
    # -------------------------------Action Methods---------------------------------
    def action_start(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_("Only requests in 'Draft' state can be marked as In Progress."))
            
            record.state = 'in_progress'
            record.start_date = fields.Datetime.now()
            
    def action_done(self):
        for record in self:
            if record.state != 'in_progress':
                raise ValidationError(_("Only requests in 'In Progress' state can be marked as done."))
            
            record.state = 'done'
            record.end_date = fields.Datetime.now()
            
    def create_invoice(self):
        Invoice = self.env['account.move']
        for record in self:
            
            if record.state != 'done':
                raise ValidationError(_("Only requests in 'Done' state can be invoiced."))
            
            if not record.repair_line_ids:
                raise ValidationError(_("Cannot create an invoice without repair lines."))
                
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': record.partner_id.id,
                'ref': record.name,
                'invoice_line_ids': [
                    (0, 0,{
                        'product_id': line.product_id.id,
                        'quantity': line.product_qty,
                        'price_unit': line.unit_price,
                        'name': line.product_id.name,
                    }) for line in record.repair_line_ids
                ],
            }
            invoice = Invoice.create(invoice_vals)
            record.invoice_id = invoice.id
                        
    # --------------------------------CRUD Methods---------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('repair.request') or '/'

        return super().create(vals_list)