from collections import OrderedDict

# ==============================================================================
#                               PART 0: EASY SIZE PRESETS
# ==============================================================================
PRESETS = OrderedDict([
    ("SD1.5", [
        ("512×512 (1:1)", (512, 512)), ("768×512 (3:2)", (768, 512)),
        ("512×768 (2:3)", (512, 768)), ("768×576 (4:3)", (768, 576)), ("576×768 (3:4)", (576, 768)),
    ]),
    ("SDXL", [
        ("1024×1024 (1:1)", (1024, 1024)), ("1152×896 (9:7)", (1152, 896)),
        ("896×1152 (7:9)", (896, 1152)), ("1344×768 (7:4)", (1344, 768)), ("768×1344 (4:7)", (768, 1344)),
        ("1216×832 (19:13)", (1216, 832)), ("832×1216 (13:19)", (832, 1216)), ("1280×768 (5:3)", (1280, 768)),
        ("768×1280 (3:5)", (768, 1280)), ("1536×640 (12:5)", (1536, 640)), ("640×1536 (5:12)", (640, 1536)),
        ("1600×640 (5:2)", (1600, 640)), ("640×1600 (2:5)", (640, 1600)),
    ]),
    ("FLUX", [
        ("1024×1024 (1:1)", (1024, 1024)), ("1920×1080 (16:9)", (1920, 1080)), ("1080×1920 (9:16)", (1080, 1920)),
        ("1536×640 (12:5)", (1536, 640)), ("640×1536 (5:12)", (640, 1536)), ("1600×1600 (1:1)", (1600, 1600)),
        ("1280×720 (16:9)", (1280, 720)), ("720×1280 (9:16)", (720, 1280)), ("1366×768 (16:9)", (1366, 768)),
        ("768×1366 (9:16)", (768, 1366)), ("2560×1440 (16:9)", (2560, 1440)),
    ]),
    ("WAN", [
        ("832×480 (16:9)", (832, 480)), ("480×832 (9:16)", (480, 832)), ("896×512 (7:4)", (896, 512)),
        ("512×896 (4:7)", (512, 896)), ("1280×720 (16:9)", (1280, 720)), ("720×1280 (9:16)", (720, 1280)),
        ("640×480 (4:3)", (640, 480)), ("960×720 (4:3)", (960, 720)), ("480×640 (3:4)", (480, 640)),
        ("720×960 (3:4)", (720, 960)), ("720×720 (1:1)", (720, 720)), ("480×480 (1:1)", (480, 480)),
        ("1024×576 (16:9)", (1024, 576)), ("576×1024 (9:16)", (576, 1024)),
    ]),
    ("QWEN", [
        ("1328×1328 (1:1)", (1328, 1328)), ("928×1664 (9:16)", (928, 1664)), ("1664×928 (16:9)", (1664, 928)),
        ("1104×1472 (3:4)", (1104, 1472)), ("1472×1104 (4:3)", (1472, 1104)), ("1056×1584 (2:3)", (1056, 1584)),
        ("1584×1056 (3:2)", (1584, 1056)),
    ])
])

CROP_METHODS = ["中心裁剪", "直接缩放"]
RESIZE_ALGOS = ["lanczos", "bilinear", "nearest"]

def get_size_from_preset(choices: dict):
    for k, v in choices.items():
        if v != "关":
            for name, wh in PRESETS[k]:
                if name == v:
                    return wh
    return (512, 512)

