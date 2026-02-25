import { api } from "../../../scripts/api.js";
import { app } from "../../../scripts/app.js";

console.log("[EasyNode] Initializing JS V17 (Unified Loader + Smart Flux Edit)...");

async function canvasToBlob(canvas) {
    return new Promise((resolve) => {
        canvas.toBlob(resolve, "image/png");
    });
}

// --- Custom Widget Class ---
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
        this.isFilling = false;
        this.isDrawing = false;
        this.lastMousePos = null;
        this.history = [];
        this.canvasRect = { x: 0, y: 0, w: 0, h: 0 };
        
        // Image & Canvas
        this.img = new Image();
        this.drawingCanvas = document.createElement("canvas");
        this.drawingCtx = this.drawingCanvas.getContext("2d", { willReadFrequently: true });
        
        // Toolbar Config
        this.toolbarHeight = 80;
        this.footerHeight = 25;
        this.margin = 10;
        this.topPadding = 20;
    }
    
    computeSize(width) {
        let currentWidth = width;
        if (!currentWidth || currentWidth < 100) {
            currentWidth = this.widgetWidth || 450;
        }
        if (this.mode === "batch") return [currentWidth, 0];
        let neededHeight = this.toolbarHeight + this.footerHeight + (this.margin * 2) + this.topPadding + 200;
        return [currentWidth, neededHeight];
    }

    draw(ctx, node, widget_width, y, widget_height) {
        const modeWidget = node.widgets.find(w => w.name === "mode");
        this.mode = modeWidget ? modeWidget.value : "single";
        if (this.mode === "batch") return;

        const topY = y;
        this.widgetTopY = topY;
        const availableHeight = node.size[1] - y - 10; 
        this.widgetHeight = Math.max(widget_height, availableHeight);
        this.widgetWidth = widget_width;
        const topPadding = this.topPadding;
        
        ctx.save();
        ctx.fillStyle = "#222";
        ctx.fillRect(0, topY, widget_width, this.widgetHeight);
        const drawWidth = widget_width - this.margin * 2;
        
        // 1. Toolbar
        const toolbarY = topY + topPadding;
        ctx.shadowColor = "rgba(0,0,0,0.5)";
        ctx.shadowBlur = 10;
        ctx.fillStyle = "#181818";
        ctx.roundRect(this.margin, toolbarY, drawWidth, this.toolbarHeight, 4);
        ctx.fill();
        ctx.shadowColor = "transparent";

        // 2. Buttons
        const btns = [
            { label: "Load", id: "load" }, { label: "Clear", id: "clear" },
            { label: "Undo", id: "undo" }, { label: "Eraser", id: "eraser" },
            { label: "Fill", id: "fill" }, { label: "Brush", id: "brush" }
        ];
        const btnW = (drawWidth - 10) / btns.length;
        const btnH = 24;
        const btnY = toolbarY + 6;

        btns.forEach((btn, i) => {
            const bx = this.margin + 5 + i * btnW;
            const isSelected = (btn.id === "brush" && !this.isEraser && !this.isFilling) || 
                               (btn.id === "eraser" && this.isEraser) ||
                               (btn.id === "fill" && this.isFilling);
            ctx.fillStyle = isSelected ? "#4a90e2" : "#333";
            ctx.beginPath();
            ctx.roundRect(bx + 2, btnY, btnW - 4, btnH, 3);
            ctx.fill();
            ctx.fillStyle = "#fff";
            ctx.font = "bold 10px Arial";
            ctx.textAlign = "center";
            ctx.fillText(btn.label, bx + btnW / 2, btnY + 16);
        });

        // 3. Sliders
        const sliderY = btnY + 34;
        const sliderW = (drawWidth - 30) / 2;
        ctx.fillStyle = "#aaa";
        ctx.font = "10px Arial";
        ctx.textAlign = "left";
        ctx.fillText(`Size: ${this.brushSize}`, this.margin + 5, sliderY + 12);
        const sBarX = this.margin + 50; const sBarW = sliderW - 50;
        ctx.fillStyle = "#222"; ctx.fillRect(sBarX, sliderY + 6, sBarW, 6);
        ctx.fillStyle = "#4a90e2"; ctx.fillRect(sBarX, sliderY + 6, (this.brushSize / 200) * sBarW, 6);

        ctx.fillStyle = "#aaa";
        ctx.fillText(`Alpha: ${Math.round(this.brushOpacity * 100)}%`, this.margin + sliderW + 15, sliderY + 12);
        const oBarX = this.margin + sliderW + 75; const oBarW = sliderW - 75;
        ctx.fillStyle = "#222"; ctx.fillRect(oBarX, sliderY + 6, oBarW, 6);
        ctx.fillStyle = "#4a90e2"; ctx.fillRect(oBarX, sliderY + 6, this.brushOpacity * oBarW, 6);

        this.sliderRects = {
            size: { x: this.margin, y: sliderY - topY, w: sliderW, h: 20, barX: sBarX, barW: sBarW },
            alpha: { x: this.margin + sliderW + 10, y: sliderY - topY, w: sliderW, h: 20, barX: oBarX, barW: oBarW }
        };

        // 4. Image Area
        const imgY = toolbarY + this.toolbarHeight + 5;
        const drawHeight = this.widgetHeight - (imgY - topY) - this.footerHeight;

        if (this.img.complete && this.img.src && this.img.naturalWidth > 0) {
            const aspect = this.img.width / this.img.height;
            let dw = drawWidth; let dh = drawWidth / aspect;
            if (dh > drawHeight) { dh = drawHeight; dw = dh * aspect; }
            const dx = this.margin + (drawWidth - dw) / 2; const dy = imgY; 
            this.canvasRect = { x: dx, y: dy, w: dw, h: dh };
            ctx.fillStyle = "#000"; ctx.fillRect(dx, dy, dw, dh);
            ctx.drawImage(this.img, dx, dy, dw, dh);
            ctx.globalAlpha = this.brushOpacity;
            const tempCanvas = document.createElement("canvas");
            tempCanvas.width = this.drawingCanvas.width; tempCanvas.height = this.drawingCanvas.height;
            const tempCtx = tempCanvas.getContext("2d");
            tempCtx.drawImage(this.drawingCanvas, 0, 0);
            tempCtx.globalCompositeOperation = "source-in"; tempCtx.fillStyle = "red";
            tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
            ctx.drawImage(tempCanvas, dx, dy, dw, dh);
            ctx.globalAlpha = 1.0;
            ctx.strokeStyle = "#444"; ctx.strokeRect(dx, dy, dw, dh);
            ctx.fillStyle = "#888"; ctx.font = "10px monospace"; ctx.textAlign = "center";
            ctx.fillText(`${this.img.width} × ${this.img.height}PX`, widget_width / 2, dy + dh + 15);
        } else {
            ctx.fillStyle = "#111"; ctx.fillRect(this.margin, imgY, drawWidth, drawHeight > 0 ? drawHeight : 100);
            ctx.fillStyle = "#444"; ctx.textAlign = "center";
            ctx.fillText("NO IMAGE LOADED", widget_width / 2, imgY + (drawHeight > 0 ? drawHeight : 100) / 2);
        }
        ctx.restore();
    }

    // --- 省略 mouse, drawAt, floodFill 等内部逻辑以保证长度，实际替换时请保留 ---
    updateSliderValue(type, mouseX) {
        const rect = this.sliderRects[type];
        const val = Math.max(0, Math.min(1, (mouseX - rect.barX) / rect.barW));
        if (type === 'size') this.brushSize = Math.round(val * 200);
        else this.brushOpacity = val;
        this.node.setDirtyCanvas(true, true);
    }
    mouse(event, pos, node) {
        const [x, y] = pos; if (this.widgetTopY === undefined) return false;
        const localY = y - this.widgetTopY;
        if (localY < this.toolbarHeight + this.topPadding + 20) {
            if (event.type === "pointerdown" || event.type === "mousedown") {
                const btnY = 6 + this.topPadding; const btnX0 = this.margin + 5;
                const drawWidth = (this.widgetWidth || node.size[0]) - this.margin * 2;
                const btnW = (drawWidth - 10) / 6;
                if (localY >= btnY && localY <= btnY + 24 && x >= btnX0 && x <= btnX0 + btnW * 6) {
                    const idx = Math.floor((x - btnX0) / btnW);
                    if (idx === 0) this.uploadImage();
                    else if (idx === 1) this.clear();
                    else if (idx === 2) this.undo();
                    else if (idx === 3) { this.isEraser = true; this.isFilling = false; }
                    else if (idx === 4) { this.isEraser = false; this.isFilling = true; }
                    else if (idx === 5) { this.isEraser = false; this.isFilling = false; }
                    node.setDirtyCanvas(true, true); return true;
                }
                if (this.sliderRects) {
                    const sliderY = btnY + 34;
                    if (localY >= sliderY && localY <= sliderY + 20) {
                        this.activeSlider = (x < node.size[0] / 2) ? 'size' : 'alpha';
                        this.updateSliderValue(this.activeSlider, x); return true;
                    }
                }
            } else if (event.type === "pointermove" || event.type === "mousemove") {
                if (this.activeSlider) { this.updateSliderValue(this.activeSlider, x); return true; }
            } else if (event.type === "pointerup" || event.type === "mouseup") {
                if (this.activeSlider) { this.activeSlider = null; return true; }
            }
        }
        if (this.canvasRect && this.img.src) {
            const { x: rx, y: ry, w: rw, h: rh } = this.canvasRect;
            const imgX = (x - rx) * (this.drawingCanvas.width / rw);
            const imgY = (y - ry) * (this.drawingCanvas.height / rh);
            if (event.type === "pointerdown" || event.type === "mousedown") {
                if (x >= rx && x <= rx + rw && y >= ry && y <= ry + rh) {
                    if (this.isFilling) { this.saveHistory(); this.floodFill(Math.round(imgX), Math.round(imgY)); this.uploadMask(); }
                    else { this.isDrawing = true; this.saveHistory(); this.drawAt(imgX, imgY); this.lastMousePos = [imgX, imgY]; }
                    node.setDirtyCanvas(true, true); return true;
                }
            } else if (event.type === "pointermove" || event.type === "mousemove") {
                if (this.isDrawing) { this.drawAt(imgX, imgY, this.lastMousePos); this.lastMousePos = [imgX, imgY]; node.setDirtyCanvas(true, true); return true; }
            } else if (event.type === "pointerup" || event.type === "mouseup") {
                if (this.isDrawing) { this.isDrawing = false; setTimeout(() => this.uploadMask(), 50); node.setDirtyCanvas(true, true); return true; }
            }
        }
        return false;
    }
    drawAt(x, y, lastPos = null) {
        const ctx = this.drawingCtx; ctx.save();
        ctx.lineCap = "round"; ctx.lineJoin = "round"; ctx.lineWidth = this.brushSize; ctx.strokeStyle = "white";
        ctx.globalCompositeOperation = this.isEraser ? "destination-out" : "source-over";
        ctx.beginPath(); if (lastPos) ctx.moveTo(lastPos[0], lastPos[1]); else ctx.moveTo(x, y);
        ctx.lineTo(x, y); ctx.stroke(); ctx.restore();
    }
    saveHistory() { this.history.push(this.drawingCanvas.toDataURL()); if (this.history.length > 20) this.history.shift(); }
    undo() {
        if (this.history.length > 0) {
            const img = new Image(); img.onload = () => { this.drawingCtx.clearRect(0,0,this.drawingCanvas.width,this.drawingCanvas.height); this.drawingCtx.drawImage(img,0,0); this.node.setDirtyCanvas(true,true); this.uploadMask(); };
            img.src = this.history.pop();
        }
    }
    clear() { this.saveHistory(); this.drawingCtx.clearRect(0,0,this.drawingCanvas.width,this.drawingCanvas.height); this.node.setDirtyCanvas(true,true); this.uploadMask(); }
    async uploadImage() {
        const input = document.createElement("input"); input.type = "file"; input.accept = "image/*";
        input.onchange = async () => {
            const body = new FormData(); body.append("image", input.files[0]);
            const resp = await api.fetchApi("/upload/image", { method: "POST", body });
            const data = await resp.json();
            const w = this.node.widgets.find(w => w.name === "image"); if (w) { w.value = data.name; this.onImageChanged(data.name, true); }
        }; input.click();
    }
    onImageChanged(name, resetMask = false) {
        if (!name) return; this.history = []; this.drawingCtx.clearRect(0,0,this.drawingCanvas.width,this.drawingCanvas.height);
        const mw = this.node.widgets.find(w => w.name === "mask_data");
        if (resetMask && mw) mw.value = "";
        this.img.src = api.apiURL(`/view?filename=${encodeURIComponent(name)}&type=input&t=${Date.now()}`);
        this.img.onload = () => { 
            this.drawingCanvas.width = this.img.width; this.drawingCanvas.height = this.img.height;
            if (!resetMask && mw && mw.value) this.loadMask(mw.value);
            this.node.setDirtyCanvas(true, true);
        };
    }
    loadMask(name) {
        const m = new Image(); m.onload = () => { this.drawingCtx.drawImage(m,0,0); this.node.setDirtyCanvas(true,true); };
        m.src = api.apiURL(`/view?filename=${encodeURIComponent(name)}&type=temp&t=${Date.now()}`);
    }
    async uploadMask() {
        const blob = await canvasToBlob(this.drawingCanvas);
        const body = new FormData(); body.append("image", new File([blob], `mask.png`)); body.append("type", "temp");
        const resp = await api.fetchApi("/upload/image", { method: "POST", body });
        const data = await resp.json();
        const mw = this.node.widgets.find(w => w.name === "mask_data");
        if (mw) { mw.value = data.name; if (mw.callback) mw.callback(data.name); }
    }
    floodFill(_x,_y){/*...保持原代码填充逻辑...*/}
}

