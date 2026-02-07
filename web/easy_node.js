import { api } from "../../../scripts/api.js";
import { app } from "../../../scripts/app.js";

console.log("[EasyNode] Initializing JS V8 (Compact Mode & Hidden Mask)...");

async function canvasToBlob(canvas) {
    return new Promise((resolve) => {
        canvas.toBlob(resolve, "image/png");
    });
}

class ImageBrushWidget {
    constructor(name, node) {
        this.name = name;
        this.type = "custom";
        this.node = node;
        this.value = "";
        
        // Internal State
        this.brushSize = 80;
        this.brushOpacity = 0.5;
        this.isEraser = false;
        this.isDrawing = false;
        this.lastMousePos = null;
        this.history = [];
        this.canvasRect = { x: 0, y: 0, w: 0, h: 0 };
        this.activeSlider = null;
        
        this.img = new Image();
        this.drawingCanvas = document.createElement("canvas");
        this.drawingCtx = this.drawingCanvas.getContext("2d");
        
        // Layout Config
        this.toolbarHeight = 80;
        this.footerHeight = 25;
        this.margin = 10;
        this.topPadding = 20;
    }
    
    // [MODIFIED] Compact Size Calculation
    computeSize(width) {
        let currentWidth = width;
        if (!currentWidth || currentWidth < 100) {
            currentWidth = (this.widgetWidth > 100) ? this.widgetWidth : 450;
        }

        if (this.mode === "batch") {
            return [currentWidth, 0];
        }

        // Base height: Toolbar + Footer + Paddings
        let neededHeight = this.toolbarHeight + this.footerHeight + this.topPadding + (this.margin * 2);

        if (this.img && this.img.width && this.img.height) {
            // Calculate exact image height based on width
            const aspect = this.img.width / this.img.height;
            const drawWidth = currentWidth - this.margin * 2;
            const imgHeight = drawWidth / aspect;
            neededHeight += imgHeight;
        } else {
            // Minimum height for "NO IMAGE" placeholder
            neededHeight += 100;
        }
        
        return [currentWidth, neededHeight];
    }

