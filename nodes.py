import os
import torch
import numpy as np
import hashlib
from PIL import Image, ImageOps, ImageSequence
import folder_paths
import zipfile
import io
from collections import OrderedDict

# ==============================================================================
#                               PART 0: PRESETS
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
#                               PART 1: EasySize Nodes
# ==============================================================================
def resize_crop(image: Image.Image, tgt_w, tgt_h, crop_method, algo) -> Image.Image:
    if crop_method == "中心裁剪":
        image = ImageOps.fit(image, (tgt_w, tgt_h), method=Image.Resampling[algo.upper()])
    else:
        image = image.resize((tgt_w, tgt_h), resample=Image.Resampling[algo.upper()])
    return image

def resize_by_long_or_short(pil_img: Image.Image, edge_mode: str, target_len: int) -> Image.Image:
    w, h = pil_img.size
    if edge_mode == "最长边":
        if w >= h:
            new_w, new_h = target_len, int(h * target_len / w)
        else:
            new_w, new_h = int(w * target_len / h), target_len
    else:  # 最短边
        if w <= h:
            new_w, new_h = target_len, int(h * target_len / w)
        else:
            new_w, new_h = int(w * target_len / h), target_len
    return pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

class EasySizeSimpleImage:
    def __init__(self): pass
    @classmethod
    def INPUT_TYPES(cls):
        preset_dict = {k: ["关"] + [t[0] for t in PRESETS[k]] for k in PRESETS}
        return {
            "required": {
                **{k: (v, {"default": "关"}) for k, v in preset_dict.items()},
                "裁剪方式": (CROP_METHODS, {"default": "中心裁剪"}),
                "缩放算法": (RESIZE_ALGOS, {"default": "lanczos"}),
                "启用边长缩放": ("BOOLEAN", {"default": False}),
                "缩放至边": (["最长边", "最短边"], {"default": "最长边"}),
                "缩放长度": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
            },
            "optional": {"图像": ("IMAGE",), "遮罩": ("MASK",)}
        }
    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("图像", "遮罩", "宽", "高")
    FUNCTION = "run"
    CATEGORY = "EasyNode/EasySize"
    def run(self, 图像=None, 遮罩=None, **kwargs):
        use_edge = kwargs["启用边长缩放"]
        edge_mode = kwargs["缩放至边"]
        target_len = kwargs["缩放长度"]
        crop = kwargs["裁剪方式"]
        algo = kwargs["缩放算法"]
        if use_edge:
            if 图像 is not None:
                b, h0, w0, c = 图像.shape
                arr = (图像.squeeze(0).cpu().numpy() * 255).astype(np.uint8)
                pil_img = Image.fromarray(arr)
                pil_img = resize_by_long_or_short(pil_img, edge_mode, target_len)
                arr = np.array(pil_img).astype(np.float32) / 255.0
                图像 = torch.from_numpy(arr).unsqueeze(0)
                out_w, out_h = pil_img.size
            else:
                图像 = torch.zeros((1, 512, 512, 3), dtype=torch.float32); out_w, out_h = 512, 512
            if 遮罩 is not None:
                b, h0, w0 = 遮罩.shape
                arr = (遮罩.squeeze(0).cpu().numpy() * 255).astype(np.uint8)
                pil_msk = Image.fromarray(arr, mode="L")
                pil_msk = resize_by_long_or_short(pil_msk, edge_mode, target_len)
                arr = np.array(pil_msk).astype(np.float32) / 255.0
                遮罩 = torch.from_numpy(arr).unsqueeze(0)
            else:
                遮罩 = torch.zeros((1, out_h, out_w), dtype=torch.float32)
            return (图像, 遮罩, out_w, out_h)
        choices = {k: kwargs[k] for k in PRESETS}
        w, h = get_size_from_preset(choices)
        if 图像 is not None:
            b, h0, w0, c = 图像.shape
            arr = (图像.squeeze(0).cpu().numpy() * 255).astype(np.uint8)
            pil_img = Image.fromarray(arr)
            pil_img = resize_crop(pil_img, w, h, crop, algo)
            arr = np.array(pil_img).astype(np.float32) / 255.0
            图像 = torch.from_numpy(arr).unsqueeze(0)
        else:
            图像 = torch.zeros((1, h, w, 3), dtype=torch.float32)
        if 遮罩 is not None:
            b, h0, w0 = 遮罩.shape
            arr = (遮罩.squeeze(0).cpu().numpy() * 255).astype(np.uint8)
            pil_msk = Image.fromarray(arr, mode="L")
            pil_msk = resize_crop(pil_msk, w, h, crop, algo)
            arr = np.array(pil_msk).astype(np.float32) / 255.0
            遮罩 = torch.from_numpy(arr).unsqueeze(0)
        else:
            遮罩 = torch.zeros((1, h, w), dtype=torch.float32)
        return (图像, 遮罩, w, h)

