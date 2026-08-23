from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import AssemblyConnection, Category, Part, Product


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(Category.id).limit(1)) is not None:
            print("数据库已有数据，跳过示例数据导入。")
            return

        digital = Category(name="数码设备", slug="digital-devices", description="手机、相机、电脑和平板")
        watches = Category(name="钟表", slug="watches", description="电子手表与机械手表")
        cars = Category(name="汽车", slug="cars", description="轿车、SUV 与赛车")
        db.add_all([digital, watches, cars])
        db.flush()

        iphone = Product(
            category_id=digital.id,
            name="iPhone 15",
            slug="iphone-15",
            brand="Apple",
            summary="用于验证产品拆解、零件讲解和虚拟组装流程的首个代表产品。",
            is_published=True,
        )
        db.add(iphone)
        db.flush()

        screen = Part(
            product_id=iphone.id,
            name="显示屏总成",
            slug="display-assembly",
            description="负责显示画面并接收触控输入。",
            working_principle="OLED 像素自发光，触控层感知手指位置。",
            sort_order=1,
        )
        battery = Part(
            product_id=iphone.id,
            name="电池",
            slug="battery",
            description="为整机提供电能。",
            working_principle="锂离子在正负极之间移动，实现充电与放电。",
            sort_order=2,
        )
        frame = Part(
            product_id=iphone.id,
            name="中框",
            slug="mid-frame",
            description="固定内部零件并提供结构强度。",
            material="铝合金",
            sort_order=3,
        )
        db.add_all([screen, battery, frame])
        db.flush()
        db.add_all(
            [
                AssemblyConnection(
                    product_id=iphone.id,
                    source_part_id=battery.id,
                    target_part_id=frame.id,
                    connection_type="place",
                    instruction="先将电池放入中框定位区域。",
                    step_order=1,
                ),
                AssemblyConnection(
                    product_id=iphone.id,
                    source_part_id=screen.id,
                    target_part_id=frame.id,
                    connection_type="attach",
                    instruction="连接排线后，将屏幕总成与中框对齐。",
                    step_order=2,
                ),
            ]
        )
        db.commit()
        print("示例数据导入完成：http://127.0.0.1:8000/api/v1/products/iphone-15")


if __name__ == "__main__":
    seed()
