from getpass import getpass

from sqlalchemy import select

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Admin


def main() -> None:
    Base.metadata.create_all(bind=engine)
    username = input("管理员用户名: ").strip()
    password = getpass("管理员密码（至少 10 位）: ")
    if not username or len(password) < 10:
        raise SystemExit("用户名不能为空，密码至少需要 10 位。")
    with SessionLocal() as db:
        if db.scalar(select(Admin).where(Admin.username == username)):
            raise SystemExit("该管理员用户名已存在。")
        db.add(Admin(username=username, password_hash=hash_password(password)))
        db.commit()
    print("管理员创建成功。")


if __name__ == "__main__":
    main()
