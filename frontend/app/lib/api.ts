import type { Member, Product, PurchaseQuote, PurchaseResult, Transaction } from './types';
async function request<T>(path:string, options:RequestInit={}):Promise<T>{const response=await fetch(path,options);const body=await response.json();if(!response.ok)throw new Error(typeof body.detail==='string'?body.detail:'入力内容を確認してください');return body;}
const auth=(token:string)=>({Authorization:`Bearer ${token}`});
export const loginCashier=(cashier_id:string,password:string)=>request<{access_token:string;cashier:{display_name:string}}>('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cashier_id,password})});
export const fetchMember=(token:string,id:string)=>request<Member>(`/api/members/${encodeURIComponent(id)}`,{headers:auth(token)});
export const fetchProduct=(token:string,code:string)=>request<Omit<Product,'quantity'>>(`/api/products/${encodeURIComponent(code)}`,{headers:auth(token)});
const purchaseBody=(memberId:string|null,items:Product[])=>({member_id:memberId,items:items.map(({product_code,quantity})=>({product_code,quantity}))});
export const quotePurchase=(token:string,memberId:string|null,items:Product[])=>request<PurchaseQuote>('/api/purchases/quote',{method:'POST',headers:{'Content-Type':'application/json',...auth(token)},body:JSON.stringify(purchaseBody(memberId,items))});
export const createPurchase=(token:string,memberId:string|null,items:Product[],requestId:string,expectedGrandTotal:number)=>request<PurchaseResult>('/api/purchases',{method:'POST',headers:{'Content-Type':'application/json',...auth(token)},body:JSON.stringify({...purchaseBody(memberId,items),request_id:requestId,expected_grand_total:expectedGrandTotal})});
export const fetchTransactions=(token:string,page=0)=>request<Transaction[]>(`/api/transactions?page=${page}`,{headers:auth(token)});