// --- Main Extension Registration ---
app.registerExtension({
    name: "Comfy.EasyNode",
    async beforeRegisterNodeDef(nodeType, nodeData, _app) {
        
        // --- EasyNodeLoader (笔刷涂鸦) ---
        if (nodeData.name === "EasyNodeLoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
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

                    const updateVisibility = () => {
                        const isBatch = modeWidget.value === "batch";
                        brushWidget.mode = modeWidget.value; 
                        imageWidget.type = isBatch ? "hidden" : "image";
                        batchPathWidget.type = isBatch ? "string" : "hidden";
                        this.setSize([this.size[0], this.computeSize([this.size[0], 0])[1]]);
                        this.setDirtyCanvas(true, true);
                    };
                    if (modeWidget) modeWidget.callback = updateVisibility;
                    if (imageWidget) {
                        imageWidget.callback = (v) => { brushWidget.onImageChanged(v, true); };
                        if (imageWidget.value) brushWidget.onImageChanged(imageWidget.value, false);
                    }
                    updateVisibility();
                }, 100);
                return r;
            };
        }

        // --- EasyNodeFluxImageEdit  ---
        if (nodeData.name === "EasyNodeFluxImageEdit") {
            
            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function(type, index, connected, _link_info) {
                if (onConnectionsChange) onConnectionsChange.apply(this, arguments);

                // 只处理输入端的连接变化
                if (type === 1) {
                    const modeWidget = this.widgets.find(w => w.name === "mode");
                    if (!modeWidget) return;

                    if (connected) {
                        // 【添加连接】逻辑：自动切换到新连入的最高索引
                        const input = this.inputs[index];
                        if (input.name.startsWith("image") && !input.name.includes("mask")) {
                            const num = parseInt(input.name.replace("image", ""));
                            const currentMax = parseInt(modeWidget.value.split("_")[0]);
                            if (num > currentMax) {
                                modeWidget.value = `${num}_image`;
                                if (modeWidget.callback) modeWidget.callback(modeWidget.value);
                            }
                        }
                    } else {
                        // 【移除连接】逻辑：自动寻找当前仍保持连接的最大索引
                        let maxIndex = 1;
                        this.inputs.forEach(input => {
                            if (input.name.startsWith("image") && !input.name.includes("mask") && input.link !== null) {
                                const num = parseInt(input.name.replace("image", ""));
                                if (num > maxIndex) maxIndex = num;
                            }
                        });
                        
                        const targetMode = `${maxIndex}_image`;
                        if (modeWidget.value !== targetMode) {
                            modeWidget.value = targetMode;
                            if (modeWidget.callback) modeWidget.callback(modeWidget.value);
                        }
                    }
                }
            };

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                setTimeout(() => {
                    const modeWidget = this.widgets.find(w => w.name === "mode");
                    const updateFluxInputs = () => {
                        if (!this.inputs) return;
                        const count = parseInt(modeWidget.value.split("_")[0]);
                        let changed = false;
                        this.inputs.forEach(input => {
                            if (input.name.startsWith("image")) {
                                const num = parseInt(input.name.replace("image", "").replace("_mask", ""));
                                const hide = num > count;
                                if (input.hidden !== hide) { input.hidden = hide; changed = true; }
                            }
                        });
                        if (changed) {
                            this.setDirtyCanvas(true, true);
                            const size = this.computeSize();
                            this.setSize([this.size[0], size[1]]);
                        }
                    };
                    if (modeWidget) modeWidget.callback = updateFluxInputs;
                    updateFluxInputs();
                }, 100);
                return r;
            };
        }
        // --- EasyNodeStylePrompt (新增：风格提示词三级联动) ---
        if (nodeData.name === "EasyNodeStylePrompt") {
          const onNodeCreated = nodeType.prototype.onNodeCreated;
          nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated
              ? onNodeCreated.apply(this, arguments)
              : undefined;

            // 获取该节点上的下拉框 Widget
            const modelWidget = this.widgets.find((w) => w.name === "Model");
            const categoryWidget = this.widgets.find(
              (w) => w.name === "Category",
            );
            const styleWidget = this.widgets.find((w) => w.name === "Style");

            if (!modelWidget || !categoryWidget || !styleWidget) return r;

            // 异步请求我们在后端 nodes.py 建立的内部 API 获取字典数据
            api
              .fetchApi("/easynode/get_styles")
              .then((res) => res.json())
              .then((presets) => {
                // 当 Model 改变时，更新 Category 下拉列表
                const updateCategories = () => {
                  const model = modelWidget.value;
                  const categories = presets[model]
                    ? Object.keys(presets[model])
                    : ["None"];

                  categoryWidget.options.values = categories;
                  // 如果当前的分类不再新列表里，默认选中第一个
                  if (!categories.includes(categoryWidget.value)) {
                    categoryWidget.value = categories[0] || "None";
                  }
                  updateStyles(); // 联动触发更新第三级 Style
                };

                // 当 Category 改变时，更新 Style 下拉列表
                const updateStyles = () => {
                  const model = modelWidget.value;
                  const category = categoryWidget.value;
                  const styles =
                    presets[model] && presets[model][category]
                      ? Object.keys(presets[model][category])
                      : ["None"];

                  styleWidget.options.values = styles;
                  if (!styles.includes(styleWidget.value)) {
                    styleWidget.value = styles[0] || "None";
                  }
                  // 强制 ComfyUI 刷新界面显示
                  app.graph.setDirtyCanvas(true, true);
                };

                // 绑定事件回调
                modelWidget.callback = updateCategories;
                categoryWidget.callback = updateStyles;

                // 首次加载初始化数据
                const models = Object.keys(presets);
                modelWidget.options.values =
                  models.length > 0 ? models : ["None"];
                if (!models.includes(modelWidget.value)) {
                  modelWidget.value = models[0] || "None";
                }
                updateCategories();
              });

            return r;
          };
        }
    }
});