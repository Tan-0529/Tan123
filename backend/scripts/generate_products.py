import json
import re
import sys
import time
import urllib.request

from openai import OpenAI

sys.path.insert(0, ".")
from app.config import Settings  # noqa: E402

CATEGORIES = [
    "沙发", "床", "床垫", "餐桌", "餐椅", "书桌", "办公桌", "衣柜", "鞋柜", "电视柜",
    "茶几", "书架", "床头柜", "梳妆台", "儿童床",
    "落地灯", "吸顶灯", "台灯", "窗帘", "地毯", "挂画", "花洒", "水龙头", "马桶", "瓷砖",
    "空调", "冰箱", "洗衣机", "电视机", "热水器", "油烟机", "燃气灶", "消毒柜",
    "电饭煲", "微波炉", "空气炸锅", "破壁机", "咖啡机", "电水壶", "烤箱", "电磁炉", "豆浆机", "榨汁机",
    "吸尘器", "扫地机器人", "加湿器", "空气净化器", "电风扇", "挂烫机", "除湿机",
    "手机", "笔记本电脑", "平板电脑", "蓝牙耳机", "蓝牙音箱", "智能手表", "路由器", "充电宝",
    "显示器", "机械键盘", "鼠标", "移动硬盘", "摄像头",
    "T恤", "衬衫", "卫衣", "毛衣", "夹克", "羽绒服", "大衣", "牛仔裤", "休闲裤", "连衣裙",
    "半身裙", "内衣", "袜子",
    "运动鞋", "皮鞋", "靴子", "拖鞋", "凉鞋", "帆布鞋",
    "双肩包", "行李箱", "单肩包", "钱包", "手提包",
    "护肤套装", "口红", "香水", "面膜", "洗发水", "沐浴露", "电动牙刷", "剃须刀", "防晒霜", "粉底液",
    "零食", "茶叶", "咖啡豆", "坚果", "牛奶", "巧克力", "饼干", "方便面", "大米", "食用油", "蜂蜜", "红酒",
    "婴儿推车", "奶粉", "纸尿裤", "儿童玩具", "婴儿床", "奶瓶", "童装",
    "瑜伽垫", "跑步机", "帐篷", "登山包", "哑铃", "自行车", "羽毛球拍", "篮球", "泳衣", "滑板",
    "钢笔", "笔记本", "文件夹", "订书机", "白板", "计算器", "剪刀", "马克笔", "书包",
    "纸巾", "洗衣液", "垃圾袋", "收纳箱", "雨伞", "保温杯", "餐具", "锅具", "床上用品", "毛巾", "拖鞋", "衣架",
    "猫粮", "狗粮", "宠物玩具", "猫砂", "宠物窝",
    "行车记录仪", "车载充电器", "汽车坐垫", "汽车脚垫", "车载香水",
    "小说", "儿童绘本", "工具书",
]

BASE_URL = "http://127.0.0.1:8000"


def extract_json(text: str):
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(text)


def main():
    settings = Settings()
    client = OpenAI(base_url=settings.openai_base_url, api_key=settings.openai_api_key)

    total = 0
    batch_size = 10
    for i in range(0, len(CATEGORIES), batch_size):
        batch = CATEGORIES[i:i + batch_size]
        types = json.dumps(batch, ensure_ascii=False)
        prompt = (
            f"你是电商商品数据生成器。为以下每个品类各生成 1 个商品，使用真实知名品牌名，"
            f"直接输出 JSON 数组，不要额外文字。品类列表：{types}\n"
            f'每个元素字段：{{"type":"品类","title":"商品标题","content":"描述50字内",'
            f'"price":价格数字,"brand":"真实品牌名","image_keyword":"该商品英文图片搜索关键词",'
            f'"attributes":{{"参数":"值","参数2":"值2"}}}}'
        )
        try:
            resp = client.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
            )
            text = resp.choices[0].message.content or ""
            items = extract_json(text)
        except Exception as e:
            print(f"批次{i} 生成失败: {e}", flush=True)
            continue

        for item in items:
            total += 1
            sku = f"FULL{total:04d}"
            category = item.get("type", "其他")
            keyword = item.get("image_keyword", "").strip().replace(" ", "-") or category
            doc = {
                "doc_id": f"full_{time.time_ns()}_{total}",
                "source_type": "text",
                "title": item.get("title", category),
                "content": item.get("content", ""),
                "metadata": {
                    "price": float(item.get("price", 0)),
                    "rating": round(4.0 + (total % 10) * 0.1, 1),
                    "category": category,
                    "brand": item.get("brand", ""),
                    "sku": sku,
                    "image_url": f"https://loremflickr.com/300/200/{keyword}",
                    "product_url": f"https://example.com/p/{sku}",
                },
                "attributes": item.get("attributes", {}),
            }
            data = json.dumps(doc, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(
                f"{BASE_URL}/ingest", data=data,
                headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req)
        print(f"批次{i} 完成: {len(items)} 个 ({batch[0]}~{batch[-1]})", flush=True)

    print(f"总计生成 {total} 个商品", flush=True)


if __name__ == "__main__":
    main()
