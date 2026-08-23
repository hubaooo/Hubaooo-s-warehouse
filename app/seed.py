from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import AssemblyConnection, Category, DisassemblyStep, Part, Product

INTERNAL_VIEW = "https://support.apple.com/en-us/104901"
ORDERABLE_PARTS = "https://support.apple.com/en-us/104902"
REPAIR_MANUAL = "https://support.apple.com/en-us/104900"
FIRST_STEPS = "https://support.apple.com/en-us/100300"


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
            summary=(
                "依据 Apple iPhone 15 维修手册与内部视图整理的教学型拆解数据。"
                "3D 几何模型为独立重建，不代表 Apple 官方 CAD 数据。"
            ),
            is_published=True,
        )
        db.add(iphone)
        db.flush()

        part_specs = [
            ("显示屏", "display", "Display", "外壳与显示组件", "z", 5, ORDERABLE_PARTS),
            ("显示屏粘合剂", "display-adhesive", "Display adhesive", "连接件", "z", 4, INTERNAL_VIEW),
            ("后玻璃", "back-glass", "Back glass", "外壳与显示组件", "-z", 5, ORDERABLE_PARTS),
            ("后玻璃粘合剂", "back-glass-adhesive", "Back glass adhesive", "连接件", "-z", 4, INTERNAL_VIEW),
            ("电池", "battery", "Battery", "内部组件", "z", 3, ORDERABLE_PARTS),
            ("主板", "logic-board", "Logic board", "核心部件", "z", 3, INTERNAL_VIEW),
            ("摄像头", "camera", "Camera", "核心部件", "z", 4, ORDERABLE_PARTS),
            ("原深感摄像头", "truedepth-camera", "TrueDepth camera", "核心部件", "z", 4, ORDERABLE_PARTS),
            ("顶部扬声器", "top-speaker", "Top speaker", "内部组件", "z", 3, ORDERABLE_PARTS),
            ("底部扬声器", "bottom-speaker", "Bottom speaker", "内部组件", "z", 3, ORDERABLE_PARTS),
            ("触感引擎", "taptic-engine", "Taptic Engine", "内部组件", "z", 3, ORDERABLE_PARTS),
            ("主麦克风", "main-microphone", "Main microphone", "内部组件", "z", 3, ORDERABLE_PARTS),
            ("USB-C 接口", "usb-c-connector", "USB-C connector", "连接件", "-y", 3, ORDERABLE_PARTS),
            ("SIM 卡组件", "sim-assembly", "SIM assembly", "附属配件", "-x", 2, INTERNAL_VIEW),
            ("机壳", "enclosure", "Enclosure", "主结构", "z", 1, ORDERABLE_PARTS),
        ]
        parts: dict[str, Part] = {}
        for order, (name, slug, official_name, group, axis, level, source) in enumerate(
            part_specs, start=1
        ):
            direction = -1 if axis.startswith("-") else 1
            coordinate = axis[-1]
            positions = {
                "x": [direction * level * 0.55, 0, 0],
                "y": [0, direction * level * 0.55, 0],
                "z": [0, 0, direction * level * 0.55],
            }
            part = Part(
                product_id=iphone.id,
                name=name,
                slug=slug,
                official_name=official_name,
                source_url=source,
                verification_status="apple-verified-name",
                description=f"Apple iPhone 15 维修资料中标示的 {official_name}。",
                exploded_transform={
                    "position": positions[coordinate],
                    "rotation": [0, 0, 0],
                    "scale": [1, 1, 1],
                },
                explosion_axis=axis,
                explosion_level=level,
                display_group=group,
                sort_order=order,
            )
            parts[slug] = part
            db.add(part)
        db.flush()

        steps = [
            (1, None, "安全准备", "备份设备、完全放电、关机并准备防静电工作区。", "防静电腕带和防静电垫", "受损或带电的锂离子电池可能造成火灾或人身伤害。", FIRST_STEPS),
            (2, "sim-assembly", "取出 SIM 卡托", "先取出 SIM 卡托，为后续拆卸做好准备。", "SIM 卡针", None, REPAIR_MANUAL),
            (3, "display", "释放并移除显示屏", "按 Apple 显示屏维修流程软化粘合剂、释放边缘并断开排线。", "加热式显示屏拆卸夹具与粘合剂切割工具", "破裂玻璃可能造成割伤；操作前佩戴防护眼镜和防割手套。", REPAIR_MANUAL),
            (4, "battery", "断开电池", "打开设备后优先断开电池排线，再处理其他内部连接。", "防静电镊子与指定螺丝刀", "不得刺穿、挤压或弯折电池。", REPAIR_MANUAL),
            (5, "back-glass", "移除后玻璃", "按后玻璃维修流程释放粘合剂并断开后玻璃连接。", "后玻璃拆卸夹具与粘合剂切割工具", "检查后玻璃和电池是否损坏。", REPAIR_MANUAL),
            (6, "camera", "移除摄像头", "拆下护盖、断开摄像头排线并垂直取出摄像头组件。", "指定扭矩螺丝刀与防静电镊子", None, REPAIR_MANUAL),
            (7, "truedepth-camera", "移除原深感摄像头", "拆下对应护盖并按维修手册断开原深感摄像头。", "指定扭矩螺丝刀与防静电镊子", "避免触碰镜头及排线触点。", REPAIR_MANUAL),
            (8, "top-speaker", "移除顶部扬声器", "解除固定件后取出顶部扬声器。", "指定扭矩螺丝刀", None, REPAIR_MANUAL),
            (9, "taptic-engine", "移除触感引擎", "断开连接并解除固定件后取出触感引擎。", "指定扭矩螺丝刀", None, REPAIR_MANUAL),
            (10, "bottom-speaker", "移除底部扬声器", "解除固定件后取出底部扬声器。", "指定扭矩螺丝刀", None, REPAIR_MANUAL),
            (11, "main-microphone", "移除主麦克风", "断开连接并按维修手册取出主麦克风组件。", "指定扭矩螺丝刀与防静电镊子", None, REPAIR_MANUAL),
            (12, "usb-c-connector", "移除 USB-C 接口", "解除相关固定件与连接后取出 USB-C 接口组件。", "指定扭矩螺丝刀与防静电镊子", None, REPAIR_MANUAL),
            (13, "battery", "移除电池", "按电池维修流程拉出粘合胶条并取出电池。", "电池压辊与防静电镊子", "仅在电池完全放电且无损伤时继续。", REPAIR_MANUAL),
        ]
        for order, slug, title, instruction, tool, safety, source in steps:
            db.add(
                DisassemblyStep(
                    product_id=iphone.id,
                    target_part_id=parts[slug].id if slug else None,
                    step_order=order,
                    title=title,
                    instruction=instruction,
                    tool=tool,
                    safety_notice=safety,
                    source_url=source,
                    verification_status="apple-manual-derived",
                )
            )

        attached = ["battery", "logic-board", "camera", "taptic-engine", "display"]
        for order, slug in enumerate(attached, start=1):
            db.add(
                AssemblyConnection(
                    product_id=iphone.id,
                    source_part_id=parts[slug].id,
                    target_part_id=parts["enclosure"].id,
                    connection_type="attach",
                    instruction=f"将{parts[slug].name}与机壳中的对应安装位置对齐。",
                    step_order=order,
                )
            )

        db.commit()
        print("权威示例数据导入完成：http://127.0.0.1:8000/api/v1/products/iphone-15")


if __name__ == "__main__":
    seed()
