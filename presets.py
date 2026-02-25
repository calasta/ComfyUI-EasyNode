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