    draw(ctx, node, widget_width, y, widget_height) {
        this.widgetWidth = widget_width;
        const modeWidget = node.widgets.find(w => w.name === "mode");
        this.mode = modeWidget ? modeWidget.value : "single";
        
        if (this.mode === "batch") return;
        
        this.widgetTopY = y; 
        
        // Ensure we fit within the allocated space, but layout logic drives the size now
        this.widgetHeight = widget_height;
        
        const topPadding = this.topPadding;
        
        ctx.save();
        ctx.fillStyle = "#222";
        ctx.fillRect(0, y, widget_width, this.widgetHeight);
        const drawWidth = widget_width - this.margin * 2;
        
        ctx.beginPath();
        const toolbarY = y + topPadding;
        
        // 1. Toolbar
        ctx.shadowColor = "rgba(0,0,0,0.5)";
        ctx.shadowBlur = 10;
        ctx.fillStyle = "#181818";
        ctx.roundRect(this.margin, toolbarY, drawWidth, this.toolbarHeight, 4);
        ctx.fill();
        ctx.shadowColor = "transparent";
        ctx.shadowBlur = 0;

        // Buttons
        const btns = [{ label: "Load", id: "load" }, { label: "Clear", id: "clear" }, { label: "Undo", id: "undo" }, { label: "Eraser", id: "eraser" }, { label: "Brush", id: "brush" }];
        const btnW = (drawWidth - 10) / btns.length;
        const btnH = 24;
        const btnY = toolbarY + 6;

        btns.forEach((btn, i) => {
            const bx = this.margin + 5 + i * btnW;
            const isSelected = (btn.id === "brush" && !this.isEraser) || (btn.id === "eraser" && this.isEraser);
            ctx.fillStyle = isSelected ? "#4a90e2" : "#333";
            ctx.beginPath();
            ctx.roundRect(bx + 2, btnY, btnW - 4, btnH, 3);
            ctx.fill();
            ctx.fillStyle = "#fff";
            ctx.font = "bold 10px Arial";
            ctx.textAlign = "center";
            ctx.fillText(btn.label, bx + btnW / 2, btnY + 16);
        });

        // Sliders
        const sliderY = btnY + 34;
        const sliderW = (drawWidth - 30) / 2;
        
        ctx.fillStyle = "#aaa";
        ctx.font = "10px Arial";
        ctx.textAlign = "left";
        ctx.fillText(`Size: ${this.brushSize}`, this.margin + 5, sliderY + 12);
        const sBarX = this.margin + 50;
        const sBarW = sliderW - 50;
        ctx.fillStyle = "#222";
        ctx.fillRect(sBarX, sliderY + 6, sBarW, 6);
        ctx.fillStyle = "#4a90e2";
        ctx.fillRect(sBarX, sliderY + 6, (this.brushSize / 200) * sBarW, 6);

        ctx.fillStyle = "#aaa";
        ctx.fillText(`Alpha: ${Math.round(this.brushOpacity * 100)}%`, this.margin + sliderW + 15, sliderY + 12);
        const oBarX = this.margin + sliderW + 75;
        const oBarW = sliderW - 75;
        ctx.fillStyle = "#222";
        ctx.fillRect(oBarX, sliderY + 6, oBarW, 6);
        ctx.fillStyle = "#4a90e2";
        ctx.fillRect(oBarX, sliderY + 6, this.brushOpacity * oBarW, 6);

        const relSliderY = sliderY - y;
        this.sliderRects = {
            size: { x: this.margin, y: relSliderY, w: sliderW, h: 20, barX: sBarX, barW: sBarW },
            alpha: { x: this.margin + sliderW + 10, y: relSliderY, w: sliderW, h: 20, barX: oBarX, barW: oBarW }
        };

        // 2. Image Area
        const imgY = toolbarY + this.toolbarHeight + 5;
        
        // Calculate max available height for drawing to prevent overflow
        // But since we resized the node to fit, we should just use what we need.
        const drawHeight = this.widgetHeight - (imgY - y) - this.footerHeight;

        if (this.img.complete && this.img.src && this.img.naturalWidth > 0) {
            const aspect = this.img.width / this.img.height;
            let dw = drawWidth;
            let dh = drawWidth / aspect;
            
            const dx = this.margin + (drawWidth - dw) / 2;
            const dy = imgY;
            this.canvasRect = { x: dx, y: dy, w: dw, h: dh };

            ctx.shadowColor = "rgba(0,0,0,0.5)";
            ctx.shadowBlur = 10;
            ctx.fillStyle = "#000";
            ctx.fillRect(dx, dy, dw, dh);
            ctx.shadowColor = "transparent";
            ctx.shadowBlur = 0;
            ctx.drawImage(this.img, dx, dy, dw, dh);
            
            ctx.globalAlpha = this.brushOpacity;
            const tempCanvas = document.createElement("canvas");
            tempCanvas.width = this.drawingCanvas.width;
            tempCanvas.height = this.drawingCanvas.height;
            const tempCtx = tempCanvas.getContext("2d");
            tempCtx.drawImage(this.drawingCanvas, 0, 0);
            tempCtx.globalCompositeOperation = "source-in";
            tempCtx.fillStyle = "red";
            tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
            ctx.drawImage(tempCanvas, dx, dy, dw, dh);
            ctx.globalAlpha = 1.0;
            
            ctx.strokeStyle = "#444";
            ctx.strokeRect(dx, dy, dw, dh);
            ctx.fillStyle = "#888";
            ctx.font = "10px monospace";
            ctx.textAlign = "center";
            ctx.fillText(`${this.img.width} × ${this.img.height}PX`, widget_width / 2, dy + dh + 15);
        } else {
            // Draw placeholder
            ctx.fillStyle = "#111";
            ctx.fillRect(this.margin, imgY, drawWidth, Math.max(50, drawHeight));
            ctx.fillStyle = "#444";
            ctx.textAlign = "center";
            ctx.fillText("NO IMAGE LOADED", widget_width / 2, imgY + Math.max(50, drawHeight) / 2);
        }
        ctx.restore();
    }

