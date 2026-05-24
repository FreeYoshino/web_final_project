import hashlib
import hmac
import secrets

class PasswordService:
    """
    密碼處理服務類別
    採用 PBKDF2-HMAC-SHA256 演算法進行密碼雜湊與驗證。
    """
    
    _ALGORITHM = "pbkdf2_sha256"
    _ITERATIONS = 100_000
    _SALT_BYTES = 16    # salt 的位元組長度 16 bytes = 128 bits

    @staticmethod
    def hash_password(password: str) -> str:
        """將明文密碼轉換為安全的雜湊字串"""
        
        # 1. 產生隨機鹽值
        salt = secrets.token_hex(PasswordService._SALT_BYTES)
        
        # 2. 執行 PBKDF2 密碼雜湊演算法
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",                      # 使用的雜湊函數
            password.encode("utf-8"),      # 將字串轉為位元組 (bytes)
            salt.encode("utf-8"),          # 鹽值也需轉為位元組
            PasswordService._ITERATIONS,   # 執行 10 萬次計算
        ).hex()                            # 轉回 16 進位字串方便儲存
        
        # 3. 組合並返回最終字串 
        # 格式：演算法$迭代次數$鹽值$雜湊值
        return f"{PasswordService._ALGORITHM}${PasswordService._ITERATIONS}${salt}${password_hash}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """驗證使用者輸入的明文密碼是否與資料庫儲存的雜湊值吻合"""
        try:
            # 1. 解析資料庫中儲存的格式
            algorithm, iterations_str, salt, expected_hash = hashed_password.split("$", 3)
            
            # 2. 演算法防禦：如果資料庫的密碼不是用此演算法生成的，直接拒絕。
            if algorithm != PasswordService._ALGORITHM:
                return False

            # 3. 取出當初這組密碼使用的迭代次數
            iterations = int(iterations_str)
            
            # 4. 用「使用者輸入的密碼」加上「當初的鹽值」與「當初的迭代次數」，重新計算一次雜湊
            actual_hash = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                iterations,
            ).hex()
            
            # 5. 比對結果 
            # 使用 hmac.compare_digest 進行安全的字串比對 防止時序攻擊
            return hmac.compare_digest(actual_hash, expected_hash)
            
        except (ValueError, TypeError):
            return False