export type Product = { product_code:string; product_name:string; current_unit_price:number; tax_rate:number; image_url:string|null; quantity:number };
export type PurchaseDetail = {product_code:string;product_name:string;quantity:number;sold_unit_price:number;discount_amount:number;applied_tax_rate:number;tax_amount:number;line_total:number};
export type PurchaseQuote = {subtotal:number;tax_total:number;grand_total:number;tax_breakdown:Record<string,{taxable_amount:number;tax_amount:number}>;details:PurchaseDetail[]};
export type PurchaseResult = Omit<PurchaseQuote,'details'> & {transaction_id:string};
export type Member = { member_id:string; name:string };
export type Transaction = { transaction_id:string; purchased_at:string; member_id:string|null; cashier_name:string; subtotal:number; tax_total:number; grand_total:number; details:Array<{product_name:string;quantity:number;sold_unit_price:number;discount_amount:number;applied_tax_rate:number;tax_amount:number;line_total:number}> };