    updateSliderValue(sliderType, x) {
        if (!this.sliderRects) return;
        const rect = this.sliderRects[sliderType];
        if (!rect) return;
        const ratio = Math.max(0, Math.min(1, (x - rect.barX) / rect.barW));
        if (sliderType === 'size') this.brushSize = Math.max(1, Math.min(200, Math.round(ratio * 200)));
        else if (sliderType === 'alpha') this.brushOpacity = Math.max(0.1, Math.min(1.0, ratio));
        this.node.setDirtyCanvas(true, true);
    }

    mouse(event, pos, node) {
        if (this.mode === "batch") return false;
        const [x, y] = pos;
        if (this.widgetTopY === undefined) return false;
        
        const localY = y - this.widgetTopY; 
        const topPadding = 20;
        
        if (localY < this.toolbarHeight + topPadding + 20) { 
            if (event.type === "pointerdown" || event.type === "mousedown") {
                const drawWidth = (this.widgetWidth || node.size[0]) - this.margin * 2;
                const btnW = (drawWidth - 10) / 5;
                const btnY = 6 + topPadding;
                const btnX0 = this.margin + 5;
                
                // Buttons
                if (localY >= btnY && localY <= btnY + 24 && x >= btnX0 && x <= btnX0 + btnW * 5) {
                    const idx = Math.floor((x - btnX0) / btnW);
                    if (idx === 0) this.uploadImage();
                    else if (idx === 1) this.clear();
                    else if (idx === 2) this.undo();
                    else if (idx === 3) this.isEraser = true;
                    else if (idx === 4) this.isEraser = false;
                    node.setDirtyCanvas(true, true);
                    return true;
                }
                
                // Sliders
                if (this.sliderRects) {
                    const sr = this.sliderRects.size;
                    if (localY >= sr.y - 10 && localY <= sr.y + sr.h + 10 && x < node.size[0] / 2) {
                        this.activeSlider = 'size';
                        this.updateSliderValue('size', x);
                        return true;
                    }
                    const ar = this.sliderRects.alpha;
                    if (localY >= ar.y - 10 && localY <= ar.y + ar.h + 10 && x >= node.size[0] / 2) {
                        this.activeSlider = 'alpha';
                        this.updateSliderValue('alpha', x);
                        return true;
                    }
                }
            } else if (event.type === "pointermove" || event.type === "mousemove") {
                if (this.activeSlider) { this.updateSliderValue(this.activeSlider, x); return true; }
            } else if (event.type === "pointerup" || event.type === "mouseup") {
                if (this.activeSlider) { this.activeSlider = null; return true; }
            }
        }

        if (this.activeSlider) return false; 
        
        // Canvas Drawing
        if (this.canvasRect && this.img.src) {
            const { x: rx, y: ry, w: rw, h: rh } = this.canvasRect;
            const scaleX = this.drawingCanvas.width / rw;
            const scaleY = this.drawingCanvas.height / rh;
            const imgX = (x - rx) * scaleX;
            const imgY = (y - ry) * scaleY;

            if (event.type === "pointerdown" || event.type === "mousedown") {
                if (x >= rx && x <= rx + rw && y >= ry && y <= ry + rh) {
                    this.isDrawing = true; this.saveHistory(); this.drawAt(imgX, imgY); this.lastMousePos = [imgX, imgY]; return true;
                }
            } else if (event.type === "pointermove" || event.type === "mousemove") {
                if (this.isDrawing) { this.drawAt(imgX, imgY, this.lastMousePos); this.lastMousePos = [imgX, imgY]; node.setDirtyCanvas(true, true); return true; }
            } else if (event.type === "pointerup" || event.type === "mouseup") {
                if (this.isDrawing) { this.isDrawing = false; this.uploadMask(); node.setDirtyCanvas(true, true); return true; }
            }
        }
        return false;
    }

