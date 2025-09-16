from odoo import _, api, fields, models

class RepairRequestLine(models.Model):
    _name = "repair.request.line"
    _description = "Repair Request Line"
    
    # --------------------------------------Basic Fields---------------------------------
    product_qty = fields.Float(
        string="Quantity",
        required=True,
        default=1.0
    )
    unit_price = fields.Float(
        string="Unit Price",
        required=True,
        default=0.0
    )
    subtotal = fields.Float(
        string="Subtotal",
        compute='_compute_subtotal',
        store=True
    ) 
    
    # --------------------------------------Relational Fields---------------------------------
    repair_request_id = fields.Many2one(
        comodel_name="repair.request",
        string="Repair Request",
        ondelete="cascade"
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
    )
    
    # --------------------------------------Compute Methods---------------------------------
    @api.depends('product_qty', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.product_qty * line.unit_price