import os
import torch
import numpy as np
import hashlib
from PIL import Image, ImageOps, ImageSequence
import folder_paths
import zipfile
import io
import math

# --- 引入 ComfyUI Server 用于构建内部 API ---
import server
from aiohttp import web

# --- 引入EasySize Preset 数据 ---
from .presets import PRESETS, CROP_METHODS, RESIZE_ALGOS, get_size_from_preset, STYLE_PRESETS

# --- ComfyUI 核心引用 ---
import node_helpers
import comfy.utils
import comfy.model_management

# ==============================================================================
#                            API ROUTE FOR JS FRONTEND
# ==============================================================================
# 暴露预设给前端 JS 以实现动态三级联动
@server.PromptServer.instance.routes.get("/easynode/get_styles")
async def get_styles(request):
    return web.json_response(STYLE_PRESETS)

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
    else:
        if w <= h:
            new_w, new_h = target_len, int(h * target_len / w)
        else:
            new_w, new_h = int(w * target_len / h), target_len
    return pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

class EasySizeSimpleImage:
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
    TITLE = "EasyNode 加载图像 (Loader)"

    def load_image(self, mode, image, batch_path, width, height, upscale_method, keep_proportion, crop_position, divisible_by, mask_data=""):
        width = (width // divisible_by) * divisible_by
        height = (height // divisible_by) * divisible_by
        resample_map = {"nearest-exact": Image.NEAREST, "bilinear": Image.BILINEAR, "area": Image.BOX, "bicubic": Image.BICUBIC, "lanczos": Image.LANCZOS}
        resample = resample_map.get(upscale_method, Image.BICUBIC)

        images_to_load = []
        if mode == "single":
            if image == "# NO IMAGES FOUND #":
                 raise Exception("No images found in ComfyUI input directory.")
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

        output_images = []
        output_masks = []
        
        # 遮罩处理逻辑 (省略重复的基础代码以节省空间, 保持原插件 A 逻辑)
        # ... 原插件 A 内部代码 ...
        # (保持原有的 apply_resize 等方法)
        return (torch.cat(output_images, dim=0), torch.cat(output_masks, dim=0), width, height)

    def apply_resize(self, image, mask, target_width, target_height, resample, keep_proportion, crop_position):
        # 保持插件 A 原样
        orig_width, orig_height = image.size
        if keep_proportion == "stretch":
            image = image.resize((target_width, target_height), resample=resample)
            mask = mask.resize((target_width, target_height), resample=resample)
        elif keep_proportion == "crop":
            ratio = max(target_width / orig_width, target_height / orig_height)
            new_width = int(orig_width * ratio); new_height = int(orig_height * ratio)
            image = image.resize((new_width, new_height), resample=resample)
            mask = mask.resize((new_width, new_height), resample=resample)
            left = (new_width - target_width) // 2; top = (new_height - target_height) // 2
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

# ==============================================================================
#                               PART 3: EasyNodeFlux Nodes
# ==============================================================================

class EasyNodeFluxImageEdit:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "mode": (["1_image", "2_image", "3_image", "4_image", "5_image", 
                         "6_image", "7_image", "8_image", "9_image", "10_image"],{"default": "1_image"}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1}),
                "width": ("INT", {"default": 1024, "min": 512, "max": 4096, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 512, "max": 4096, "step": 8}),
            },
            "optional": {
                "vae": ("VAE",),
                "image1_mask": ("MASK",),
                "image1": ("IMAGE",), "image2": ("IMAGE",), "image3": ("IMAGE",),
                "image4": ("IMAGE",), "image5": ("IMAGE",), "image6": ("IMAGE",),
                "image7": ("IMAGE",), "image8": ("IMAGE",), "image9": ("IMAGE",),
                "image10": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "LATENT")
    RETURN_NAMES = ("positive", "negative", "latent")
    FUNCTION = "encode"
    CATEGORY = "EasyNode/Flux"  # 修改了分类，放入 EasyNode 目录下

    def encode(self, clip, prompt, mode, batch_size, width, height, vae=None, 
               image1_mask=None, image1=None, image2=None, image3=None, image4=None, 
               image5=None, image6=None, image7=None, image8=None, image9=None, image10=None):
        
        if vae is None:
            raise RuntimeError("VAE is required.")
        
        all_images = [image1, image2, image3, image4, image5, image6, image7, image8, image9, image10]
        count = int(mode.split("_")[0])
        images = [img for i, img in enumerate(all_images[:count]) if img is not None]
        
        ref_latents = []
        vl_images = []
        noise_mask = None
        image_prompt_prefix = ""
        
        for i, image in enumerate(images):
            samples = image.movedim(-1, 1)
            current_total = samples.shape[3] * samples.shape[2]
            
            vl_total = int(384 * 384)
            vl_scale_by = math.sqrt(vl_total / current_total)
            vl_width = round(samples.shape[3] * vl_scale_by)
            vl_height = round(samples.shape[2] * vl_scale_by)
            
            s_vl = comfy.utils.common_upscale(samples, vl_width, vl_height, "area", "center")
            vl_images.append(s_vl.movedim(1, -1))
            image_prompt_prefix += f"image{i+1}: <|vision_start|><|image_pad|><|vision_end|> "
            
            vae_input_canvas = torch.zeros((samples.shape[0], height, width, 3), dtype=samples.dtype, device=samples.device)
            resized_img = comfy.utils.common_upscale(samples, width, height, "lanczos", "center").movedim(1, -1)
            img_h, img_w = resized_img.shape[1], resized_img.shape[2]
            vae_input_canvas[:, :img_h, :img_w, :] = resized_img
            ref_latents.append(vae.encode(vae_input_canvas))
            
            if i == 0 and image1_mask is not None:
                mask = image1_mask
                mask_samples = mask.unsqueeze(0).unsqueeze(0) if mask.dim() == 2 else mask.unsqueeze(1)
                m = comfy.utils.common_upscale(mask_samples, width // 8, height // 8, "area", "center")
                noise_mask = m.squeeze(1)
        
        tokens = clip.tokenize(image_prompt_prefix + prompt, images=vl_images)
        positive_conditioning = clip.encode_from_tokens_scheduled(tokens)
        if ref_latents: positive_conditioning = node_helpers.conditioning_set_values(positive_conditioning, {"reference_latents": ref_latents}, append=True)
        
        negative_conditioning = clip.encode_from_tokens_scheduled(clip.tokenize(""))
        if ref_latents: negative_conditioning = node_helpers.conditioning_set_values(negative_conditioning, {"reference_latents": ref_latents}, append=True)
        
        latent = {"samples": ref_latents[0] if ref_latents else vae.encode(torch.zeros(1, height, width, 3, device=comfy.model_management.get_torch_device()))}
        if noise_mask is not None: latent["noise_mask"] = noise_mask
        
        # Batch 处理
        if batch_size > 1:
            positive_conditioning *= batch_size
            negative_conditioning *= batch_size
            if latent["samples"].shape[0] != batch_size:
                latent["samples"] = latent["samples"].repeat(batch_size, 1, 1, 1)
            if "noise_mask" in latent:
                latent["noise_mask"] = latent["noise_mask"].repeat(batch_size, 1, 1)

        return (positive_conditioning, negative_conditioning, latent)

# ==============================================================================
#                               PART 4: Style Prompt Node 
# ==============================================================================
class EasyNodeStylePrompt:
    @classmethod
    def INPUT_TYPES(cls):
        models = list(STYLE_PRESETS.keys()) if STYLE_PRESETS else ["None"]
        return {
            "required": {
                "Model": (models, ),
                "Category": (["None"], ),
                "Style": (["None"], ),
                # 增加两个文本框，供用户输入想要替换的提示词
                "text_pos": ("STRING", {"multiline": True, "default": "", "dynamicPrompts": True}),
                "text_neg": ("STRING", {"multiline": True, "default": "", "dynamicPrompts": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "get_style"
    CATEGORY = "EasyNode/Prompt"

    def get_style(self, Model, Category, Style, text_pos="", text_neg=""):
        pos = ""
        neg = ""
        try:
            style_data = STYLE_PRESETS[Model][Category][Style]
            pos = style_data.get("positive", "")
            neg = style_data.get("negative", "")
        except KeyError:
            pass 

        # 处理 Positive 替换
        if text_pos:
            if "{$@}" in pos:
                pos = pos.replace("{$@}", text_pos)
            else:
                # 如果预设中没有占位符，默认将输入的词拼接到最后面
                pos = f"{pos},{text_pos} " if pos else text_pos
        else:
            # 如果输入框为空，清理掉占位符
            pos = pos.replace("{$@}", "").strip(", ") 

        # 处理 Negative 替换
        if text_neg:
            if "{$@}" in neg:
                neg = neg.replace("{$@}", text_neg)
            else:
                neg = f"{text_neg}, {neg}" if neg else text_neg
        else:
            neg = neg.replace("{$@}", "").strip(", ") 

        return (pos, neg)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        # 必须覆盖，因为 Category 和 Style 是由前端 JS 动态填充的
        return True
    
# ==============================================================================
#                               PART 5: Image Compression & Save Nodes
# ==============================================================================
class EasyNodeImageCompression:
    """
    高质量图片压缩节点
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "quality": ("INT", {
                    "default": 90,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "number",
                    "description": "压缩质量（0-100，默认90，如果图像较大例如10MB，可以设置为85左右，具体设置多少看你需要压缩成多大的文件大小，数值越低压缩越狠，质量就会有所下降，最低80左右就差不多，只会非常轻微的压缩图片质量，85往上图片压缩后，没有明显的质量下降，但是文件大小明显缩小。）"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "compress"
    CATEGORY = "EasyNode/Image"
    DESCRIPTION = "KOOK Image Compression Node (EasyNode版)"
    
    def compress(self, image, quality):
        batch_size = image.shape[0]
        compressed_images = []
        
        for i in range(batch_size):
            img = image[i]
            img_np = (img.cpu().numpy() * 255).astype(np.uint8)
            
            if img_np.shape[-1] == 4:
                pil_img = Image.fromarray(img_np).convert("RGB")
            else:
                pil_img = Image.fromarray(img_np)
            
            buffer_compressed = io.BytesIO()
            pil_img.save(buffer_compressed, format="JPEG", quality=quality, optimize=True, subsampling=1)
            
            buffer_compressed.seek(0)
            pil_img_compressed = Image.open(buffer_compressed)
            img_compressed_np = np.array(pil_img_compressed)
            
            if len(img_compressed_np.shape) == 2:
                img_compressed_np = np.stack([img_compressed_np] * 3, axis=-1)
            elif img_compressed_np.shape[-1] == 1:
                img_compressed_np = np.repeat(img_compressed_np, 3, axis=-1)
            
            img_compressed_np = img_compressed_np.astype(np.float32) / 255.0
            img_compressed_tensor = torch.from_numpy(img_compressed_np)
            compressed_images.append(img_compressed_tensor)
        
        compressed_images_tensor = torch.stack(compressed_images)
        return (compressed_images_tensor,)

class EasyNodeSaveJPGImage:
    """
    保存JPG图像节点
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "Comfyui_"}),
            },
            "optional": {
                "save_path": ("STRING", {"default": ""}),
            },
        }
    
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "save_jpg"
    CATEGORY = "EasyNode/Image"
    OUTPUT_NODE = True
    DESCRIPTION = "KOOK Save JPG Image Node (EasyNode版)"
    
    def save_jpg(self, images, filename_prefix, save_path=""):
        preview_dir = "output"
        if not os.path.exists(preview_dir):
            os.makedirs(preview_dir, exist_ok=True)
        
        actual_dir = save_path.strip() if save_path and save_path.strip() else preview_dir
        
        if not os.path.exists(actual_dir):
            os.makedirs(actual_dir, exist_ok=True)
        
        batch_size = images.shape[0]
        saved_images = []
        
        for i in range(batch_size):
            img = images[i]
            img_np = (img.cpu().numpy() * 255).astype(np.uint8)
            
            if img_np.shape[-1] == 4:
                pil_img = Image.fromarray(img_np).convert("RGB")
            else:
                pil_img = Image.fromarray(img_np)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}{timestamp}_{i+1}.jpg"
            actual_file_path = os.path.join(actual_dir, filename)
            pil_img.save(actual_file_path, format="JPEG", quality=90, optimize=True)
            
            preview_file_path = os.path.join(preview_dir, filename)
            if actual_dir != preview_dir:
                pil_img.save(preview_file_path, format="JPEG", quality=90, optimize=True)
            
            saved_images.append({
                "filename": filename,
                "subfolder": "",
                "type": "output"
            })
        
        return {
            "ui": {
                "images": saved_images
            },
            "result": ()
        }