class EasySizeSimpleLatent:
    def __init__(self): pass
    @classmethod
    def INPUT_TYPES(cls):
        preset_dict = {k: ["关"] + [t[0] for t in PRESETS[k]] for k in PRESETS}
        return {
            "required": {
                **{k: (v, {"default": "关"}) for k, v in preset_dict.items()},
                "启用自定义尺寸": ("BOOLEAN", {"default": False}),
                "宽度": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "高度": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
            }
        }
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "run"
    CATEGORY = "EasyNode/EasySize"
    def run(self, **kwargs):
        use_custom = kwargs["启用自定义尺寸"]
        if use_custom:
            w, h = kwargs["宽度"], kwargs["高度"]
        else:
            choices = {k: kwargs[k] for k in PRESETS}
            w, h = get_size_from_preset(choices)
        latent = torch.zeros([1, 4, h // 8, w // 8])
        return ({"samples": latent},)

class EasySizeSimpleSetting:
    def __init__(self): pass
    @classmethod
    def INPUT_TYPES(cls):
        preset_dict = {k: ["关"] + [t[0] for t in PRESETS[k]] for k in PRESETS}
        return {
            "required": {
                **{k: (v, {"default": "关"}) for k, v in preset_dict.items()},
                "启用自定义尺寸": ("BOOLEAN", {"default": False}),
                "宽度": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "高度": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
            }
        }
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("宽度", "高度")
    FUNCTION = "run"
    CATEGORY = "EasyNode/EasySize"
    def run(self, **kwargs):
        use_custom = kwargs["启用自定义尺寸"]
        if use_custom:
            return (kwargs["宽度"], kwargs["高度"])
        choices = {k: kwargs[k] for k in PRESETS}
        w, h = get_size_from_preset(choices)
        return (w, h)

# ==============================================================================
#                               PART 2: Loader Nodes
# ==============================================================================

class EasyNodeLoader: 
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = []
        try:
            if input_dir and os.path.exists(input_dir):
                files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
                files = sorted(files)
        except Exception as e:
            print(f"[EasyNode] Error reading input directory: {e}")
        
        if not files:
            files = ["# NO IMAGES FOUND #"]

        return {
            "required": {
                "mode": (["single", "batch"], {"default": "single"}),
                "image": (files, {"image_upload": True}),
                "batch_path": ("STRING", {"default": ""}),
                "width": ("INT", {"default": 720, "min": 1, "max": 8192, "step": 1}),
                "height": ("INT", {"default": 1280, "min": 1, "max": 8192, "step": 1}),
                "upscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "lanczos"],),
                "keep_proportion": (["crop", "stretch", "pad"],),
                "crop_position": (["center", "top", "bottom", "left", "right"], {"default": "center"}),
                "divisible_by": ("INT", {"default": 2, "min": 1, "max": 64, "step": 1}),
            },
            "hidden": {
                "mask_data": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("IMAGE", "MASK", "width", "height")
    FUNCTION = "load_image"
    CATEGORY = "EasyNode/Loader"
    TITLE = "EasyNode Load Image"

    def load_image(self, mode, image, batch_path, width, height, upscale_method, keep_proportion, crop_position, divisible_by, mask_data=""):
        width = (width // divisible_by) * divisible_by
        height = (height // divisible_by) * divisible_by
        resample_map = {"nearest-exact": Image.NEAREST, "bilinear": Image.BILINEAR, "area": Image.BOX, "bicubic": Image.BICUBIC, "lanczos": Image.LANCZOS}
        resample = resample_map.get(upscale_method, Image.BICUBIC)

        images_to_load = []
        if mode == "single":
            if image == "# NO IMAGES FOUND #":
                 raise Exception("No images found in ComfyUI input directory. Please upload an image.")
            image_path = folder_paths.get_annotated_filepath(image)
            images_to_load.append(("path", image_path))
        else:
            if not batch_path: raise Exception("Batch path is empty")
            batch_path = batch_path.strip().strip('"')
            if os.path.isdir(batch_path):
                for f in sorted(os.listdir(batch_path)):
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')) and not f.startswith("mask_"):
                        images_to_load.append(("path", os.path.join(batch_path, f)))
            elif zipfile.is_zipfile(batch_path):
                with zipfile.ZipFile(batch_path, 'r') as z:
                    for f in sorted(z.namelist()):
                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')) and not os.path.basename(f).startswith("mask_"):
                            images_to_load.append(("zip", (batch_path, f)))
            else:
                raise Exception(f"Invalid batch path: {batch_path}. Must be a directory or zip file.")

        if not images_to_load: raise Exception("No images found to load.")

        external_mask = None
        if mode == "single" and mask_data:
            mask_path = None
            try:
                # 1. Try Input Dir (Standard)
                mask_path = folder_paths.get_annotated_filepath(mask_data)
            except:
                pass

            # 2. Fallback check Input Dir
            if not mask_path or not os.path.exists(mask_path):
                 inp_dir = folder_paths.get_input_directory()
                 potential_path = os.path.join(inp_dir, mask_data)
                 if os.path.exists(potential_path):
                     mask_path = potential_path
            
            # 3. [FIX] Check Temp Dir (for new behavior)
            if not mask_path or not os.path.exists(mask_path):
                 try:
                     temp_dir = folder_paths.get_temp_directory()
                     potential_path = os.path.join(temp_dir, mask_data)
                     if os.path.exists(potential_path):
                         mask_path = potential_path
                 except:
                     pass

            if mask_path and os.path.exists(mask_path):
                try:
                    mask_img = Image.open(mask_path)
                    if "A" in mask_img.getbands():
                        external_mask = np.array(mask_img.getchannel("A")).astype(np.float32) / 255.0
                    else:
                        external_mask = np.array(mask_img.convert("L")).astype(np.float32) / 255.0
                except Exception as e:
                    print(f"[EasyNode] Error loading external mask: {e}")

        output_images = []
        output_masks = []
        
        for img_type, img_info in images_to_load:
            if img_type == "path": img = Image.open(img_info)
            else:
                z_path, z_file = img_info
                with zipfile.ZipFile(z_path, 'r') as z:
                    with z.open(z_file) as f: img = Image.open(io.BytesIO(f.read()))

            for i in ImageSequence.Iterator(img):
                i = ImageOps.exif_transpose(i)
                if i.mode == 'I': i = i.point(lambda i: i * (1 / 255))
                image_rgb = i.convert("RGB")
                
                if external_mask is not None:
                    current_mask_pil = Image.fromarray((external_mask * 255).astype(np.uint8), mode='L')
                    if current_mask_pil.size != image_rgb.size:
                        current_mask_pil = current_mask_pil.resize(image_rgb.size, resample=Image.BILINEAR)
                elif "A" in i.getbands():
                    alpha = np.array(i.getchannel("A")).astype(np.float32) / 255.0
                    current_mask_pil = Image.fromarray(((1.0 - alpha) * 255).astype(np.uint8), mode='L')
                else:
                    current_mask_pil = Image.new("L", image_rgb.size, 0)

                image_rgb, current_mask_pil = self.apply_resize(image_rgb, current_mask_pil, width, height, resample, keep_proportion, crop_position)
                
                image_tensor = np.array(image_rgb).astype(np.float32) / 255.0
                image_tensor = torch.from_numpy(image_tensor)[None,]
                mask_tensor = np.array(current_mask_pil).astype(np.float32) / 255.0
                mask_tensor = torch.from_numpy(mask_tensor)[None,]

                output_images.append(image_tensor)
                output_masks.append(mask_tensor)

        if not output_images: raise Exception("No valid images processed.")
        return (torch.cat(output_images, dim=0), torch.cat(output_masks, dim=0), width, height)

    def apply_resize(self, image, mask, target_width, target_height, resample, keep_proportion, crop_position):
        orig_width, orig_height = image.size
        if keep_proportion == "stretch":
            image = image.resize((target_width, target_height), resample=resample)
            mask = mask.resize((target_width, target_height), resample=resample)
        elif keep_proportion == "crop":
            ratio = max(target_width / orig_width, target_height / orig_height)
            new_width = int(orig_width * ratio); new_height = int(orig_height * ratio)
            image = image.resize((new_width, new_height), resample=resample)
            mask = mask.resize((new_width, new_height), resample=resample)
            if crop_position == "center": left = (new_width - target_width) // 2; top = (new_height - target_height) // 2
            elif crop_position == "top": left = (new_width - target_width) // 2; top = 0
            elif crop_position == "bottom": left = (new_width - target_width) // 2; top = new_height - target_height
            elif crop_position == "left": left = 0; top = (new_height - target_height) // 2
            elif crop_position == "right": left = new_width - target_width; top = (new_height - target_height) // 2
            else: left = (new_width - target_width) // 2; top = (new_height - target_height) // 2
            image = image.crop((left, top, left + target_width, top + target_height))
            mask = mask.crop((left, top, left + target_width, top + target_height))
        elif keep_proportion == "pad":
            ratio = min(target_width / orig_width, target_height / orig_height)
            new_width = int(orig_width * ratio); new_height = int(orig_height * ratio)
            image = image.resize((new_width, new_height), resample=resample)
            mask = mask.resize((new_width, new_height), resample=resample)
            new_image = Image.new("RGB", (target_width, target_height), (0, 0, 0))
            new_mask = Image.new("L", (target_width, target_height), 0)
            left = (target_width - new_width) // 2; top = (target_height - new_height) // 2
            new_image.paste(image, (left, top)); new_mask.paste(mask, (left, top))
            image = new_image; mask = new_mask
        return image, mask

    @classmethod
    def IS_CHANGED(s, mode, image, batch_path, mask_data="", **kwargs):
        m = hashlib.sha256()
        if mode == "single":
            image_path = folder_paths.get_annotated_filepath(image)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f: m.update(f.read())
            if mask_data: m.update(mask_data.encode())
        else:
            m.update(batch_path.encode())
            if os.path.exists(batch_path): m.update(str(os.path.getmtime(batch_path)).encode())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, mode, image, batch_path, **kwargs):
        if mode == "single":
            if image == "# NO IMAGES FOUND #": return "No images found in input directory"
            if not folder_paths.exists_annotated_filepath(image): return "Invalid image file: {}".format(image)
        else:
            if not batch_path: return "Batch path is required for batch mode."
            if not os.path.exists(batch_path): return "Batch path does not exist: {}".format(batch_path)
        return True

# ==============================================================================
#                               REGISTRATION
# ==============================================================================

NODE_CLASS_MAPPINGS = {
    "EasySizeSimpleImage":   EasySizeSimpleImage,
    "EasySizeSimpleLatent":  EasySizeSimpleLatent,
    "EasySizeSimpleSetting": EasySizeSimpleSetting,
    "EasyNodeLoader":        EasyNodeLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EasySizeSimpleImage":   "EasyNode 简单图像尺寸",
    "EasySizeSimpleLatent":  "EasyNode 简单图像尺寸-Latent",
    "EasySizeSimpleSetting": "EasyNode 简单尺寸设置",
    "EasyNodeLoader":        "EasyNode 加载图像 (Loader)"
}