from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal
from uuid import UUID, uuid4

from app.services.expense_split_helper import calculate_split_amounts


SplitType = Literal["EQUAL", "EXACT"]


@dataclass(frozen=True)
class SplitItem:
    user_id: UUID
    split_amount: Decimal

# 生成n個UUID的輔助函數
def _ids(n: int) -> list[UUID]:
    return [uuid4() for _ in range(n)]

def test_equal_split_with_remainder() -> None:
    '''測試均分計算邏輯是否正確處理剩餘金額的分配'''
    user_ids = _ids(3)
    splits = [SplitItem(user_id=u, split_amount=Decimal("0.00")) for u in user_ids]
    result = calculate_split_amounts(Decimal("100.00"), "EQUAL", splits)

    assert result == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]


def test_equal_split_exact() -> None:
    '''測試均分計算邏輯是否正確處理精確分攤'''
    user_ids = _ids(4)
    splits = [SplitItem(user_id=u, split_amount=Decimal("0.00")) for u in user_ids]
    result = calculate_split_amounts(Decimal("80.00"), "EQUAL", splits)

    assert result == [Decimal("20.00"), Decimal("20.00"), Decimal("20.00"), Decimal("20.00")]


def test_exact_split_success() -> None:
    '''測試指定金額分攤的成功情況'''
    user_ids = _ids(2)
    splits = [
        SplitItem(user_id=user_ids[0], split_amount=Decimal("10.00")),
        SplitItem(user_id=user_ids[1], split_amount=Decimal("15.00")),
    ]
    result = calculate_split_amounts(Decimal("25.00"), "EXACT", splits)

    assert result == [Decimal("10.00"), Decimal("15.00")]


def test_exact_split_sum_mismatch() -> None:
    '''測試指定金額分攤的總和與原始金額不匹配的情況'''
    user_ids = _ids(2)
    splits = [
        SplitItem(user_id=user_ids[0], split_amount=Decimal("10.00")),
        SplitItem(user_id=user_ids[1], split_amount=Decimal("10.00")),
    ]

    try:
        calculate_split_amounts(Decimal("25.00"), "EXACT", splits)
        raise AssertionError("expected ValueError for sum mismatch")
    except ValueError as exc:
        assert str(exc) == "split sum must equal amount"


def run_all() -> None:
    test_equal_split_with_remainder()
    test_equal_split_exact()
    test_exact_split_success()
    test_exact_split_sum_mismatch()
    print("All pure-logic split tests passed.")


if __name__ == "__main__":
    run_all()
