from typing import List
from decimal import Decimal
from app.schemas.balance import UserBalanceResponse, SettlementSuggestion

def simplify_debts(balances: List[UserBalanceResponse])-> List[SettlementSuggestion]:
    """
    商業邏輯: 根據每個成員的帳務結算餘額，計算出一組最簡化的債務清償建議
    目標: 最小化交易次數和金額 
    方法:
        1. 分離角色: 債務人 (net_balance < 0) 和債權人 (net_balance > 0) 以及排除餘額為零的成員
        2. 排序: 將債務人及債權人都以大到小排序(絕對值) 優先處理金額較大的交易
        3. 使用雙指針法: 一個指向債務人列表的開始(最大債務) 另一個指向債權人列表的開始(最大債權)
        4. 迭代過程:
            - 計算當前債務人和債權人之間的交易金額 (取兩者絕對值的最小值) 作為建議的交易金額
            - 生成一筆SettlementSuggestion 包含債務人ID 債權人ID 和建議的交易金額
            - 更新債務人和債權人的餘額(減去建議的交易金額)
            - 根據更新後的餘額調整指針位置 (如果債務人或債權人已經清償完畢 則移動到下一個)
    """
    # 1. 分離角色: 分離債務人和債權人 排除餘額為零的成員
    debtors = []  # balance < 0 (應付款)
    creditors = []  # balance > 0 (應收款)
    
    for balance_item in balances:
        if balance_item.balance < 0:
            debtors.append({
                'user_id': balance_item.user_id,
                'user_name': balance_item.user_name,
                'balance': balance_item.balance  # 負數
            })
        elif balance_item.balance > 0:
            creditors.append({
                'user_id': balance_item.user_id,
                'user_name': balance_item.user_name,
                'balance': balance_item.balance  # 正數
            })
    
    # 2. 排序: 按絕對值從大到小排序
    # 債務人: 越小的在前 (sort ascending, 因為負數)
    debtors.sort(key=lambda x: x['balance'])
    # 債權人: 越大的在前 (sort descending)
    creditors.sort(key=lambda x: x['balance'], reverse=True)
    
    # 3. 使用雙指針法計算建議的交易金額
    settlements = []
    i = 0  # 債務人指針
    j = 0  # 債權人指針
    
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        
        # 計算交易金額 (取絕對值的最小值)
        debt_amount = abs(debtor['balance'])  # 債務人欠款金額
        credit_amount = creditor['balance']   # 債權人應收金額
        
        amount = min(debt_amount, credit_amount)
        
        # 生成一筆 SettlementSuggestion
        settlement = SettlementSuggestion(
            from_user_id=debtor['user_id'],
            from_user_name=debtor['user_name'],
            to_user_id=creditor['user_id'],
            to_user_name=creditor['user_name'],
            amount=Decimal(str(amount))
        )
        settlements.append(settlement)
        
        # 更新債務人和債權人的餘額
        debtor['balance'] += amount  # 負數變小 (更接近0)
        creditor['balance'] -= amount  # 正數變小 (更接近0)
        
        # 調整指針位置 (如果已經清償完畢則移動到下一個)
        if abs(debtor['balance']) < Decimal('0.01'):  # 近似為零
            i += 1
        if abs(creditor['balance']) < Decimal('0.01'):  # 近似為零
            j += 1
    
    return settlements