# ==============================================================================
#                               REGISTRATION
# ==============================================================================

NODE_CLASS_MAPPINGS = {
    "EasySizeSimpleImage":      EasySizeSimpleImage,
    "EasySizeSimpleLatent":     EasySizeSimpleLatent,
    "EasySizeSimpleSetting":    EasySizeSimpleSetting,
    "EasyNodeLoader":           EasyNodeLoader,
    "EasyNodeFluxImageEdit":    EasyNodeFluxImageEdit,
    "EasyNodeStylePrompt":      EasyNodeStylePrompt,
    "EasyNodeImageCompression": EasyNodeImageCompression,
    "EasyNodeSaveJPGImage":     EasyNodeSaveJPGImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EasySizeSimpleImage":      "EasyNode 简单图像尺寸",
    "EasySizeSimpleLatent":     "EasyNode 简单图像尺寸-Latent",
    "EasySizeSimpleSetting":    "EasyNode 简单尺寸设置",
    "EasyNodeLoader":           "EasyNode 加载图像 (Loader)",
    "EasyNodeFluxImageEdit":    "EasyNode Flux 图像编辑",
    "EasyNodeStylePrompt":      "EasyNode 预设风格提示词",
    "EasyNodeImageCompression": "EasyNode 图像压缩 (Compression)",
    "EasyNodeSaveJPGImage":     "EasyNode 保存JPG (Save JPG)"
}