    drawAt(x, y, lastPos = null) {
        const ctx = this.drawingCtx;
        ctx.lineCap = "round"; ctx.lineJoin = "round"; ctx.lineWidth = this.brushSize;
        if (this.isEraser) ctx.globalCompositeOperation = "destination-out";
        else { ctx.globalCompositeOperation = "source-over"; ctx.strokeStyle = "white"; }
        ctx.beginPath();
        if (lastPos) ctx.moveTo(lastPos[0], lastPos[1]); else ctx.moveTo(x, y);
        ctx.lineTo(x, y); ctx.stroke();
    }

    saveHistory() {
        this.history.push(this.drawingCanvas.toDataURL());
        if (this.history.length > 20) this.history.shift();
    }

    undo() {
        if (this.history.length > 0) {
            const last = this.history.pop();
            const tempImg = new Image();
            tempImg.onload = () => {
                this.drawingCtx.globalCompositeOperation = "source-over";
                this.drawingCtx.clearRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);
                this.drawingCtx.drawImage(tempImg, 0, 0);
                this.node.setDirtyCanvas(true, true);
                this.uploadMask();
            };
            tempImg.src = last;
        }
    }

    clear() {
        this.saveHistory();
        this.drawingCtx.globalCompositeOperation = "source-over";
        this.drawingCtx.clearRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);
        this.node.setDirtyCanvas(true, true);
        this.uploadMask();
    }

    uploadImage() {
        const input = document.createElement("input");
        input.type = "file"; input.accept = "image/*";
        input.onchange = async () => {
            const file = input.files[0];
            if (!file) return;
            const body = new FormData(); body.append("image", file);
            const resp = await api.fetchApi("/upload/image", { method: "POST", body });
            const data = await resp.json();
            const imageWidget = this.node.widgets.find(w => w.name === "image");
            if (imageWidget) { imageWidget.value = data.name; this.onImageChanged(data.name, true); }
        };
        input.click();
    }

    onImageChanged(name, resetMask = false) {
        if (!name || name === "# NO IMAGES FOUND #") return;
        this.history = [];
        this.drawingCtx.clearRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);
        const maskWidget = this.node.widgets.find(w => w.name === "mask_data");
        if (resetMask) { if (maskWidget) maskWidget.value = ""; this.pendingMaskReset = true; } else { this.pendingMaskReset = false; }

        this.img.src = api.apiURL(`/view?filename=${encodeURIComponent(name)}&type=input&t=${Date.now()}`);
        this.img.onerror = () => { this.node.setDirtyCanvas(true, true); };
        this.img.onload = () => {
            this.drawingCanvas.width = this.img.width;
            this.drawingCanvas.height = this.img.height;
            if (!this.pendingMaskReset && maskWidget && maskWidget.value) { this.loadMask(maskWidget.value); }
            this.pendingMaskReset = false;
            
            // [MODIFIED] Snap height to content immediately after loading image
            if (this.node) {
                const currentWidth = this.node.size[0];
                const newSize = this.node.brushWidget.computeSize(currentWidth); 
                this.node.setSize(newSize);
            }
            this.node.setDirtyCanvas(true, true);
        };
    }

    loadMask(name) {
        const maskImg = new Image();
        maskImg.onload = () => {
            if (maskImg.naturalWidth > 0) {
                this.drawingCtx.globalCompositeOperation = "source-over";
                this.drawingCtx.clearRect(0, 0, this.drawingCanvas.width, this.drawingCanvas.height);
                this.drawingCtx.drawImage(maskImg, 0, 0);
                this.node.setDirtyCanvas(true, true);
            }
        };
        maskImg.src = api.apiURL(`/view?filename=${encodeURIComponent(name)}&type=input&t=${Date.now()}`);
    }

    async uploadMask() {
        if (!this.drawingCanvas.width) return;
        const blob = await canvasToBlob(this.drawingCanvas);
        const file = new File([blob], `mask_${Date.now()}.png`, { type: "image/png" });
        const body = new FormData(); 
        body.append("image", file);
        
        try {
            const resp = await api.fetchApi("/upload/image", { method: "POST", body });
            const data = await resp.json();
            
            // [MODIFIED] Force Hidden Widget
            const maskWidget = this.node.widgets.find(w => w.name === "mask_data");
            if (maskWidget) {
                 maskWidget.value = data.name;
            } else {
                 const w = this.node.addWidget("text", "mask_data", data.name, ()=>{}, { serialize: true });
                 // Strict Hiding Properties
                 w.type = "hidden";
                 w.computeSize = () => [0, -4];
                 w.draw = () => {}; 
                 if (w.inputEl) w.inputEl.style.display = "none";
            }

        } catch(e) {
            console.error("[EasyNode] Mask upload failed", e);
        }
    }
}

