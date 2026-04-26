from __future__ import annotations

from decimal import Decimal, ROUND_DOWN
from typing import Iterable, Protocol


class SplitLike(Protocol):
    split_amount: Decimal


def calculate_split_amounts(
    amount: Decimal,
    split_type: str,
    splits: Iterable[SplitLike],
) -> list[Decimal]:
    split_list = list(splits)
    if not split_list:
        raise ValueError("splits must not be empty")

    normalized_amount = amount.quantize(Decimal("0.01"))

    if split_type == "EQUAL":
        '''
        均分計算邏輯:
        1. 先將總金額除以分攤人數 得到基礎分攤金額（向下取整到小數點後兩位）
        2. 計算剩餘金額（總金額 - 基礎分攤金額 * 分攤人數）
        3. 將剩餘金額以0.01的單位分配給前幾個分攤人 直到剩餘金額分配完畢
        這樣可以確保分攤金額的總和等於原始金額 同時盡量平均分配剩餘金額
        '''
        count = len(split_list)
        base = (normalized_amount / count).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        remainder = normalized_amount - (base * count)
        extra_cents = int((remainder * Decimal("100")).to_integral_value())

        split_amounts = [base for _ in range(count)]
        for index in range(extra_cents):
            split_amounts[index] += Decimal("0.01")
    elif split_type == "EXACT":
        split_amounts = [split.split_amount.quantize(Decimal("0.01")) for split in split_list]
    else:
        raise ValueError(f"unsupported split_type: {split_type}")

    if sum(split_amounts) != normalized_amount:
        raise ValueError("split sum must equal amount")

    return split_amounts