# ==============================================================================
#                               PART 1: STYLE PRESETS (风格预设)
# ==============================================================================
# 三级联动字典： Model (一级) -> Category (二级) -> Style (三级) -> { positive, negative }
STYLE_PRESETS = {
    "Flux2": {
        "写实摄影": {
            "None": {
                "positive": "{$@}",
                "negative": "{$@}"
            },
            "手机抓拍纪实摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into android phone cam-quality，taking photographs exhibit {$spicy-content-with} surprising compositions, sharp complex backgrounds, natural lighting, and candid moments that feel immediate and authentic.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": (
                    "blurry, overexposed, digital, artificial, drawing, 3d"
                )
            },
            "随拍纪实照": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into low quality photos，taking photographs exhibit {$spicy-content-with} sharp backgrounds, unpolished realism with natural lighting, and candid friendship‑level moments that feel immediate and authentic.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "90年代傻瓜机闪光照": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into the early 1990s, taking photographs exhibit {$spicy-content-with} a rough, low-resolution quality, washed-out colors, including a harsh built-in flash, grainy texture, and overexposed highlights, capturing a casual atmosphere that evokes nostalgia.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "高反差硬光摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into an white light source to generate dramatic light and shadow，taking photographs exhibit {$spicy-content-with} high definition,whites with sharp dark shadows, and vibrant colors.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "影视剧照": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into a Hollywood high-budget film，taking photographs exhibit {$spicy-content-with} atmospheric composition that emphasize intense emotions using selective focus, and warm and cold colors with high quality studio lighting.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "经典宽银幕胶片剧照": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into iconic classic mid‑century cinema (1950s‑1960s Hollywood golden age)，taking photographs are on 35mm film with grain, displaying {$spicy-content-with} a warm color temperature, and an anamorphic lens that creates imperfections and blurry edges.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "黑色电影风格剧照": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into dark movies，taking photographs exhibit {$spicy-content-with} intense side lighting and gobo‑crafted patterns to sculpt deep, sharply defined shadows, along with a muted Ektachrome palette that evokes film noir.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "80年代怀旧生活随拍": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into 80s informal shots，taking photographs exhibit {$spicy-content-with} a minimalist, amateurish composition, warm desaturated tones and a soft focus that creates a cozy atmosphere.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "洛莫摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into lomographic lens，taking photographs exhibit {$spicy-content-with} film grain, colorful lens flares, soft focus with motion blur, and analog filter effects, trying to capture emotions.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "极简主义负空间摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into serene and tranquil images，taking photographs exhibit {$spicy-content-with} high contrast and clean, minimalist compositions that emphasize empty space to highlight negative space.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "光绘摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into light painting images with long exposures and LED sources，taking photographs exhibit {$spicy-content-with} luminous trails, vibrant colors, and elements that are strikingly illuminated by the long exposure.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "霓虹都市夜景": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into dark colorful neon light scenes，taking photographs exhibit {$spicy-content-with} dark cinematic environments illuminated only by neon lights that emphasize vibrant reds, greens, and blues, presenting emotional scenes with saturated colors.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "胶片纪实": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your analog photographs show {$spicy-content-with} captivating elements and dark backgrounds suggesting an intimate, dimly lit indoor environment. The overall impression is one of introspection and raw authenticity.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            }
        },
        "艺术风格": {
            "None": {
                "positive": "{$@}",
                "negative": "{$@}"
            },
            "吉卜力风": {
                "positive": "Transform the images into epic hand-drawn Japanese animation including {$spicy-content-with} warm artwork from Studio Ghibli. This shot features: {$@}",
                "negative": "3d render, photorealistic, photography"
            },
            "美式漫画": {
                "positive": (
                    "Transform the images into illustration with comic book style and {$spicy-content-with} intense colors. Action scene featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "意式手绘漫画": {
                "positive": (
                    "Transform the images into hand-drawn Italian comic book including {$spicy-content-with} bold colors and sinuous lines, featuring realistic characters in hypersaturated imagery with high-contrast ballpoint hatching and intricate cross-hatch patterns. A seamless complete full page illustration using red, green and blue. Featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "复古漫画": {
                "positive": (
                    "Transform the images into an old sheet of paper with a vintage comic strip from 1950, painted in white, red, blue and black including {$spicy-content-with} freehand outlines. A detailed and dirty image featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "波普艺术": {
                "positive": (
                    "Transform the images into Pop Art style characterized by {$spicy-content-with} bold, vibrant colors, and thick black outlines defining each form with clarity and contrast. The surface is executed using a pointillist technique, where dots of color come together to create the overall picture. Dazzling patterns and comic style characters {$with-adult-content}. The scene has a flat, two-dimensional appearance typical of pop art aesthetics, featuring {$@}"
                ),
                "negative": "{$@}"
            },
            "日本动画": {
                "positive": (
                    "Transform the images into classic Japanese anime style with clean lines and expressive facial expressions. The artwork uses dynamic lighting and soft shadows to highlight the central figure: {$@}, including {$spicy-content-with}."
                ),
                "negative": "{$@}"
            },
            "日式漫画": {
                "positive": (
                    "Transform the images into black and white manga-style illustration that includes {$spicy-content-with} a violent atmosphere. The illustration features: {$@}."
                ),
                "negative": "{$@}"
            },
            "暗黑恐怖漫画": {
                "positive": (
                    "Transform the images into illustration that includes {$spicy-content-with} stippling textures and intense side lighting with deep shadows; dark low key illumination with high contrast and minimal highlights; cinematic chiaroscuro; horror graphic novel with dynamic composition, featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "淡彩素描": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into a minimalist style, combining delicate pencil sketches with soft watercolor washes. They exhibit {$spicy-content-with} large areas of untouched white space, creating a sense of airiness and simplicity. The pencil lines are light and expressive, while the watercolor washes are subtle and translucent, often blending into the white space. The overall effect is ethereal and contemplative.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "墨线写实": {
                "positive": (
                    "Transform the images into a realistically rendered ink drawing featuring {$spicy-content-with} fine cross-hatching and stippling techniques. These methods create deep shadows and highlights using a monochromatic color scheme. The image includes large areas of white space and high contrast due to varying line densities. Featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "手绘插画": {
                "positive": (
                    "Transform the images into a realistically rendered concept-art done in ink that includes {$spicy-content-with} large white areas and high contrast thanks to the varying density of the lines. It's like a very sharp photograph, but drawn. This colorful concept-art features: {$@}"
                ),
                "negative": "{$@}"
            },
            "数字插画": {
                "positive": (
                    "Transform the images into a detailed illustration in stylized line art featuring {$spicy-content-with} vector graphics aesthetics. With black solid shadows and big negative space creating enigmatic stillness. Saturated highlights with glowing accents, emphasizing contrasts between obscurity and luminous for a vivid impact. Featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "矢量插画": {
                "positive": (
                    "Transform the images into a stylized digital illustration featuring {$spicy-content-with} iconography style. The illustration has a graphic design aesthetic, including flat, solid colors, no defined outlines, and a minimalist approach to composition. Featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "怀旧像素艺术": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into a low-resolution pixel art style, reminiscent of 16-bit era video games. It exhibits {$spicy-content-with} bold, vibrant colors and a limited color palette. Details are simplified and blocky, emphasizing shape and form over realism. The overall aesthetic is retro and nostalgic, with a focus on strong visual impact despite the low pixel count.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "油画": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are a painter.Transform the images into canvas is painted with impasto; the brushstrokes are thick and visible, and the heavy texture of the impasto is very pronounced. The composition is minimalist with large areas of the same color.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "日本热血动漫": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into high-quality anime artwork, exhibiting {$spicy-content-with} dynamic action poses, vibrant colors, and detailed backgrounds. Character designs are expressive and feature sharp lines, intricate shading, and visible energy effects (like speed lines or glowing auras). The style is inspired by modern action anime.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "怀旧手绘漫画": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into 1950s comics，the worn sheet of paper contains {$spicy-content-with} a vintage 1950s comic book illustration made with hand-drawn lines painted in white, red, blue, and black.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "手绘美漫": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into comics.the drawing is a detailed, full-color comic book cover featuring {$spicy-content-with} hatching and hand-drawn curved lines, depicting an intense and violent scene of the highest quality.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            }
        },
        "趣味风格": {
            "None": {
                "positive": "{$@}",
                "negative": "{$@}"
            },
            "办公桌手办": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "补全角色主体的躯体，保持姿势和面部特征不变，将主体变成一个写实的全身角色手办，在手办的后面，有一个比手办大的设计精美的二次元手办包装盒，包装盒上写着精美设计的\"limited\"艺术字，包装右下角有正方形的红色标签，红色标签上写着\"2026\"，\"WAN\"和\"DAI\"各占标签的一行，包装盒上印着图片形象,在包装盒后面还有一个MAC牌子的电脑屏幕，屏幕上显示着3d建模软件中手办的灰色3d模型，手办被摆放在一个半透明的展示盘上，强调手办的pvc塑料质感，场景在一个手办生产工作室内，后面有3d打印机.{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "工作室手持手办": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "补全角色主体的躯体，保持姿势和面部特征不变，将主体变成一个写实的全身角色手办，手办被拿在一只真实的手里把玩，强调手办的pvc塑料质感，场景在一个手办生产工作室内.{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "漫展展位手办": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "补全角色主体的躯体，保持姿势和面部特征不变，将主体变成一个写实的全身角色手办，手办被放置在漫展摊位上进行售卖，后面有正在售卖的工作人员的身体.{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "魔法法阵手办": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "补全角色主体的躯体，保持姿势和面部特征不变，将主体变成一个写实的全身角色手办，手办置于会发光的魔法法阵中央，法阵浮现半透明光线和神秘符文，手办表面带有逼真PVC光泽，法阵散发蓝色和金色光芒在手办上投射动态光影，背景是古老手办工作室与奇幻元素结合的场景，桌面上散落着模型工具和魔法书籍，整体画面呈现幻想实验室的神秘氛围。{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "高科技展厅手办": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "补全角色主体的躯体，保持姿势和面部特征不变，将主体变成一个写实的全身角色手办，手办被置于未来感浮空展示架上，周围漂浮着微型全息屏幕显示手办设计信息，光线从架顶射下形成逼真阴影，PVC表面细节清晰，背景是高科技手办展览厅，氛围冷色调科技感十足，同时有微型机械臂在旁辅助整理手办道具。{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "书桌手办": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "补全角色主体的躯体，保持姿势和面部特征不变，将主体变成一个写实的全身角色手办，手办被放置在木质收藏架上，架上还陈列着其他动漫角色手办与奖杯，背景是温馨的日式房间，窗外透入午后阳光，在PVC表面形成柔和高光，书桌上散落着包装盒、说明书和一把小刷子，整体氛围宁静而充满收藏热爱。{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "玻璃罩内手办": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "补全角色主体的躯体，保持姿势和面部特征不变，将主体变成一个写实的全身角色手办，手办置于玻璃防尘罩内，罩底为旋转展示台缓慢转动，背景是高端手办专卖店橱窗，夜晚灯光璀璨，橱窗外有行人驻足观看，店内暖色射灯精准打光，凸显手办面部表情与衣物质感，反射在玻璃上形成细腻倒影。{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "工作台手办": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "补全角色主体的躯体，保持姿势和面部特征不变，将主体变成一个写实的全身角色手办，手办被摆放在复古蒸汽朋克风格工作台上，台面布满齿轮、铜管、黄铜量尺与未完成的手办零件，背景墙上挂着设计草图与泛黄照片，一盏可调节机械臂台灯从斜上方投下暖黄聚光，PVC手办在金属环境中显得格外精致而现代。{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "手办开箱": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "补全角色主体的躯体，保持姿势和面部特征不变，将主体变成一个写实的全身角色手办，手办正被放入定制泡沫内衬的黑色运输箱中，箱盖半开，露出印有\"FRAGILE\"字样的标签，背景是物流打包区，纸箱堆叠，胶带卷散落，一束顶光从仓库天窗洒下照亮手办，强调其即将启程交付的仪式感与珍贵性。{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "贩卖机内手办": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "补全角色主体的躯体，保持姿势和面部特征不变，将主体变成一个写实的全身角色手办，手办被置于雨夜街头的自动贩卖机内，机器内部LED灯照亮手办全身，玻璃外壁沾有雨水水珠，模糊反射城市霓虹灯光，背景是湿润的柏油路与模糊车灯，营造出赛博都市中孤独而闪耀的收藏品意象，PVC材质在潮湿环境中反光细腻。{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "微观玩具摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Transform the images into tilt‑shift lenses to turn real‑world scenes into miniature toy models,taking photographs exhibit {$spicy-content-with} crisp, high‑resolution details captured in an exaggerated perspective, with a very narrow focus plane, and a dreamy, toy‑like atmosphere that creates the classic “miniature” illusion.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "亚克力角色立牌": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "将平面人物变换为人物立牌；立牌的镀金边框镶嵌着半透明水晶，将整体包裹在柔和的光晕中；桌面采用仿古木纹质感，表面覆盖着薄如蝉翼的银质光泽，在魔法能量的映照下呈现出微波荡漾的特效。桌布选用半透明的蕾丝材质，边缘缀有细小的星砂，随着魔法阵的能量波动会泛起微弱的蓝紫色光晕；魔法阵以立体的星砂构成，悬浮在桌面中央的水晶球中投射出流动的星河，星光在桌面的银质光泽中折射出细碎的光点；水晶球下方放置着三枚悬浮的魔法符文，符文表面不断流转着淡金色的纹路，与桌面的银光形成微妙的色彩呼应；立牌位于现实场景的装点桌面中。{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "钥匙扣": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "将原图中的人物全身立绘图像替换为一个透明亚克力材质的人物挂件，穿着与原图相似的服饰，但体型更小、风格更卡通化；在挂件上方添加两个金属钥匙圈，其中一个钥匙圈连接着一个透明亚克力材质的购物袋形状挂件；在钥匙圈连接处添加一个橙色粗条形标签；将原图中人物的背景替换为黑色竖条纹的塑料包装卡，包装卡顶部有挂孔；保留原图中人物的服饰细节、颜色和装饰元素，但以缩小、简化和卡通化的方式呈现；保持原图中人物的姿势和朝向不变，但挂件整体呈悬挂状态，与钥匙圈相连；保持原图中人物的配色不变，但整体视觉风格从写实变为Q版卡通风格。{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "伯爵徽章": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "将原图人物变成圆形吧唧；将原图中人物的姿势调整为正面半身像，头部略微倾斜，表情变为严肃凝视；原图中人物的蓝色衣帽替换为黑色英伦风衣帽；原图中的细节被简化，仅保留部分装饰性元素；吧唧背景由纯白色改为圆形构图，背景填充为黑色与白色交织的几何光效图案。 {$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "化妆品包装": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "将原图人物变成面霜商品；将上一个图片中的人物形象，转换为贴附在高级面霜身上的插画图案，图案为粉色高级浮雕形式呈现为半身姿态，背景有花卉纹样；在面霜的顶部添加一条白金色链条，链条末端悬挂一个银色玫瑰花吊坠，吊坠内有花纹；在中部添加一个粉色标签，标签上印有一个蝴蝶结图案；将原图中人物的背景从纯白改为粉白色高级浮雕渐变背景；在面霜周围布置粉色与白色的花朵装饰，花朵置于管体两侧，部分花瓣带有透明质感；使整个画面呈现于一个具有镜面反射效果的平面上，反射出管体和花朵的倒影。{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "金属徽章": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "将上一个图片中的人物形象进行金属风格化简化，将其转化为一个以太阳系和星际元素构成的徽章造型；人物的头发和装饰性制服被抽象为镂空多边形，整体呈椭圆形框架结构；原人物的面部特征被压缩并置于徽章中心，保留基本轮廓和发色，但去除了细节表情；在徽章底部添加了风格化的文字，文字为日文\"愛しい人\"，字体呈粗体且带有棱角，与整体设计风格统一；原图中人物的服装和装饰被简化为与背景同色系的几何色块，不再呈现具体纹理或层次；原图的纯白背景被保留，但整体构图从人物半身像转变为挂件式徽章；顶部添加了一个银色金属质感的钥匙扣和链条结构，使其具备实用挂件功能；整体挂件有金属质感而立体，在观察中反光。{$spicy-content-with}\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            }
        },
        "镜头": {
            "None": {
                "positive": "{$@}",
                "negative": "{$@}"
            },
            "广角全景图": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Change the viewing angle of the picture to a panoramic scene captured from a distance.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "广角 / 猫眼": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your peephole shows {$spicy-content-with} a shot from a high angle, inside a fisheye lens distortion glass circle, highly distorted with a wide angle.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
        }
    },
    "Z-image": {
        "写实摄影": {
            "None": {
                "positive": "{$@}",
                "negative": "{$@}"
            },
            "手机抓拍纪实摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your photographs has android phone cam-quality.\n"
                    "Your photographs exhibit {$spicy-content-with} surprising compositions, sharp complex backgrounds, natural lighting, and candid moments that feel immediate and authentic.\n"
                    "Your photographs are actual gritty candid photographic background.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "随拍纪实照": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are an amateur documentary photographer taking low quality photos.\n"
                    "Your photographs exhibit {$spicy-content-with} sharp backgrounds, unpolished realism with natural lighting, and candid friendship‑level moments that feel immediate and authentic.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "90年代傻瓜机闪光照": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are an amateur photographer, taking photos with point‑and‑shoot cam-quality, in the early 1990s.\n"
                    "Your photographs exhibit {$spicy-content-with} a rough, low-resolution quality, washed-out colors, including a harsh built-in flash, grainy texture, and overexposed highlights, capturing a casual atmosphere that evokes nostalgia.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "高反差硬光摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are a photographer who loves using an intense white light source to generate dramatic light and shadow.\n"
                    "Your photographs exhibit {$spicy-content-with} high definition, brilliant glowing whites with sharp dark shadows, and vibrant colors.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "影视剧照": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are a Hollywood filmmaker making a high-budget film.\n"
                    "Your photographs exhibit {$spicy-content-with} atmospheric composition that emphasize intense emotions using selective focus, and warm and cold colors with high quality studio lighting.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "经典宽银幕胶片剧照": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are a professional cinematographer of iconic classic mid‑century cinema (1950s‑1960s Hollywood golden age).\n"
                    "Your photographs are on 35mm film with grain, displaying {$spicy-content-with} a warm color temperature, and an anamorphic lens that creates imperfections and blurry edges.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "黑色电影风格剧照": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are a cinematographer who works in dark movies.\n"
                    "Your photographs exhibit {$spicy-content-with} intense side lighting and gobo‑crafted patterns to sculpt deep, sharply defined shadows, along with a muted Ektachrome palette that evokes film noir.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "80年代怀旧生活随拍": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are an 80s photographer who enjoys informal shots.\n"
                    "Your worn vintage photographs exhibit {$spicy-content-with} a minimalist, amateurish composition, warm desaturated tones and a soft focus that creates a cozy atmosphere.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "洛莫摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are an adventurous experimental photographer exploring the world through a lomographic lens.\n"
                    "Your photographs exhibit {$spicy-content-with} film grain, colorful lens flares, soft focus with motion blur, and analog filter effects, trying to capture emotions.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "航拍广角全景图": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are an aerial photographer who enjoys using wide-angle drone cams.\n"
                    "Your photographs exhibit {$spicy-content-with} panoramic scenes captured from afar, high up with elevated perspectives and intense colors.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "极简主义负空间摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are a photographer who prefers serene and tranquil images.\n"
                    "Your photographs exhibit {$spicy-content-with} high contrast and clean, minimalist compositions that emphasize empty space to highlight negative space.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "波普艺术风格影像": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are a contemporary pop artist known for your vibrant, oversaturated palettes and energetic, graphic compositions.\n"
                    "Your photographs exhibit {$spicy-content-with} exaggerated colors and solid backgrounds using Ben-Day dots, achieving an unconventional and clearly pop art effect.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "光绘摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are an experimental photographer who enjoys creating light painting images with long exposures and LED sources.\n"
                    "Your photographs exhibit {$spicy-content-with} luminous trails, vibrant colors, and elements that are strikingly illuminated by the long exposure.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "霓虹都市夜景": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are a photographer who likes dark colorful neon light scenes.\n"
                    "Your photographs exhibit {$spicy-content-with} dark cinematic environments illuminated only by neon lights that emphasize vibrant reds, greens, and blues, presenting emotional scenes with saturated colors.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "胶片纪实": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your analog photographs show {$spicy-content-with} captivating elements and dark backgrounds suggesting an intimate, dimly lit indoor environment. The overall impression is one of introspection and raw authenticity.\n"
                    "---\n"
                    "YOUR ANALOG PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "胶片摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your analog photographs show {$spicy-content-with} a diagonal shot where the image is grainy and underexposed.\n"
                    "---\n"
                    "YOUR ANALOG PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "经典老电影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your cinematic shot from classic film exhibit {$spicy-content-with} deep black shadows and warm earth tones. The scene's composition is vintage, from the 1950s, and imbued with profound emotion.\n"
                    "---\n"
                    "THE CINEMATIC SHOT FROM CLASSIC FILM:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "复古抓拍照": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your photographs exhibit {$spicy-content-with} a gritty, candid vintage style from a disposable camera, dark shadows and vibrant warm colors\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "手机随拍": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your photographs has android phone cam-quality.\n"
                    "Your photographs exhibit {$spicy-content-with} a casual and amateur style using soft focus and vibrant colors.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "低保真手机摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your photographs has android phone cam-quality.\n"
                    "Your photographs exhibit {$spicy-content-with} real, documented moments that seem surprisingly authentic.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            }
        },
        "艺术风格": {
            "None": {
                "positive": "{$@}",
                "negative": "{$@}"
            },
            "美式漫画": {
                "positive": (
                    "Illustration with comic book style and {$spicy-content-with} intense colors. Action scene featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "意式手绘漫画": {
                "positive": (
                    "Hand-drawn Italian comic book including {$spicy-content-with} bold colors and sinuous lines, featuring realistic characters in hypersaturated imagery with high-contrast ballpoint hatching and intricate cross-hatch patterns. A seamless complete full page illustration using red, green and blue. \n"
                    "Featuring: {$@}\n"
                ),
                "negative": "{$@}"
            },
            "复古漫画": {
                "positive": (
                    "An old sheet of paper with a vintage comic strip from 1950, painted in white, red, blue and black including {$spicy-content-with} freehand outlines. A detailed and dirty image featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "波普艺术": {
                "positive": (
                    "Image in Pop Art style characterized by {$spicy-content-with} bold, vibrant colors, and thick black outlines defining each form with clarity and contrast. The surface is executed using a pointillist technique, where dots of color come together to create the overall picture. Dazzling patterns and comic style characters {$with-adult-content}. The scene has a flat, two-dimensional appearance typical of pop art aesthetics, featuring {$@}"
                ),
                "negative": "{$@}"
            },
            "吉卜力": {
                "positive": (
                    "Epic hand-drawn Japanese animation including {$spicy-content-with} warm artwork from Studio Ghibli. This shot features: {$@}"
                ),
                "negative": "{$@}"
            },
            "日本动画": {
                "positive": (
                    "An image in anime style including {$spicy-content-with} an ominous atmosphere, clean lines, and dramatic facial expressions. The artwork uses cool and dark tones along with dramatic lighting and shadows that emphasize the central figure and create a somber, intense mood. The dynamic shot has a black background and features: {$@}"
                ),
                "negative": "{$@}"
            },
            "日式漫画": {
                "positive": (
                    "Black and white manga-style illustration that includes {$spicy-content-with} a violent atmosphere. The illustration features: {$@}."
                ),
                "negative": "{$@}"
            },
            "暗黑恐怖漫画": {
                "positive": (
                    "An illustration that includes {$spicy-content-with} stippling textures and intense side lighting with deep shadows; dark low key illumination with high contrast and minimal highlights; cinematic chiaroscuro; horror graphic novel with dynamic composition, featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "淡彩素描": {
                "positive": (
                    "A minimalist and simple pencil sketch that includes {$spicy-content-with} large empty areas and a white background. Painted in watercolors. Featuring: {$@}."
                ),
                "negative": "{$@}"
            },
            "墨线写实": {
                "positive": (
                    "A realistically rendered ink drawing featuring {$spicy-content-with} fine cross-hatching and stippling techniques. These methods create deep shadows and highlights using a monochromatic color scheme. The image includes large areas of white space and high contrast due to varying line densities. Featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "手绘插画": {
                "positive": (
                    "A realistically rendered concept-art done in ink that includes {$spicy-content-with} large white areas and high contrast thanks to the varying density of the lines. It's like a very sharp photograph, but drawn. This colorful concept-art features: {$@}"
                ),
                "negative": "{$@}"
            },
            "数字插画": {
                "positive": (
                    "A detailed illustration in stylized line art featuring {$spicy-content-with} vector graphics aesthetics. With black solid shadows and big negative space creating enigmatic stillness. Saturated highlights with glowing accents, emphasizing contrasts between obscurity and luminous for a vivid impact. Featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "矢量插画": {
                "positive": (
                    "A stylized digital illustration featuring {$spicy-content-with} iconography style. The illustration has a graphic design aesthetic, including flat, solid colors, no defined outlines, and a minimalist approach to composition. Featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "像素艺术": {
                "positive": (
                    "Pixel art image in low resolution that includes {$spicy-content-with} 2D pixelated image in 16 colors. 320x200 sharp image featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "CGA彩色显示器": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "The image shows only an old white CRT PC monitor, reflecting light from a window. A screenshot with black, cyan, magenta, and white colors (CGA graphics card) is visible on the monitor.\n"
                    "Everything in the screenshot is black, cyan, magenta or white, for example, skin should be magenta, plants should be cyan, metal should be cyan, sky should be black.\n"
                    "---\n"
                    "The screenshot inside the monitor features a 2D pixel-art image from 1980 with solid satured colors. {$@}"
                ),
                "negative": "{$@}"
            },
            "复古 VGA 显示器": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You have an old VGA CRT monitor sitting on a wooden desk, and a window is reflected on its screen. The monitor's casing has a raised black inscription in the upper left corner that reads VGA. The screen has a slight curve and sweep lines typical of CRT displays.\n"
                    "---\n"
                    "WHAT'S INSIDE YOUR MONITOR'S SCREEN:\n"
                    "A low-resolution, 2D pixel art platform videogame form early 1990s, featuring: {$@}"
                ),
                "negative": "{$@}"
            },
            "怀旧像素艺术": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your artwork is created in a low-resolution pixel art style, reminiscent of 16-bit era video games. It exhibits {$spicy-content-with} bold, vibrant colors and a limited color palette. Details are simplified and blocky, emphasizing shape and form over realism. The overall aesthetic is retro and nostalgic, with a focus on strong visual impact despite the low pixel count.\n"
                    "---\n"
                    "YOUR DRAWING:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "淡彩素描": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your illustrations are created in a minimalist style, combining delicate pencil sketches with soft watercolor washes. They exhibit {$spicy-content-with} large areas of untouched white space, creating a sense of airiness and simplicity. The pencil lines are light and expressive, while the watercolor washes are subtle and translucent, often blending into the white space. The overall effect is ethereal and contemplative.\n"
                    "---\n"
                    "YOUR DRAWING:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "油画": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are a painter.\n"
                    "Your canvas is painted with impasto; the brushstrokes are thick and visible, and the heavy texture of the impasto is very pronounced. The composition is minimalist with large areas of the same color.\n"
                    "---\n"
                    "YOUR IMPASTO PAINTING:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "日本热血动漫": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your illustrations are high-quality anime artwork, exhibiting {$spicy-content-with} dynamic action poses, vibrant colors, and detailed backgrounds. Character designs are expressive and feature sharp lines, intricate shading, and visible energy effects (like speed lines or glowing auras). The style is inspired by modern action anime.\n"
                    "---\n"
                    "YOUR DRAWING:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "怀旧手绘漫画": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are a 1950s artist who draws comics.\n"
                    "Your worn sheet of paper contains {$spicy-content-with} a vintage 1950s comic book illustration made with hand-drawn lines painted in white, red, blue, and black.\n"
                    "---\n"
                    "YOUR SHEET OF PAPER CONTAINS:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "手绘美漫": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are an artist who draws comics.\n"
                    "Your drawing is a detailed, full-color comic book cover featuring {$spicy-content-with} hatching and hand-drawn curved lines, depicting an intense and violent scene of the highest quality.\n"
                    "---\n"
                    "YOUR DRAWING:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            }
        },
        "镜头": {
            "None": {
                "positive": "{$@}",
                "negative": "{$@}"
            },
            "航拍广角全景图": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are an aerial photographer who enjoys using wide-angle drone cams.\n"
                    "Your photographs exhibit {$spicy-content-with} panoramic scenes captured from afar, high up with elevated perspectives and intense colors.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "移轴微缩摄影": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "You are a photographer who enjoys using tilt‑shift lenses to turn real‑world scenes into miniature toy models.\n"
                    "Your photographs exhibit {$spicy-content-with} crisp, high‑resolution details captured in an exaggerated perspective, with a very narrow focus plane, and a dreamy, toy‑like atmosphere that creates the classic “miniature” illusion.\n"
                    "---\n"
                    "YOUR PHOTO:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "广角 / 猫眼": {
                "positive": (
                    "YOUR CONTEXT:\n"
                    "Your peephole shows {$spicy-content-with} a shot from a high angle, inside a fisheye lens distortion glass circle, highly distorted with a wide angle.\n"
                    "---\n"
                    "YOUR PEEPHOLE:\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            }
        }
    },
    "Nano Banana": {
        "风格转绘": {
            "None": {
                    "positive": "{$@}",
                    "negative": "{$@}"
            },
            "草图转线稿": {
                "positive": (
                    "将输入的草图忠实重绘为干净清晰的线稿。线条风格类似日本动画原画/清线草稿：自然、有节奏感，线条粗细略有变化；使用铅笔或数位铅笔质感线条，严格保持原草图的姿势、人物比例、服装结构和所有细节，不做任何设计上的修改。去除所有辅助线、构图线、关节圆、重叠草线和杂乱笔触。面部线条干净柔和，眼睛线条精致，表情自然；二次元风格线稿，专业插画线稿质量。白色背景，无阴影，无灰度，无上色。\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "水彩风格转绘": {
                "positive": (
                    "将上传的图像转换成 淡淡的水彩绘画风格：- 使用传统水彩画的美术表现：柔和透明色彩、流动的色块、轻盈的笔触；- 色彩柔和渐变，边缘略微自然晕染，不是硬边或数字插画风格；- 画面呈现水彩纸纹理质感，颜色层次自然叠加；- 主体清晰、保留细节但融入水彩画的氛围与色彩；- 整体风格艺术感强，像用真实水彩工具手绘的一幅画；- 背景简洁或带淡淡水彩背景色块，让作品更有手绘艺术表现。\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "3A 级写实风格": {
                "positive": (
                    "将上传的角色图像转换成 Unreal Engine 5 AAA 级写实游戏美术风格的艺术作品，带 影视级光影与真实材质纹理：- 角色为写实 3D 模型渲染风格，采用高质量 物理基础渲染（PBR）材质、精细 法线贴图 / 粗糙度贴图 / 反射贴图，表现出真实表面质感；- 面部与身体具有真实体积感：自然光照下的立体阴影、高光与细节过渡，让脸部和身体更有真实感，不是扁平插画；- 肤质、眼睛、高光、微表情、皮肤表面反射等细节真实表现，光影在面部呈现自然层次，强调整体体积感；- 服装、装备与配件均为真实材质质感，纹理清晰可读，例如布料纤维、金属反射、皮革质感都真实分层；- 影视级光影处理：使用复杂光照布局，例如主光、柔光填充、逆光边缘光，以及柔和环境光，构成电影感光影效果，使角色具有更加戏剧化和真实的明暗对比； - 光照使用写实环境光与局部光源结合，阴影柔和自然、层次丰富，使整体呈现次世代写实质量；- 场景背景简单中性或虚拟光影背景（如浅灰渐变或暗色电影工作室质感），突出角色写实渲染效果；- 保留原角色设计特征、形状与风格，但整体渲染与表现为 UE5 AAA 真实游戏 + 电影感光影风格。\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "PBR风格": {
                "positive": (
                    "将上传的二次元角色图像转换为 Unreal Engine 5 实时渲染风格的高质量图像：\n"
                    "主体：保留原二次元角色的面部特征、发型与服饰设计细节；\n"
                    "风格：UE5 PBR 真实渲染材质、高清纹理、物理光照、动态阴影；\n"
                    "材质细节：皮肤具备次表面散射 (SSS) 效果，衣物带实时布料纹理与法线贴图，高光反射符合真实材质逻辑；\n"
                    "光照设置：真实世界光照（HDRI + UE5 光线追踪），柔和阴影与自然光环境；\n"
                    "镜头效果：35mm 虚幻引擎标准镜头，浅景深，高动态范围；\n"
                    "背景：简洁可选（如 UE5 默认场景、摄影棚灯光背景或真实环境 HDRI）；\n"
                    "构图：角色站立中景，全身视角，可见全身与服饰；\n"
                    "附加渲染设定：真实环境反射、柔光阴影、细节高对比纹理；\n"
                    "{$@}"
                    ),
                "negative": "{$@}"
            },
            "手办风格": {
                "positive": (
                    "将上传的二次元角色转换为高精度手办风格图像：\n"
                    "主体角色作为 3D 收藏手办，比例如 1/7 或 1/8 真实比例；\n"
                    "材质：PVC/ABS 玩具质感，高渲染细节、真实光泽与纹理；\n"
                    "上色：精细喷涂质感、无卡通平涂、带自然渐变与阴影；\n"
                    "灯光：柔光摄影棚光照 + 细节阴影，逼真模型摄影风；\n"
                    "底座：透明圆形丙烯底座或展示台，配角色姓名牌（可选）；\n"
                    "背景：简洁摄影棚灰或浅色背景，弱景深突出手办主体；\n"
                    "相机设定：85mm 标准镜头，浅景深，高清 4K 输出；\n"
                    "附加：如包装盒与角色设计图展示（可选），增加展示感；\n"
                    "保持角色外观一致，不改变原设定特征与配色；将上传的二次元角色转换为高精度手办风格图像：\n"
                    "主体角色作为 3D 收藏手办，比例如 1/7 或 1/8 真实比例；\n"
                    "材质：PVC/ABS 玩具质感，高渲染细节、真实光泽与纹理；\n"
                    "上色：精细喷涂质感、无卡通平涂、带自然渐变与阴影；\n"
                    "灯光：柔光摄影棚光照 + 细节阴影，逼真模型摄影风；\n"
                    "底座：透明圆形丙烯底座或展示台，配角色姓名牌（可选）；\n"
                    "背景：简洁摄影棚灰或浅色背景，弱景深突出手办主体；\n"
                    "相机设定：85mm 标准镜头，浅景深，高清 4K 输出；\n"
                    "附加：如包装盒与角色设计图展示（可选），增加展示感；\n"
                    "保持角色外观一致，不改变原设定特征与配色；\n"
                    "{$@}"
                    ),
                "negative": "{$@}"
            },
            "黏土风格": {
                "positive": (
                    "将主体转化为风格化的3D角色，采用柔软的黏土质感、圆润的雕塑造型、夸张的面部特征、柔和与鲜艳的色彩搭配、光滑的底层纹理、卡通大眼睛和简化的解剖结构。在醒目的蓝色工作室背景下渲染，采用柔和的正面光线和微妙的阴影。营造一种趣味盎然、超现实且精致的角色设计美感，类似于现代风格化的3D插画。保留原照片的构图和取景。\n"
                    "{$@}"
                    ),
                "negative": "{$@}"
            },
            "日式老动画风格": {
                "positive": (
                    "将上传的角色图像转换成类似**1980~90 年代日本 TV 动画（如《城市猎人 City Hunter》）**的视觉风格插画：\n"
                    "动画作画风格参照 80~90 年代日式老动画，强调手绘质感与传统单元动画表现；\n"
                    "角色线条清晰但不完美，略带自然笔触手绘感，线条粗细略有变化；\n"
                    "色彩使用经典平涂与简化阴影，不是现代渐变渲染，采用经典日式动画色板；\n"
                    "明显的细节处理（如脸部线条细节、眼睛高光、服装褶皱线条），带复古感；\n"
                    "略微颗粒质感或“胶片感”背景，使画面有旧动画胶片的怀旧色调与质感；\n"
                    "角色动作或姿势可参考老式动画构图法，具有动态但简化的表现；\n"
                    "整体呈现怀旧风格，像一幅来自 80~90 年代电视动画的角色设定插画或一帧画面；\n"
                    "{$@}"
                    ),
                "negative": "{$@}"
            },
            "Overwatch游戏风格": {
                "positive": (
                    "将上传的角色图像转换成 3D 实时渲染风格，效果像真实的《Overwatch 2》局内截图：\n"
                    "主体：\n"
                    "保留角色的所有视觉特征：面部结构、发型、服装设计、装饰细节、配色。\n"
                    "将角色转换成 Overwatch 2 风格的 3D 游戏模型外观，不保留二次元平面风。\n"
                    "材质与光照：\n"
                    "游戏引擎实时渲染：高质量 PBR 材质、清晰法线贴图、真实光泽、高光与阴影。\n"
                    "明亮且饱和的色彩、柔和环境光遮蔽（AO）、动态光照和阴影表现。\n"
                    "模拟《Overwatch 2》特有的科技幻想质感：服装、护甲、光泽面料、金属反射、能量效果。\n"
                    "构图与环境：\n"
                    "场景为 Overwatch 2 局内地图某区域（科技基地、竞技场墙面、细节背景景深）。\n"
                    "采用等距或第三人称视角，如真实游戏截图镜头。\n"
                    "可选：场景动态光影、粒子效果、战斗中动作姿态（如准备姿势）。\n"
                    "镜头与输出：\n"
                    "实时渲染截图质感，浅景深、HDR、清晰纹理、边缘锐利。\n"
                    "4K 高清效果，真实游戏感，不是插画或卡通风格。\n"
                    "约束：\n"
                    "禁止卡通平涂阴影和手绘边缘。\n"
                    "角色结构必须匹配真实 3D 模型体积感和比例。\n"
                    "输出要求：\n"
                    "输出看起来像是在 Overwatch 2 内真实截取的画面级渲染图。\n"
                    "{$@}"
                    ),
                "negative": "{$@}"
            },
            "原神游戏风格": {
                "positive": (
                    "将上传的角色转换成类似《原神》（Genshin Impact）游戏内真实截图风格：\n"
                    "- 角色整体为 3D 实时渲染风格，符合原神游戏的美术与材质表现（PBR 材质、逼真光影、柔和阴影、环境光遮蔽等）。\n"
                    "- 面部与身体的立体体积感与光照表现像原神游戏内角色模型，真实但具有幻想游戏质感，非平面绘画。\n"
                    "- 保留原角色的设计特征与细节，但整体渲染风格贴合原神游戏里角色的模型与材质风格。\n"
                    "- 加入典型《原神》局内 HUD/UI 元素覆盖在画面上，如角色图标、生命值/元素能量条、技能快捷栏、小地图等。\n"
                    "- 场景背景为《原神》游戏世界局内地图，可见地表纹理、植被、建筑等细节。\n"
                    "- 输出清晰、锐利、高质量截图级效果。将上传的角色转换成类似《原神》（Genshin Impact）游戏内真实截图风格：\n"
                    "- 角色整体为 3D 实时渲染风格，符合原神游戏的美术与材质表现（PBR 材质、逼真光影、柔和阴影、环境光遮蔽等）。\n"
                    "- 面部与身体的立体体积感与光照表现像原神游戏内角色模型，真实但具有幻想游戏质感，非平面绘画。\n"
                    "- 保留原角色的设计特征与细节，但整体渲染风格贴合原神游戏里角色的模型与材质风格。\n"
                    "- 加入典型《原神》局内 HUD/UI 元素覆盖在画面上，如角色图标、生命值/元素能量条、技能快捷栏、小地图等。\n"
                    "- 场景背景为《原神》游戏世界局内地图，可见地表纹理、植被、建筑等细节。\n"
                    "- 输出清晰、锐利、高质量截图级效果。\n"
                    "{$@}"
                    ),
                "negative": "{$@}"
            },
            "少女前线游戏风格": {
                "positive": (
                    "将上传的角色转换成类似《少女前线2：追放》局内真实截图风格的图像：\n"
                    "- 角色整体为 3D 实时渲染风格（高质量 PBR 材质、法线贴图、动态光照、环境阴影），面部和身体体积感、细节光影符合《少女前线2》游戏内渲染风格；\n"
                    "- 面部风格像游戏内模型：立体面部体积、自然光影过渡、清晰光泽与皮肤质感，使其看起来像局内角色模型（非平面插画）；\n"
                    "- 建模风格贴近《少女前线2》角色三维造型：清晰可见的材质层级、装备结构与服饰纹理；\n"
                    "- 保留原角色的视觉设计与细节，但渲染风格、光照与面部表现与游戏一致；\n"
                    "- 添加典型《少女前线2》局内 HUD/UI 元素（如角色状态栏、技能图标、命令界面等）覆盖在画面上；\n"
                    "- 背景为游戏战场场景，可见策略视角或第三人称俯视视角；\n"
                    "- 输出清晰、锐利、高清，如真实游戏截图。\n"
                    "{$@}"
                    ),
                "negative": "{$@}"
            },
        },
        "Tool": {
            "图片转化成色卡": {
                "positive": (
                    "请从上传的图像中提取主要配色，生成一组清晰的色卡：分析图像中出现的主要颜色；提取代表性配色，而非噪点或偶发颜色；颜色数量控制在合理范围内（约 6–12 色）；以色块形式展示色卡；每个颜色标注对应的 HEX 或 RGB 数值；色卡应能准确反映原图整体色彩风格。\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "按色卡给线稿上色": {
                "positive": (
                    "严格参照图1的色卡将图2转换为 线稿 + 色卡平：使用清晰的线稿作为结构基础，线条干净、有轻微粗细变化；上色方式为 严格平涂（flat color），不添加任何阴影、高光或渐变；所有颜色必须严格取自用户提供的色卡，不得自行生成或偏移颜色；每个区域只使用单一纯色填充，色块边缘清晰、干净；不进行体积塑造、不做明暗关系、不做光照表现；面部、头发、服装、饰品均按色卡对应颜色平涂；整体效果类似动画/游戏制作中的“平涂上色阶段”；背景可留白或使用色卡中的单一背景色；保留原角色设计与结构，仅执行线稿与色卡平涂处理。\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "设计元素拆解": {
                "positive": (
                    "角色设定 你是一位顶尖的游戏与动漫概念美术设计大师 ，擅长制作详尽的角色设定图。你具备“像素级拆解”的能力，能够透视角色的穿着层级、捕捉微表情变化，并将与其相关的物品进行具象化还原。 任务目标 根据用户上传或描述的主体形象，生成一张“全景式角色深度概念分解图”。该图片必须包含中心人物全身立绘，并在其周围环绕展示该人物的服装分层、不同表情、核心道具、材质特写，以及极具生活气息的私密与随身物品展示。 视觉规范 1. 构图布局 : • 中心位 : 放置角色的全身立绘或主要动态姿势，作为视觉锚点。 • 环绕位 : 在中心人物四周空白处，有序排列拆解后的元素。 • 视觉引导 : 使用手绘箭头或引导线，将周边的拆解物品与中心人物的对应部位或所属区域（如包包连接手部）连接起来。 2. 拆解内容 核心迭代区域: 服装分层 : 将角色的服装拆分为单品展示。如果是多层穿搭，需展示脱下外套后的内层状态。 新增：私密内着拆解 : 独立展示角色的内层衣物，重点突出设计感与材质。 表情集 : 在角落绘制 3-4 个不同的头部特写，展示不同的情绪。 材质特写 : 选取 1-2 个关键部位进行放大特写。 新增：物品质感特写: 增加对小物件材质的描绘 关联物品 : 此处不再局限于大型道具，需增加展示角色的“生活切片”。 随身包袋与内容物 : 绘制角色的日常通勤包或手拿包，并将其“打开”，展示散落在旁的物品。 美妆与护理 : 展示其常用的化妆品组合。 私密生活物件 : 具象化角色隐藏面的物品。根据角色性格可能包括：私密日记本、常用药物/补剂盒、电子烟、或者更私人的物件。 3. 风格与注释 : 画风: 保持高质量的 2D 插画风格或概念设计草图风格，线条干净利落。 背景: 使用米黄色、羊皮纸或浅灰色纹理背景，营造设计手稿的氛围。 文字说明: 在每个拆解元素旁模拟手写注释，简要说明材质或品牌/型号暗示。 执行逻辑 当用户提供一张图片或描述时： 1. 分析主体的核心特征、穿着风格及潜在性格。 2. 提取可拆解的一级元素（外套、鞋子、大表情） 3. 脑补并设计二级深度元素（她内衣穿什么风格？她包里会装什么口红？） 4. 生成一张包含所有这些元素的组合图，确保透视准确，光影统一，注释清晰。 5. 使用中文，白色背景\n"
                    "{$@}"
                    ),
                "negative": "{$@}"
            },
            "三视图": {
                "positive": (
                    "参考图片角色，制作它的三视图，a poss，正视图，侧视图，背视图，视图平行排开。\n"
                    "{$@}"
                ),
                "negative": "{$@}"
            },
            "手绘风格食谱教学": {
                "positive": (
                    "创作一张竖版 的 《{$@}》手绘风格教学食谱信息图。\n"
                    "整体风格要求：\n"
                    "•        由专业厨师写给普通人的教学食谱\n"
                    "•        使用 Z 字形动线排版（左上 → 右上 → 左下），阅读顺畅\n"
                    "•        彩色水彩笔速写风格，搭配 细腻墨线轮廓\n"
                    "•        采用 2026 主流插画配色与笔触\n"
                    "•        米色纸张纹理背景，温暖、质朴、亲切\n"
                    "•        插图必须让人“看了就想做”\n"
                    "⸻\n"
                    "内容结构（通用）\n"
                    "1. 顶部标题（醒目）\n"
                    "《{菜名}》\n"
                    "⸻\n"
                    "2. 步骤区块（Z 动线排版，3–5 步）\n"
                    "每个步骤包含：\n"
                    "•        手绘步骤插图（彩色水彩＋墨线）\n"
                    "•        简短图文说明\n"
                    "•        厨师秘技\n"
                    "•        小心得或提示\n"
                    "⸻\n"
                    "步骤模板（通用，可被模型自动填充）\n"
                    "步骤 1：准备食材\n"
                    "（自动根据菜名生成相关食材）\n"
                    "插图：整齐摆放的主要食材和调味料。\n"
                    "说明：列出并处理该菜的基本材料。\n"
                    "秘技：告诉用户如何提升风味或口感。\n"
                    "心得：提供简单经验或提醒。\n"
                    "⸻\n"
                    "步骤 2：调味 / 腌制 / 前置处理\n"
                    "插图：调制酱汁、腌肉、处理主料的小碗或砧板画面。\n"
                    "说明：展示关键基础步骤。\n"
                    "秘技：比例、小技巧、避免失败要点。\n"
                    "心得：轻松风格的小提示。\n"
                    "⸻\n"
                    "步骤 3：炒制 / 烹调关键步骤\n"
                    "插图：锅中食材的烹调场景，水彩烟气柔和。\n"
                    "说明：大火、小火、顺序、重要动作。\n"
                    "秘技：保持火候、控制时间、提升香气的办法。\n"
                    "心得：强调料理灵魂所在。\n"
                    "⸻\n"
                    "步骤 4：合味 / 出锅前步骤\n"
                    "插图：加入酱汁、调味、配料混合的场景。\n"
                    "说明：整体收汁、调味到位。\n"
                    "秘技：亮油、保持口感或香味的小技巧。\n"
                    "心得：此步决定成败。\n"
                    "⸻\n"
                    "步骤 5：点缀 / 完成步骤\n"
                    "插图：撒香料、加入坚果、盛盘等动作。\n"
                    "说明：最后调整味道或摆盘。\n"
                    "秘技：保持脆感、避免过熟等技巧。\n"
                    "心得：成品风味描述。\n"
                    "⸻\n"
                    "底部成品插图\n"
                    "•        一份精致、色香俱全的 《{菜名}》\n"
                    "•        水彩质感强烈、油亮、鲜嫩、诱人\n"
                    "•        让读者看了就想做\n"
                    "⸻\n"
                    ),
                "negative": "{$@}"
            },
            "9宫格照片": {
                "positive": (
                    "生成 3×3 照片网格。 在所有面板中完整保留上传图像中的面部、发型和服装。 画中人应该做出可爱、滑稽、表情和姿势，并且所有 9 个画面中的表情和姿势都不一样。 每个小组都应该使用不同的拍摄角度。 使用以下角度，并采用不同的构图和取景方式： 1. 高角度（顶部- down) 2. 低角度（从下方） 3. 视线水平正对 4. 荷兰角（略微倾斜） 5. 近景低角度拍摄 6. 过肩角度 7. 侧面远景 8. 从正面看呈45度角 9. 略微俯视角度 风格要求： •逼真、清晰的光照 •真实相机镜头渲染 •无插图或卡通风格 •所有图片中的服装、脸型和发型都相同 •整个网格中的姿势和表情保持一致 现代简约美学\n"
                    "{$@}"
                    ),
                "negative": "{$@}"
            },
        }
    }
    
    # "Temple": {
    #     "": {
    #         "": {
    #             "positive": (
    #                 "YOUR CONTEXT:\n"
    #                 "\n"
    #                 "---\n"
    #                 "YOUR PHOTO:\n"
    #                 "{$@}"
    #             ),
    #             "negative": "{$@}"
    #         },
    #         "": {
    #             "positive": (
    #                 "YOUR CONTEXT:\n"
    #                 "\n"
    #                 "---\n"
    #                 "YOUR PHOTO:\n"
    #                 "{$@}"
    #             ),
    #             "negative": "{$@}"
    #         }
    #     }
    # }
}