app.registerExtension({
    name: "Comfy.EasyNode",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "EasyNodeLoader") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        const onDrawBackground = nodeType.prototype.onDrawBackground;
        nodeType.prototype.onDrawBackground = function() {
            this.imgs = null; this.images = null;
            if (onDrawBackground) return onDrawBackground.apply(this, arguments);
        };
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function() {
            if (onExecuted) onExecuted.apply(this, arguments);
            this.imgs = null; this.images = null;
        };

        nodeType.prototype.onNodeCreated = function() {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            setTimeout(() => {
                const keep = ["mode", "image", "batch_path", "width", "height", "upscale_method", "keep_proportion", "crop_position", "divisible_by", "mask_data"];
                this.widgets = this.widgets.filter(w => keep.includes(w.name));
                const brushWidget = new ImageBrushWidget("painter", this);
                this.addCustomWidget(brushWidget);
                this.brushWidget = brushWidget;
                
                const modeWidget = this.widgets.find(w => w.name === "mode");
                const imageWidget = this.widgets.find(w => w.name === "image");
                const batchPathWidget = this.widgets.find(w => w.name === "batch_path");
                const imageWidgetType = imageWidget.type;
                const batchPathWidgetType = batchPathWidget.type;
                
                const updateVisibility = () => {
                    const isBatch = modeWidget.value === "batch";
                    brushWidget.mode = modeWidget.value; 
                    if (isBatch) { 
                        imageWidget.type = "hidden"; 
                        batchPathWidget.type = batchPathWidgetType; 
                    } else { 
                        imageWidget.type = imageWidgetType; 
                        batchPathWidget.type = "hidden"; 
                    }
                    
                    // [MODIFIED] Recalculate size immediately on visibility change
                    // Pass current width (this.size[0]) to preserve it
                    this.setSize(this.brushWidget.computeSize(this.size[0])); 
                    this.setDirtyCanvas(true, true);
                };

                if (modeWidget) {
                    modeWidget.callback = () => {
                        updateVisibility();
                    };
                }

                if (imageWidget) {
                    imageWidget.computeSize = () => [0, 26]; 
                    const originalCallback = imageWidget.callback;
                    imageWidget.callback = (v) => {
                        if (originalCallback) originalCallback.apply(imageWidget, [v]);
                        this.imgs = null; this.images = null;
                        brushWidget.onImageChanged(v, true);
                    };
                    if (imageWidget.value) {
                        this.imgs = null; this.images = null;
                        brushWidget.onImageChanged(imageWidget.value, false);
                    }
                }
                const maskWidget = this.widgets.find(w => w.name === "mask_data");
                if (maskWidget) { maskWidget.type = "hidden"; maskWidget.computeSize = () => [0, -4]; maskWidget.draw = () => {}; }
                
                updateVisibility();
                this.onResize?.(this.size);
                this.setDirtyCanvas(true, true);
            }, 100);
            return r;
        };
    }
});